# Manga Generation System
param(
    [Parameter(Mandatory=$true)]
    [string]$StoryName
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Manga Generation System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check virtual environment
if (-not (Test-Path "venv_win\Scripts\python.exe")) {
    Write-Host "Error: Virtual environment not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run setup first:" -ForegroundColor Yellow
    Write-Host "  .\setup_en.ps1"
    exit 1
}

# Use virtual environment Python
$PythonExe = ".\venv_win\Scripts\python.exe"

Write-Host "[Step 1/2] Expanding YAML..." -ForegroundColor Green
& $PythonExe scripts\expand_story.py stories\$StoryName.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: YAML expansion failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[Step 2/2] Generating manga..." -ForegroundColor Green
Write-Host "(This may take several seconds...)" -ForegroundColor Yellow
Write-Host ""

& $PythonExe scripts\generate_from_yaml.py stories\${StoryName}_expanded.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: Manga generation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output: output\${StoryName}_generated.png" -ForegroundColor Yellow
Write-Host ""
