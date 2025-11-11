# マンガ自動生成システム
param(
    [Parameter(Mandatory=$true)]
    [string]$StoryName
)

Write-Host "========================================"
Write-Host "マンガ自動生成システム"
Write-Host "========================================"
Write-Host ""

Write-Host "ステップ1: YAML展開中..."
python scripts\expand_story.py stories\$StoryName.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "エラー: YAML展開に失敗しました" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "ステップ2: マンガ生成中..."
Write-Host "（これには数十秒かかる場合があります）"
Write-Host ""

python scripts\generate_from_yaml.py stories\${StoryName}_expanded.yaml

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
