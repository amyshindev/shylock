#Requires -Version 5.1

$ErrorActionPreference = "Continue"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"

$BackendPort = 8000
$FrontendPort = 3000

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Stop-UvicornWorkers {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -match 'uvicorn|multiprocessing\.spawn|main:app'
        } |
        ForEach-Object {
            Write-Host "  stop uvicorn worker PID $($_.ProcessId)" -ForegroundColor Yellow
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
}

function Get-ListenerProcessIds {
    param([int]$Port)

    $pids = @(
        Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess -Unique
    ) | Where-Object { $_ -and $_ -ne 0 }

    if ($pids) {
        return $pids
    }

    # Fallback when Get-NetTCPConnection misses duplicate listeners.
    $lines = netstat -ano | Select-String ":$Port\s" | Select-String "LISTENING"
    return @(
        $lines | ForEach-Object {
            if ($_ -match '\s(\d+)\s*$') { [int]$Matches[1] }
        } | Select-Object -Unique
    ) | Where-Object { $_ -and $_ -ne 0 }
}

function Stop-ListenersOnPort {
    param([int]$Port)

    $pids = Get-ListenerProcessIds -Port $Port
    if (-not $pids) {
        Write-Host "  port $Port : idle" -ForegroundColor DarkGray
        return
    }

    foreach ($procId in $pids) {
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if (-not $proc) {
            Write-Host "  port $Port : stale PID $procId (already exited)" -ForegroundColor DarkGray
            continue
        }
        try {
            Write-Host "  port $Port : stop PID $procId ($($proc.ProcessName))" -ForegroundColor Yellow
            Stop-Process -Id $procId -Force -ErrorAction Stop
        }
        catch {
            Write-Host "  port $Port : failed to stop PID $procId - $_" -ForegroundColor Red
        }
    }
}

function Wait-PortsFree {
    param(
        [int[]]$Ports,
        [int]$TimeoutSec = 15
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        $busy = @()
        foreach ($port in $Ports) {
            $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
            if ($listener) {
                $busy += $port
            }
        }
        if (-not $busy) {
            return $true
        }
        Start-Sleep -Milliseconds 400
    }
    return $false
}

function Stop-DockerDevServices {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "  docker not installed, skip" -ForegroundColor DarkGray
        return
    }

    $composeFile = Join-Path $Root "docker-compose.yaml"
    if (-not (Test-Path $composeFile)) {
        return
    }

    Push-Location $Root
    try {
        Write-Host "  stopping docker compose frontend/backend..." -ForegroundColor Yellow
        & docker compose stop frontend backend 2>$null | Out-Null
        Start-Sleep -Seconds 2
    }
    finally {
        Pop-Location
    }
}

function Resolve-BackendPython {
    $venvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        return $venvPython
    }

    $rootVenvPython = Join-Path $Root ".venv\Scripts\python.exe"
    if (Test-Path $rootVenvPython) {
        return $rootVenvPython
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return $python.Source
    }

    throw "Python not found. Install Python 3.12+ and run dev.bat again."
}

function Ensure-BackendVenv {
    param([string]$PythonExe)

    $venvDir = Join-Path $BackendDir ".venv"
    $venvPython = Join-Path $venvDir "Scripts\python.exe"
    $requirements = Join-Path $Root "requirements.txt"
    $stampFile = Join-Path $venvDir ".requirements-installed"

    if (-not (Test-Path $venvPython)) {
        Write-Host "  creating backend/.venv ..." -ForegroundColor Yellow
        & $PythonExe -m venv $venvDir
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create backend/.venv"
        }
        Remove-Item $stampFile -ErrorAction SilentlyContinue
    }

    if (-not (Test-Path $stampFile) -or (Get-Item $requirements).LastWriteTime -gt (Get-Item $stampFile).LastWriteTime) {
        Write-Host "  installing backend dependencies (first run may take a minute)..." -ForegroundColor Yellow
        & $venvPython -m pip install -q -r $requirements
        if ($LASTEXITCODE -ne 0) {
            throw "pip install failed. Check requirements.txt and your network."
        }
        New-Item -ItemType File -Path $stampFile -Force | Out-Null
    }

    return $venvPython
}

function Test-CommandExists {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

Write-Host ""
Write-Host "Shylock dev restart" -ForegroundColor Green
Write-Host "Root: $Root"

if (-not (Test-Path $BackendDir)) {
    throw "backend folder not found: $BackendDir"
}
if (-not (Test-Path $FrontendDir)) {
    throw "frontend folder not found: $FrontendDir"
}
if (-not (Test-CommandExists "npm")) {
    throw "npm not found. Install Node.js first."
}

Write-Step "Stop docker dev containers (ports $FrontendPort, $BackendPort)"
Stop-DockerDevServices

Write-Step "Kill processes on ports $FrontendPort, $BackendPort"
for ($attempt = 1; $attempt -le 3; $attempt++) {
    Stop-ListenersOnPort -Port $FrontendPort
    Stop-ListenersOnPort -Port $BackendPort
    Stop-UvicornWorkers
    if (Wait-PortsFree -Ports @($FrontendPort, $BackendPort) -TimeoutSec 5) {
        break
    }
    if ($attempt -lt 3) {
        Write-Host "  retry $attempt/3..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 1
    }
}

Write-Step "Wait for ports"
$portsFree = Wait-PortsFree -Ports @($FrontendPort, $BackendPort) -TimeoutSec 10
if (-not $portsFree) {
    Write-Host "Warning: ports may still be in use." -ForegroundColor Red
}
else {
    Write-Host "  ports $FrontendPort and $BackendPort are free" -ForegroundColor Green
}

$pythonExe = Resolve-BackendPython
Write-Host "  system python: $pythonExe" -ForegroundColor DarkGray

Write-Step "Prepare backend venv"
$pythonExe = Ensure-BackendVenv -PythonExe $pythonExe
Write-Host "  backend python: $pythonExe" -ForegroundColor Green

$backendCommand = @"
`$ErrorActionPreference = 'Continue'
`$env:PYTHONPATH = '$BackendDir\apps;$BackendDir'
Set-Location '$BackendDir'
Write-Host 'Backend: http://127.0.0.1:$BackendPort' -ForegroundColor Green
Write-Host 'Python  : $pythonExe' -ForegroundColor DarkGray
& '$pythonExe' -m uvicorn main:app --reload --host 127.0.0.1 --port $BackendPort
if (`$LASTEXITCODE -ne 0) {
  Write-Host ''
  Write-Host 'Backend failed to start. See error above.' -ForegroundColor Red
}
Write-Host ''
Write-Host 'Press Enter to close this window.' -ForegroundColor Yellow
Read-Host | Out-Null
"@

$frontendCommand = @"
Set-Location '$FrontendDir'
Write-Host 'Frontend: http://localhost:$FrontendPort' -ForegroundColor Green
npm run dev -- --port $FrontendPort
"@

Write-Step "Start backend (new window)"
Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-Command", $backendCommand
) -WorkingDirectory $BackendDir | Out-Null

Start-Sleep -Seconds 1

Write-Step "Start frontend (new window)"
Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-Command", $frontendCommand
) -WorkingDirectory $FrontendDir | Out-Null

Write-Step "Done"
Write-Host "  Frontend : http://localhost:$FrontendPort"
Write-Host "  Backend  : http://127.0.0.1:$BackendPort"
Write-Host ""
Write-Host "Servers run in separate PowerShell windows. Run dev.bat again to restart." -ForegroundColor DarkGray
Write-Host ""
