$pythonExe = "C:\Users\Varad\anaconda3\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}
$backendDir = Join-Path $PSScriptRoot "backend"
Set-Location $backendDir
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Starting Supply Chain Digital Twin API Server..." -ForegroundColor Green
Write-Host "  Opening Swagger UI at: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "===================================================================" -ForegroundColor Cyan
Start-Process "http://localhost:8000/docs"
& $pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
