#!/usr/bin/env bash
# Diagnose / free Docker disk when builds fail with: [Errno 28] No space left on device
set -euo pipefail

echo "=== Host disk (C: and WSL root) ==="
df -h / /mnt/c 2>/dev/null || df -h /

echo ""
echo "=== Inodes on / ==="
df -i /

echo ""
echo "=== Docker disk usage (this can be full while C: is only 31%) ==="
docker system df -v 2>/dev/null || docker system df 2>/dev/null || true

echo ""
echo "=== WSL virtual disk file (may hit its size cap before C: fills) ==="
ls -lh /mnt/c/Users/*/AppData/Local/Packages/CanonicalGroupLimited*/LocalState/ext4.vhdx 2>/dev/null || true
ls -lh /mnt/c/Users/*/AppData/Local/Docker/wsl/disk/*.vhdx 2>/dev/null || true

echo ""
read -r -p "Prune unused Docker images/containers/build cache? [y/N] " ans
if [[ "${ans,,}" == "y" ]]; then
  docker builder prune -af 2>/dev/null || true
  docker system prune -af 2>/dev/null || true
  echo ""
  echo "=== Docker usage after prune ==="
  docker system df 2>/dev/null || true
fi

echo ""
echo "Rebuild:"
echo "  DOCKER_BUILDKIT=1 docker compose build backend"
