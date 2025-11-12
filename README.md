# Instagram用マンガ自動生成システム

簡易YAMLを書くだけで、AIがマンガを自動生成します。

## セットアップ

```bash
# 仮想環境作成とパッケージインストール
python -m venv venv_win
venv_win\Scripts\activate
pip install -r requirements.txt

# APIキー設定
# .env ファイルに GOOGLE_API_KEY を設定
```

## 使い方

### 1. ストーリーYAMLを作成

`stories/my_story.yaml`:
```yaml
story_title: "タイトル"
layout_pattern: "pattern_3panel"

scenes:
  - character: TEN
    emotion: 悩み
    dialogue: "セリフ"
    background: "背景"
    description: "動作"
```

### 2. 生成

```bash
# YAML展開
python3 scripts/expand_story.py stories/my_story.yaml

# マンガ生成
venv_win/Scripts/python.exe scripts/generate_from_yaml.py stories/my_story_expanded.yaml
```

出力先: `output/<年月>/<日付>/<セッション番号>/`

### 複数ページを同じフォルダにまとめる

```bash
SESSION=5
venv_win/Scripts/python.exe scripts/generate_from_yaml.py stories/page1_expanded.yaml --session-folder $SESSION
venv_win/Scripts/python.exe scripts/generate_from_yaml.py stories/page2_expanded.yaml --session-folder $SESSION
```

## ドキュメント

- **🚨 次世代Claude Code必読:** [docs/HANDOFF.md](docs/HANDOFF.md)
- **実行手順とルール:** [docs/STORY_CREATION_RULES.md](docs/STORY_CREATION_RULES.md)
- **システム構造と改善ポイント:** [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)

---

Made with ❤️ by TEN × Claude Code
