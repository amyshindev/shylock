#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"
BACKEND_PORT=8000
FRONTEND_PORT=3000

BACKEND_PID=""

step() {
  echo ""
  echo "==> $1"
}

cleanup() {
  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo ""
    echo "Stopping backend (PID $BACKEND_PID)..."
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

get_listener_pids() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -ti ":$port" -sTCP:LISTEN 2>/dev/null || true
    return
  fi
  if command -v fuser >/dev/null 2>&1; then
    fuser "${port}/tcp" 2>/dev/null | tr ' ' '\n' | grep -E '^[0-9]+$' || true
    return
  fi
  ss -ltnp "sport = :$port" 2>/dev/null | grep -oP 'pid=\K[0-9]+' || true
}

stop_port() {
  local port="$1"
  local pids
  pids="$(get_listener_pids "$port" | sort -u)"
  if [[ -z "$pids" ]]; then
    echo "  port $port : idle"
    return
  fi
  while IFS= read -r pid; do
    [[ -z "$pid" ]] && continue
    echo "  port $port : stop PID $pid"
    kill "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true
  done <<< "$pids"
}

wait_ports_free() {
  local ports=("$@")
  local deadline=$((SECONDS + 15))
  while (( SECONDS < deadline )); do
    local busy=0
    for port in "${ports[@]}"; do
      if [[ -n "$(get_listener_pids "$port")" ]]; then
        busy=1
        break
      fi
    done
    if (( busy == 0 )); then
      return 0
    fi
    sleep 0.4
  done
  return 1
}

stop_docker_dev_services() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "  docker not installed, skip"
    return
  fi
  if [[ ! -f "$ROOT/docker-compose.yaml" ]]; then
    return
  fi
  echo "  stopping docker compose frontend/backend..."
  (cd "$ROOT" && docker compose stop frontend backend 2>/dev/null) || true
  sleep 2
}

resolve_python() {
  local venv_python="$BACKEND_DIR/.venv/bin/python"
  if [[ -x "$venv_python" ]]; then
    echo "$venv_python"
    return
  fi
  local root_venv_python="$ROOT/.venv/bin/python"
  if [[ -x "$root_venv_python" ]]; then
    echo "$root_venv_python"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi
  echo "Python not found. Install Python 3.12+ and run ./dev.sh again." >&2
  exit 1
}

ensure_backend_venv() {
  local python_exe="$1"
  local venv_dir="$BACKEND_DIR/.venv"
  local venv_python="$venv_dir/bin/python"
  local requirements="$ROOT/requirements.txt"
  local stamp_file="$venv_dir/.requirements-installed"

  if [[ ! -x "$venv_python" ]]; then
    echo "  creating backend/.venv ..." >&2
    "$python_exe" -m venv "$venv_dir"
    rm -f "$stamp_file"
  fi

  if [[ ! -f "$stamp_file" ]] || [[ "$requirements" -nt "$stamp_file" ]]; then
    echo "  installing backend dependencies (first run may take a minute)..." >&2
    "$venv_python" -m pip install -q -r "$requirements"
    touch "$stamp_file"
  fi

  echo "$venv_python"
}

ensure_frontend_deps() {
  local next_bin="$FRONTEND_DIR/node_modules/.bin/next"
  local stamp_file="$FRONTEND_DIR/node_modules/.install-complete"
  local lock_file="$FRONTEND_DIR/package-lock.json"

  if [[ -x "$next_bin" ]] && [[ -f "$stamp_file" ]]; then
    if [[ ! -f "$lock_file" ]] || [[ "$stamp_file" -nt "$lock_file" ]]; then
      return 0
    fi
  fi

  echo "  installing frontend dependencies (first run may take a minute)..." >&2
  (cd "$FRONTEND_DIR" && npm install)
  touch "$stamp_file"
}

echo ""
echo "Shylock dev restart"
echo "Root: $ROOT"

[[ -d "$BACKEND_DIR" ]] || { echo "backend folder not found: $BACKEND_DIR" >&2; exit 1; }
[[ -d "$FRONTEND_DIR" ]] || { echo "frontend folder not found: $FRONTEND_DIR" >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm not found. Install Node.js first." >&2; exit 1; }

step "Stop docker dev containers (ports $FRONTEND_PORT, $BACKEND_PORT)"
stop_docker_dev_services

step "Kill processes on ports $FRONTEND_PORT, $BACKEND_PORT"
for attempt in 1 2 3; do
  stop_port "$FRONTEND_PORT"
  stop_port "$BACKEND_PORT"
  if wait_ports_free "$FRONTEND_PORT" "$BACKEND_PORT"; then
    break
  fi
  if (( attempt < 3 )); then
    echo "  retry $attempt/3..."
    sleep 1
  fi
done

step "Wait for ports"
if wait_ports_free "$FRONTEND_PORT" "$BACKEND_PORT"; then
  echo "  ports $FRONTEND_PORT and $BACKEND_PORT are free"
else
  echo "Warning: ports may still be in use." >&2
fi

system_python="$(resolve_python)"
echo "  system python: $system_python"

step "Prepare backend venv"
backend_python="$(ensure_backend_venv "$system_python")"
echo "  backend python: $backend_python"

step "Start backend (background)"
export PYTHONPATH="$BACKEND_DIR/apps:$BACKEND_DIR"
(
  cd "$BACKEND_DIR"
  echo "Backend: http://127.0.0.1:$BACKEND_PORT"
  exec "$backend_python" -m uvicorn main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT"
) &
BACKEND_PID=$!

sleep 2
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
  echo "Backend failed to start. See error above." >&2
  exit 1
fi

step "Prepare frontend dependencies"
ensure_frontend_deps

step "Start frontend (foreground)"
echo "  Frontend : http://localhost:$FRONTEND_PORT"
echo "  Backend  : http://localhost:$BACKEND_PORT"
echo ""
echo "Press Ctrl+C to stop both servers."
cd "$FRONTEND_DIR"
npm run dev -- --hostname 0.0.0.0 --port "$FRONTEND_PORT"
