param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

Push-Location $projectRoot
try {
    if (-not (Test-Path $venvPython)) {
        py -m venv .venv
    }

    & $venvPython -m pip install -r .\wku_backend_requirements.txt
    & $venvPython -m flask --app run.py init-db

    $env:WKU_HOST = $Host
    $env:WKU_PORT = "$Port"
    $env:WKU_DEBUG = "1"

    & $venvPython run.py
}
finally {
    Pop-Location
}
