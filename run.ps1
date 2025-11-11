# マンガ自動生成システム（仮想環境自動対応）
param(
    [Parameter(Mandatory=$true)]
    [string]$StoryName
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

Write-Host "ステップ1: YAML展開中..."
& $PythonExe scripts\expand_story.py stories\$StoryName.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "エラー: YAML展開に失敗しました" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "ステップ2: マンガ生成中..."
Write-Host "（これには数十秒かかる場合があります）"
Write-Host ""

& $PythonExe scripts\generate_from_yaml.py stories\${StoryName}_expanded.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "エラー: マンガ生成に失敗しました" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "✓ 完了！" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "生成されたマンガ: output\${StoryName}_generated.png"
Write-Host ""
