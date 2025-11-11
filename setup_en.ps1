# Manga Generation System - Setup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup: Manga Generation System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check and create virtual environment
if (Test-Path "venv_win") {
    Write-Host "[1/4] Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv_win
}

Write-Host "[2/4] Creating virtual environment..." -ForegroundColor Green
python -m venv venv_win

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
    Write-Host "Make sure Python is installed and in PATH"
    exit 1
}

Write-Host "[3/4] Activating virtual environment..." -ForegroundColor Green
& .\venv_win\Scripts\Activate.ps1

Write-Host "[4/4] Installing packages..." -ForegroundColor Green
pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: Failed to install packages" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usage:" -ForegroundColor Yellow
Write-Host "  .\run_en.ps1 my_story"
Write-Host ""
Write-Host "Or manually:" -ForegroundColor Yellow
Write-Host "  1. Activate: .\venv_win\Scripts\Activate.ps1"
Write-Host "  2. Generate: python scripts\expand_story.py stories\my_story.yaml"
Write-Host ""
