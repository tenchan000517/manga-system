# Instagram用マンガ自動生成システム セットアップ
Write-Host "========================================"
Write-Host "Instagram用マンガ自動生成システム セットアップ"
Write-Host "========================================"
Write-Host ""

# 仮想環境の確認と作成
if (Test-Path "venv_win") {
    Write-Host "既存の仮想環境を削除中..."
    Remove-Item -Recurse -Force venv_win
}

Write-Host "仮想環境を作成中..."
python -m venv venv_win

Write-Host "仮想環境を有効化中..."
& .\venv_win\Scripts\Activate.ps1

Write-Host "パッケージをインストール中..."
pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "========================================"
Write-Host "セットアップ完了！"
Write-Host "========================================"
Write-Host ""
Write-Host "使い方:"
Write-Host '  1. 仮想環境を有効化: .\venv_win\Scripts\Activate.ps1'
Write-Host '  2. マンガ生成: .\generate.ps1 my_story'
Write-Host ""
Write-Host "または一発実行:"
Write-Host '  .\run.ps1 my_story'
Write-Host ""
