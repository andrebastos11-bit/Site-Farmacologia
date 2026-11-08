$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$previewPython = Get-Command python.exe -All -ErrorAction SilentlyContinue | Where-Object { $_.Source -notlike '*WindowsApps*' } | Select-Object -First 1
if (-not $previewPython) { throw 'Python não encontrado. Instale Python ou indique o caminho do executável.' }
Write-Host 'ProPharma V2 experimental: http://localhost:8001 (Ctrl+C para parar)'
& $previewPython.Source -m http.server 8001 --bind 127.0.0.1
