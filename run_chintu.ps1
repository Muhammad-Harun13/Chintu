# Chintu Windows Launcher
# Disables fullscreen and launches the app using the local virtual environment

$env:DISPLAY_FULLSCREEN = "off"
$env:PYTHONPATH = "$PSScriptRoot\Chintu"

if (Test-Path ".\.venv\Scripts\python.exe") {
    Write-Host "Launching Chintu in Windowed Mode..." -ForegroundColor Cyan
    .\.venv\Scripts\python.exe Chintu\main.py
} else {
    Write-Host "Error: Virtual environment not found. Please run 'python -m venv .venv' and install requirements." -ForegroundColor Red
}
