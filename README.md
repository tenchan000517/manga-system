# Instagram用マンガ自動生成システム v2.0

TEN × Claude Code の開発備忘録をマンガ化するプロジェクト

> 📖 **ドキュメント一覧**: [DOCS_INDEX.md](DOCS_INDEX.md) で目的別に探せます

## 🎯 概要

- **超簡単な入力**：キャラクター、感情、セリフだけ書けばOK
- **自動展開**：詳細な構造化YAMLを自動生成
- **固定キャラクター**：TEN、Claude Codeのプロンプトは使い回し
- **コマ割りパターン**：3〜6コマのプリセットから選択
- Google AI Studio の Nano Banana (Gemini 2.0/2.5 Flash) を使用
- Instagram最適サイズ（1:1.4アスペクト比）で出力

## ✨ 新機能（v2.0）

### ネーム不要！直接ストーリー記述
従来のネーム画像作成を完全スキップ。簡易YAMLだけでマンガ生成可能。

### 2ステップワークフロー
```
簡易YAML → 完全YAML → マンガ生成
```

### テンプレート活用
- キャラクター情報は固定テンプレート
- コマ割りパターンもプリセット化
- 毎回同じ設定を書く必要なし

## 📚 ドキュメント

| ドキュメント | 内容 | 対象 |
|------------|------|------|
| **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** ★ | 総合ドキュメント | システム全体を理解したい |
| [COMMANDS.md](COMMANDS.md) | コマンド早見表 | すぐ実行したい |
| [QUICKSTART_EN.md](QUICKSTART_EN.md) | クイックスタート | 初めて使う |
| [USAGE_GUIDE.md](USAGE_GUIDE.md) | 詳しい使い方 | 日常的に使う |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | 実装詳細 | コードを理解したい |

## 📁 ディレクトリ構成

```
instagram-manga-generator/
├── characters/              # キャラクター基準画像
│   ├── TEN_ORIGIN.png
│   └── CLAUDECODE_ORIGIN.png
├── templates/               # テンプレート（自動使用）
│   ├── character_templates.yaml    # キャラ情報固定化
│   └── layout_patterns.yaml        # コマ割りプリセット
├── stories/                 # ストーリー定義
│   ├── simple_story_example.yaml   # 簡易YAML（あなたが作成）
│   └── simple_story_example_expanded.yaml  # 完全YAML（自動生成）
├── output/                  # 生成されたマンガ
├── scripts/                 # 実行スクリプト
│   ├── expand_story.py           # 簡易→完全YAML変換
│   ├── generate_from_yaml.py     # YAML→マンガ生成
│   └── utils.py
├── .env                     # APIキー（秘密）
├── requirements.txt         # 必要なパッケージ
├── generate.bat             # Windows用一発生成バッチ
├── README.md                # このファイル
└── USAGE_GUIDE.md           # 詳しい使い方
```

## 🚀 セットアップ

### 1. 仮想環境のセットアップ（推奨）

PowerShellで：

```powershell
cd C:\instagram-manga-generator

# PowerShellスクリプトを実行可能にする（初回のみ）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# セットアップ実行（仮想環境作成+パッケージインストール）
.\setup.ps1
```

または手動セットアップ：

```powershell
# 仮想環境作成
python -m venv venv_win

# 有効化
.\venv_win\Scripts\Activate.ps1

# パッケージインストール
pip install -r requirements.txt
```

### 2. APIキー設定

`.env` ファイルにGoogle AI Studio APIキーが設定済みです。

### 3. 動作確認

```bash
cd scripts
python utils.py
```

## 📝 使い方

### クイックスタート（Windows）

1. **簡易ストーリーを作成** (`stories/my_story.yaml`):

```yaml
story_title: "タイトル"
layout_pattern: "pattern_3panel"  # 3, 4, 5, 6コマから選択

scenes:
  - character: TEN
    emotion: 悩み
    dialogue: "セリフ"
    background: "背景の説明"
    description: "キャラの動作"
```

2. **PowerShellスクリプトで一発生成**:

```powershell
.\run.ps1 my_story
```

完成！`output/my_story_generated.png` が生成されます。

> **Note**: `run.ps1` は仮想環境を自動で使用します。事前に `setup.ps1` を実行してください。

### 詳しい使い方

詳細は [USAGE_GUIDE.md](USAGE_GUIDE.md) を参照してください。

## 🎨 キャラクター

- **TEN**: エンジニア（メガネ、黒髪、カジュアル）
- **Claude Code**: AIアシスタント（ロボット型、オレンジ×ブルー）

## 💰 コスト

- Google AI Studio: 無料（1日20-30回程度）
- API利用: 約$0.039/枚（約6円）

## 📱 Instagram投稿サイズ

- フィード: 1080×1350px（4:5）
- リール: 1080×1920px（9:16）

## 🔧 トラブルシューティング

### パッケージがインストールできない

Windowsで管理者権限で実行してみてください：

```bash
pip install --user -r requirements.txt
```

### APIエラー

- APIキーが正しいか確認
- レート制限に達していないか確認（少し待つ）

### 画像が生成されない

- インターネット接続を確認
- Google AI Studioのステータスを確認

## 📚 参考リソース

- [Google AI Studio](https://aistudio.google.com)
- [Nano Banana公式ドキュメント](https://ai.google.dev/gemini-api/docs)
- [Instagram画像サイズガイド](https://help.instagram.com/1631821640426723)

## 📄 ライセンス

個人プロジェクト

---

Made with ❤️ by TEN × Claude Code
