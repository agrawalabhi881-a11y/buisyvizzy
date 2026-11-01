$pythonExe = "C:\Users\Varad\AppData\Local\Programs\Python\Python314\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}
Set-Location $PSScriptRoot
& $pythonExe backend\tests\run_tests.py
