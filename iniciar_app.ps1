$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonPath = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$AppPath = Join-Path $ProjectRoot "backend\app.py"
$AppPort = 5001
$AppUrl = "http://127.0.0.1:$AppPort/?v=20260522-2"

if (-not (Test-Path $PythonPath)) {
    Write-Host "No se encontro el Python del entorno virtual en: $PythonPath" -ForegroundColor Red
    Write-Host "Revisa que exista la carpeta venv." -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "Iniciando Dulceria Inventario..." -ForegroundColor Cyan
Write-Host "Proyecto: $ProjectRoot"

$listeners = Get-NetTCPConnection -LocalPort $AppPort -State Listen -ErrorAction SilentlyContinue
if ($listeners) {
    Write-Host "Liberando puerto $AppPort..." -ForegroundColor Yellow
    $listeners |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object {
            Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
        }
    Start-Sleep -Seconds 1
}

Start-Process -FilePath $AppUrl

Write-Host "Servidor disponible en $AppUrl" -ForegroundColor Green
Write-Host "Deja esta ventana abierta mientras uses la app. Para detenerla, presiona Ctrl + C."

Set-Location $ProjectRoot
$env:PORT = "$AppPort"
& $PythonPath $AppPath
