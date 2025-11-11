@echo off
echo ========================================
echo Instagram用マンガ生成システム セットアップ
echo （仮想環境版）
echo ========================================
echo.

echo 仮想環境を作成中...
conda create -n manga-gen python=3.10 -y

echo.
echo 仮想環境をアクティベート...
call conda activate manga-gen

echo.
echo パッケージをインストール中...
pip install -r requirements.txt

echo.
echo ========================================
echo セットアップ完了！
echo ========================================
echo.
echo 使い方:
echo   1. conda activate manga-gen
echo   2. cd scripts
echo   3. python generate_manga.py ../stories/episode1.yaml
echo.
echo 終了するには:
echo   conda deactivate
echo.
pause
