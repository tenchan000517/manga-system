# マンガ自動生成システム 使い方ガイド

> **総合ドキュメント**: システム全体の理解は [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) を参照してください

## 🎯 システム概要

このシステムは**2ステップ**でマンガを自動生成します：

1. **簡易ストーリー記述 → 完全YAML生成**
2. **完全YAML → Nanobanana APIでマンガ生成**

## 📝 ワークフロー

```
[簡易YAML作成]
   ↓
[expand_story.py] ← キャラテンプレート、コマ割りパターン使用
   ↓
[完全YAML]
   ↓
[generate_from_yaml.py] ← キャラ画像、YAML使用
   ↓
[完成マンガ]
```

## 🚀 セットアップ（Windows）

### 1. 仮想環境のセットアップ

PowerShellで：

```powershell
cd C:\instagram-manga-generator

# PowerShellスクリプトを実行可能にする（初回のみ）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# セットアップ実行（仮想環境作成+パッケージインストール）
.\setup.ps1
```

これで `venv_win` フォルダに仮想環境が作成され、必要なパッケージが全てインストールされます。

### 2. APIキー確認

`.env` ファイルに Google AI Studio APIキーが設定されていることを確認：

```
GOOGLE_API_KEY=your_api_key_here
```

## 📖 使い方

### ステップ1: 簡易ストーリーを作成

`stories/` フォルダに新しいYAMLファイルを作成します。

**例: `stories/my_story.yaml`**

```yaml
story_title: "AIマンガシステム誕生記 #1"
layout_pattern: "pattern_3panel"  # 3, 4, 5, 6コマから選択

scenes:
  - character: TEN
    emotion: 悩み
    dialogue: "インスタでマンガ投稿したいけど...毎回描くの無理ゲーすぎる"
    background: "深夜のデスク、モニターにInstagramが映っている"
    description: "パソコンの前で腕組みして考え込んでいる"

  - character: CLAUDECODE
    emotion: 提案
    dialogue: "それ、AIで自動化できますよ！"
    background: "画面から飛び出してくる演出"
    description: "元気いっぱい、片手を上げて挨拶"

  - character: TEN
    emotion: 驚き
    dialogue: "マジで!? どうやるの？"
    background: "同じデスク"
    description: "目を輝かせて身を乗り出す"
```

### ステップ2: マンガを自動生成

**簡単な方法（推奨）**:

```powershell
.\run.ps1 my_story
```

これだけで、YAML展開→マンガ生成が自動実行されます！

**手動で実行する場合**:

```powershell
# 仮想環境を有効化
.\venv_win\Scripts\Activate.ps1

# ステップ2-1: YAML展開
python scripts\expand_story.py stories\my_story.yaml

# ステップ2-2: マンガ生成
python scripts\generate_from_yaml.py stories\my_story_expanded.yaml
```

完成したマンガは `output/` フォルダに保存されます！

## 🎨 カスタマイズ

### コマ割りパターン

`layout_pattern` で選択：

- `pattern_3panel` - 3コマ（縦分割）
- `pattern_4panel_equal` - 4コマ（均等分割）
- `pattern_5panel` - 5コマ
- `pattern_6panel` - 6コマ

### 感情表現

#### TEN（エンジニア）
- 通常
- 悩み
- 驚き
- 喜び
- 決意
- 説明

#### CLAUDECODE（AIロボット）
- 通常
- 提案
- 作業中
- 発見
- 承認
- 説明

## 📁 ファイル構成

```
instagram-manga-generator/
├── characters/              # キャラクター基準画像
│   ├── TEN_ORIGIN.png
│   └── CLAUDECODE_ORIGIN.png
├── templates/               # テンプレート（自動使用）
│   ├── character_templates.yaml
│   └── layout_patterns.yaml
├── stories/                 # ストーリー定義
│   ├── my_story.yaml               ← あなたが作成
│   └── my_story_expanded.yaml      ← 自動生成
├── output/                  # 生成されたマンガ
│   └── my_story_generated.png      ← 完成！
└── scripts/
    ├── expand_story.py      # YAML展開スクリプト
    └── generate_from_yaml.py # マンガ生成スクリプト
```

## 💡 ヒント

### 効率的なワークフロー

1. **簡易YAMLは超シンプルに**
   - キャラクター、感情、セリフ、背景だけ書く
   - 詳細は自動展開に任せる

2. **コマ割りパターンを活用**
   - 3コマ: テンポよく、起承転結の一部
   - 4コマ: 伝統的な4コマ漫画
   - 5-6コマ: より詳細なストーリー展開

3. **感情表現を使い分ける**
   - 会話のキャッチボールは「提案」「驚き」などで演出
   - 視線方向は自動で最適化されます

### トラブルシューティング

#### マンガが生成されない

- APIキーが正しいか確認
- レート制限に達していないか確認（少し待つ）
- インターネット接続を確認

#### キャラクターが一貫しない

- キャラクター画像（TEN_ORIGIN.png、CLAUDECODE_ORIGIN.png）が`characters/`フォルダに存在するか確認
- YAML展開時にキャラクター情報が正しく含まれているか確認

## 🔧 高度な使い方

### カスタムキャラクターを追加

1. `characters/` にキャラクター画像を追加（例: `NEWCHAR_ORIGIN.png`）
2. `templates/character_templates.yaml` に定義を追加
3. 簡易YAMLで `character: NEWCHAR` として使用

### カスタムレイアウトパターン

`templates/layout_patterns.yaml` に新しいパターンを追加可能。

## 📊 コスト目安

- Google AI Studio: 基本無料（制限あり）
- Gemini API: 約$0.039/枚（約6円/ページ）

## 📚 参考

- [Google AI Studio](https://aistudio.google.com)
- [Gemini API ドキュメント](https://ai.google.dev/gemini-api/docs)

---

Made with ❤️ by TEN × Claude Code
