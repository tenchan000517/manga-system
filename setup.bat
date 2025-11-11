@echo off
echo ========================================
echo Instagram用マンガ生成システム セットアップ
echo ========================================
echo.

echo パッケージをインストール中...
pip install -r requirements.txt

echo.
echo ========================================
echo セットアップ完了！
echo ========================================
echo.
echo 使い方:
echo   1. cd scripts
echo   2. python generate_manga.py ../stories/episode1.yaml
echo.
pause
