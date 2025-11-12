# マンガ自動生成システム（仮想環境自動対応・複数ページ対応）
param(
    [Parameter(Mandatory=$true)]
    [string]$StoryPattern
)

Write-Host "========================================"
Write-Host "マンガ自動生成システム"
Write-Host "========================================"
Write-Host ""

# 仮想環境の確認
if (-not (Test-Path "venv_win\Scripts\python.exe")) {
    Write-Host "仮想環境が見つかりません。setup.ps1 を先に実行してください。" -ForegroundColor Red
    Write-Host ""
    Write-Host "実行方法:"
    Write-Host "  .\setup.ps1"
    exit 1
}

# 仮想環境のPythonを使用
$PythonExe = ".\venv_win\Scripts\python.exe"

# ストーリーファイルを検索
$StoryFiles = Get-ChildItem "stories\${StoryPattern}.yaml" -ErrorAction SilentlyContinue

if ($StoryFiles.Count -eq 0) {
    Write-Host "エラー: ストーリーファイルが見つかりません: stories\${StoryPattern}.yaml" -ForegroundColor Red
    exit 1
}

Write-Host "検出されたファイル: $($StoryFiles.Count)個" -ForegroundColor Cyan
foreach ($file in $StoryFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor Gray
}
Write-Host ""

# セッションIDを決定（年月/日付フォルダ内の次のナンバー）
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

# 環境変数にセッションIDを設定
$env:MANGA_SESSION_ID = $SessionID.ToString()
Write-Host "セッションID: $SessionID" -ForegroundColor Yellow
Write-Host "出力先: $DateDir\$SessionID\" -ForegroundColor Yellow
Write-Host ""

# 各ファイルを処理
$TotalFiles = $StoryFiles.Count
$CurrentFile = 0

foreach ($file in $StoryFiles) {
    $CurrentFile++
    $StoryName = $file.BaseName

    Write-Host "[$CurrentFile/$TotalFiles] $StoryName を処理中..." -ForegroundColor Cyan
    Write-Host ""

    Write-Host "  ステップ1: YAML展開中..."
    & $PythonExe scripts\expand_story.py "stories\$($file.Name)"

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  エラー: YAML展開に失敗しました" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "  ステップ2: マンガ生成中..."
    Write-Host "  （これには数十秒かかる場合があります）"
    Write-Host ""

    & $PythonExe scripts\generate_from_yaml.py "stories\${StoryName}_expanded.yaml"

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  エラー: マンガ生成に失敗しました" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "  ✓ $StoryName 完了！" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================"
Write-Host "✓ すべて完了！" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "生成されたマンガ: $DateDir\$SessionID\" -ForegroundColor Yellow
Write-Host ""
