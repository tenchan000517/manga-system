@echo off
echo ========================================
echo マンガ自動生成システム
echo ========================================
echo.

if "%1"=="" (
    echo 使い方: generate.bat ^<ストーリーファイル名^>
    echo.
    echo 例:
    echo   generate.bat my_story
    echo.
    echo これで以下が自動実行されます:
    echo   1. stories/my_story.yaml を展開
    echo   2. マンガを生成
    echo.
    pause
    exit /b 1
)

set STORY_NAME=%1

echo ステップ1: YAML展開中...
python scripts\expand_story.py stories\%STORY_NAME%.yaml

if errorlevel 1 (
    echo.
    echo エラー: YAML展開に失敗しました
    pause
    exit /b 1
)

echo.
echo ステップ2: マンガ生成中...
echo （これには数十秒かかる場合があります）
echo.

python scripts\generate_from_yaml.py stories\%STORY_NAME%_expanded.yaml

if errorlevel 1 (
    echo.
    echo エラー: マンガ生成に失敗しました
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 完了！
echo ========================================
echo.
echo 生成されたマンガ: output\%STORY_NAME%_generated.png
echo.
pause
