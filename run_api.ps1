# run_api.ps1
$PythonExe = "C:\Users\Varad\anaconda3\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

Set-Location "$PSScriptRoot\backend"
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Starting NEXUS Supply Chain Digital Twin Platform..." -ForegroundColor Green
Write-Host "  Opening Web App at:    http://localhost:8000/web" -ForegroundColor Cyan
Write-Host "  Opening Swagger UI at: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "===================================================================" -ForegroundColor Cyan

Start-Process "http://localhost:8000/web"
Start-Process "http://localhost:8000/docs"
& $PythonExe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
