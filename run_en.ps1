# Manga Generation System (Multi-page Support)
param(
    [Parameter(Mandatory=$true)]
    [string]$StoryPattern
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

# Search for story files
$StoryFiles = Get-ChildItem "stories\${StoryPattern}.yaml" -ErrorAction SilentlyContinue

if ($StoryFiles.Count -eq 0) {
    Write-Host "Error: No story files found: stories\${StoryPattern}.yaml" -ForegroundColor Red
    exit 1
}

Write-Host "Found $($StoryFiles.Count) file(s):" -ForegroundColor Cyan
foreach ($file in $StoryFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor Gray
}
Write-Host ""

# Determine session ID (next number in year-month/day folder)
$Now = Get-Date
$YearMonth = $Now.ToString("yyyy-MM")
$Day = $Now.ToString("dd")
$DateDir = "output\$YearMonth\$Day"

if (Test-Path $DateDir) {
    $ExistingFolders = Get-ChildItem $DateDir -Directory | Where-Object { $_.Name -match '^\d+$' }
    if ($ExistingFolders) {
        $MaxNumber = ($ExistingFolders | ForEach-Object { [int]$_.Name } | Measure-Object -Maximum).Maximum
        $SessionID = $MaxNumber + 1
    } else {
        $SessionID = 1
    }
} else {
    $SessionID = 1
}

# Set session ID as environment variable
$env:MANGA_SESSION_ID = $SessionID.ToString()
Write-Host "Session ID: $SessionID" -ForegroundColor Yellow
Write-Host "Output folder: $DateDir\$SessionID\" -ForegroundColor Yellow
Write-Host ""

# Process each file
$TotalFiles = $StoryFiles.Count
$CurrentFile = 0

foreach ($file in $StoryFiles) {
    $CurrentFile++
    $StoryName = $file.BaseName

    Write-Host "[$CurrentFile/$TotalFiles] Processing $StoryName..." -ForegroundColor Cyan
    Write-Host ""

    Write-Host "  [Step 1/2] Expanding YAML..." -ForegroundColor Green
    & $PythonExe scripts\expand_story.py "stories\$($file.Name)"

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  Error: YAML expansion failed" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "  [Step 2/2] Generating manga..." -ForegroundColor Green
    Write-Host "  (This may take several seconds...)" -ForegroundColor Yellow
    Write-Host ""

    & $PythonExe scripts\generate_from_yaml.py "stories\${StoryName}_expanded.yaml"

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  Error: Manga generation failed" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "  ✓ $StoryName complete!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output: $DateDir\$SessionID\" -ForegroundColor Yellow
Write-Host ""
