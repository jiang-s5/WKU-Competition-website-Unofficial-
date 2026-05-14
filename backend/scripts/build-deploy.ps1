param(
    [string]$OutputPath = "F:\backend-deploy.zip"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $projectRoot
try {
    if (Test-Path $OutputPath) {
        Remove-Item -LiteralPath $OutputPath -Force
    }

    $items = @(
        ".env.example",
        ".gitignore",
        "app",
        "run.py",
        "serve.py",
        "wku_backend_app.py",
        "wku_backend_README.md",
        "wku_backend_requirements.txt"
    )

    Compress-Archive -Path $items -DestinationPath $OutputPath -CompressionLevel Optimal
    Write-Host "Deploy package rebuilt:" $OutputPath
}
finally {
    Pop-Location
}
