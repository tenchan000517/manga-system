# コマンド早見表

> 詳細は [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) を参照

## ✅ 正解のコマンド（推奨）

### 初回セットアップ
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_en.ps1
```

### マンガ生成
```powershell
.\run_en.ps1 simple_story_example
```

### 自分のストーリーで生成
```powershell
# 1. stories\my_story.yaml を作成
# 2. 生成実行
.\run_en.ps1 my_story
```

---

## 🔧 手動実行（デバッグ用）

```powershell
# 仮想環境を有効化
.\venv_win\Scripts\Activate.ps1

# ステップ1: YAML展開
python scripts\expand_story.py stories\my_story.yaml

# ステップ2: マンガ生成
python scripts\generate_from_yaml.py stories\my_story_expanded.yaml

# 無効化
deactivate
```

---

## ❌ 使わないファイル（参考）

以下は文字化けするため使用しません：
- ~~setup.ps1~~ → `setup_en.ps1` を使用
- ~~generate.ps1~~ → `run_en.ps1` を使用
- ~~setup.bat~~ → PowerShell版を使用

---

## 📋 その他のコマンド

### 生成画像を開く
```powershell
start output\my_story_generated.png
```

### 仮想環境の再作成
```powershell
Remove-Item -Recurse -Force venv_win
.\setup_en.ps1
```

### パッケージ確認
```powershell
.\venv_win\Scripts\pip list
```

### パッケージ更新
```powershell
.\venv_win\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt
deactivate
```
