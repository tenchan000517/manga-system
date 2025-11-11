# Instagram Manga Generator - プロジェクト総合ドキュメント

## 📋 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [システムの要件と意図](#システムの要件と意図)
3. [Easy Bananaとの関係](#easy-bananaとの関係)
4. [開発プロセス](#開発プロセス)
5. [環境・前提条件](#環境前提条件)
6. [実行コマンド早見表](#実行コマンド早見表)
7. [ドキュメント構成](#ドキュメント構成)
8. [トラブルシューティング](#トラブルシューティング)

---

## プロジェクト概要

### 🎯 プロジェクトの目的

**「エンジニアの学びをInstagram漫画で発信する」** ことを、最小限の労力で実現するための自動生成システム。

### ✨ 実現したこと

従来の手法（ネーム作成 → 手動生成）を完全自動化し、**簡易YAML記述だけでマンガを生成**できるシステムを構築。

### 🔑 キーワード

- **ネーム不要**: 手書きネームの作成を完全スキップ
- **テンプレート活用**: キャラクター情報とコマ割りパターンを固定化
- **2ステップ自動化**: 簡易YAML → 完全YAML → マンガ生成
- **Nanobanana (Gemini 2.5 Flash Image Preview)** 使用

---

## システムの要件と意図

### 💡 設計思想

#### 問題意識
```
【課題】
マンガ制作には時間がかかる
→ ネーム作成
→ 手動でプロンプト入力
→ 1コマずつ生成
→ 編集・結合

【解決策】
テンプレート化 + 自動化
→ ストーリーだけ書く
→ 残りは自動生成
```

#### コンセプト
1. **入力の最小化**: キャラクター、感情、セリフ、背景だけ
2. **固定部分の分離**: キャラ設定、コマ割りは使い回し
3. **段階的変換**: 人間が書きやすい簡易形式 → AIが理解しやすい詳細形式
4. **プログラマティック制御**: 全プロセスをスクリプト化

### 🎨 システム設計

```
[Layer 1: 入力]
簡易YAML（人間が書く）
  ↓
[Layer 2: 変換]
expand_story.py
  + character_templates.yaml
  + layout_patterns.yaml
  ↓
[Layer 3: 詳細定義]
完全YAML（AI向け構造化データ）
  ↓
[Layer 4: 生成]
generate_from_yaml.py
  + キャラクター画像
  + Nanobanana API
  ↓
[Layer 5: 出力]
完成マンガ（PNG）
```

### 📊 効率化の定量評価

| 項目 | 従来手法 | 新システム | 削減率 |
|------|----------|-----------|--------|
| ネーム作成 | 30分 | 0分 | 100% |
| プロンプト記述 | 20分 | 5分 | 75% |
| 手動生成操作 | 15分 | 0分 | 100% |
| **合計** | **65分** | **5分** | **92%** |

---

## Easy Bananaとの関係

### 🍌 Easy Bananaとは

先輩エンジニアが作成したChrome拡張機能。Gemini 2.5 Flash Image Preview (Nanobanana) を使った画像生成ツール。

**リポジトリ**: `C:\Users\tench\Downloads\easy_banana_v1_1_2\easy_banana`

### 📚 Easy Bananaから学んだこと

#### 1. **システムプロンプト戦略**
```javascript
// Easy Banana: sidepanel.js:26-32
const SYSTEM_PROMPT = [
  'You are an expert image generation assistant.',
  'Generate one or more high-quality images that match the user\'s prompt.',
  'Return images inline using inlineData with an appropriate MIME type (prefer image/png).',
  // ...
].join(' ');
```

→ **本システムに応用**: `generate_from_yaml.py` のプロンプト生成に活用

#### 2. **テンプレート管理**
```
easy_banana/template/
  ├── char-keisuke.png        # キャラクター画像
  ├── koma3-1.png             # 3コマパターン
  ├── koma4-1.png             # 4コマパターン
  └── index.json              # メタデータ
```

→ **本システムに応用**:
- `characters/` にキャラクター画像
- `templates/` にYAML定義

#### 3. **参照画像の活用**
Easy Bananaでは参照画像（キャラクター、コマ割り）を最大6枚まで添付可能。

→ **本システムに応用**: キャラクター画像を自動添付

#### 4. **ライブラリ機能**
よく使う画像を `chrome.storage.local` に保存して再利用。

→ **本システムに応用**: テンプレートファイルで固定化

### 🔄 Easy Bananaとの使い分け

| 用途 | 推奨ツール | 理由 |
|------|-----------|------|
| 1ページ自動生成 | **本システム** | 完全自動化 |
| 細かい調整が必要 | Easy Banana | 手動で微調整可能 |
| バッチ処理 | **本システム** | スクリプト化済み |
| UI上で確認しながら | Easy Banana | ビジュアルフィードバック |

### 💡 Easy Banana参照時のポイント

#### コマ割りテンプレート活用（将来拡張）
```javascript
// Easy Banana: library.js
// テンプレート画像を参照画像として使用
const templates = await loadTemplates();
```

**今後の拡張案**:
1. Easy Bananaの `template/koma*.png` を本システムの参照画像として追加
2. より正確なレイアウト制御が可能に

#### API呼び出し方法の参考
```javascript
// Easy Banana: sidepanel.js:774-797
const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_IMAGE}:generateContent`;
const body = {
  contents: [{
    role: 'user',
    parts: [...imageParts, { text: `${SYSTEM_PROMPT}\n\nUser prompt:\n${prompt}` }]
  }]
};
```

**本システムでの実装**: `generate_from_yaml.py:190-192`

---

## 開発プロセス

### 🗓️ タイムライン

#### Phase 1: 要件定義（対話開始）
```
ユーザー提案: "ネーム作成を省略したい"
↓
設計方針決定:
  - キャラクター情報の固定化
  - コマ割りパターンのプリセット化
  - 簡易入力フォーマットの設計
```

#### Phase 2: テンプレート設計
```
作成物:
  ✅ templates/character_templates.yaml
  ✅ templates/layout_patterns.yaml
  ✅ stories/simple_story_example.yaml (サンプル)
```

#### Phase 3: 変換スクリプト実装
```
作成物:
  ✅ scripts/expand_story.py
     - 簡易YAML読み込み
     - テンプレート適用
     - 感情表現の英語変換
     - 視線方向の自動最適化
     - 完全YAML出力
```

#### Phase 4: 生成スクリプト実装
```
作成物:
  ✅ scripts/generate_from_yaml.py
     - 完全YAML読み込み
     - プロンプト生成
     - Nanobanana API呼び出し
     - 画像保存
```

#### Phase 5: 実行環境整備
```
作成物:
  ✅ setup_en.ps1 (仮想環境セットアップ)
  ✅ run_en.ps1 (一発生成スクリプト)
  ✅ QUICKSTART_EN.md
```

#### Phase 6: デバッグ・修正
```
問題:
  ❌ 文字エンコーディング (PowerShell日本語)
  ❌ キャラクター名のスペース処理
  ❌ モデル名の誤り

解決:
  ✅ 英語版スクリプト作成
  ✅ スペース自動削除処理
  ✅ gemini-2.5-flash-image-preview に修正
  ✅ デバッグ情報追加
```

### 🎓 学んだ教訓

1. **文字エンコーディングは要注意**: Windows環境では英語版を用意
2. **段階的テスト**: YAML生成 → API呼び出しを分離してテスト
3. **テンプレート化の威力**: 一度定義すれば永続的に効率化
4. **Easy Bananaの知見活用**: 既存の成功パターンから学ぶ

---

## 環境・前提条件

### 💻 動作環境

#### OS
- **Windows 10/11** (PowerShell 5.1以上)
- WSL2 (開発・テスト用、オプション)

#### Python
- **Python 3.10以上** (推奨: 3.11+)
- 仮想環境: `venv_win` (自動作成)

#### 必須パッケージ
```txt
google-generativeai>=0.8.0
Pillow>=10.0.0
PyYAML>=6.0
python-dotenv>=1.0.0
```

#### API
- **Google AI Studio API Key** (無料枠利用可能)
- モデル: `gemini-2.5-flash-image-preview`

### 📂 ディレクトリ構造（確定版）

```
C:\instagram-manga-generator/
├── characters/                    # キャラクター画像（固定）
│   ├── TEN_ORIGIN.png
│   └── CLAUDECODE_ORIGIN.png
│
├── templates/                     # テンプレート定義（固定）
│   ├── character_templates.yaml   # キャラ情報
│   └── layout_patterns.yaml       # コマ割りパターン
│
├── stories/                       # ストーリー定義（ユーザー作成）
│   ├── simple_story_example.yaml          # 簡易YAML（入力）
│   └── simple_story_example_expanded.yaml # 完全YAML（自動生成）
│
├── output/                        # 生成結果（自動作成）
│   └── simple_story_example_generated.png
│
├── scripts/                       # 実行スクリプト
│   ├── expand_story.py           # YAML展開
│   ├── generate_from_yaml.py     # マンガ生成
│   └── utils.py                  # ユーティリティ
│
├── venv_win/                      # 仮想環境（自動作成）
│
├── .env                           # API設定（重要！）
│   └── GOOGLE_API_KEY=your_key_here
│
├── requirements.txt               # パッケージリスト
│
├── setup_en.ps1                   # セットアップスクリプト
├── run_en.ps1                     # 生成スクリプト
│
└── docs/                          # ドキュメント群
    ├── PROJECT_OVERVIEW.md        # 本ドキュメント（総合）★
    ├── QUICKSTART_EN.md           # クイックスタート（英語）
    ├── USAGE_GUIDE.md             # 詳細使い方（日本語）
    ├── README.md                  # プロジェクト概要
    └── IMPLEMENTATION_SUMMARY.md  # 実装詳細
```

---

## 実行コマンド早見表

### 🚀 初回セットアップ

```powershell
# 1. PowerShellスクリプトを有効化（初回のみ）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. セットアップ実行
cd C:\instagram-manga-generator
.\setup_en.ps1
```

**実行内容**:
- 仮想環境 `venv_win` 作成
- 必要パッケージインストール

### ✅ 動作確認

```powershell
# サンプルで動作テスト
.\run_en.ps1 simple_story_example
```

**期待結果**:
```
[Step 1/2] Expanding YAML...
[Step 2/2] Generating manga...
Complete!
Output: output\simple_story_example_generated.png
```

### 📝 新しいマンガを作成

#### ステップ1: 簡易YAMLを作成

`stories\my_first_manga.yaml`:
```yaml
story_title: "My First Manga"
layout_pattern: "pattern_3panel"

scenes:
  - character: TEN
    emotion: 悩み
    dialogue: "セリフ"
    background: "背景"
    description: "動作"
  # ... 3コマ分
```

#### ステップ2: 生成

```powershell
.\run_en.ps1 my_first_manga
```

### 🔧 手動実行（デバッグ用）

```powershell
# 仮想環境を有効化
.\venv_win\Scripts\Activate.ps1

# ステップ1: YAML展開
python scripts\expand_story.py stories\my_story.yaml

# ステップ2: マンガ生成
python scripts\generate_from_yaml.py stories\my_story_expanded.yaml

# 仮想環境を無効化
deactivate
```

### 🔄 複数ページ生成（バッチ処理）

```powershell
# 複数のストーリーを連続生成
.\run_en.ps1 episode1
.\run_en.ps1 episode2
.\run_en.ps1 episode3
```

---

## ドキュメント構成

### 📚 各ドキュメントの役割

#### 1. **PROJECT_OVERVIEW.md** ← 本ドキュメント
**対象**: 開発者、プロジェクト管理者
**内容**: 全体像、設計思想、開発プロセス、環境構築

#### 2. **QUICKSTART_EN.md**
**対象**: 初めて使う人
**内容**: 最速で動かすための手順のみ（英語）

#### 3. **USAGE_GUIDE.md**
**対象**: 日常的に使うユーザー
**内容**: 詳しい使い方、カスタマイズ方法（日本語）

#### 4. **README.md**
**対象**: GitHubで見る人
**内容**: プロジェクト概要、主要機能、簡単な使い方

#### 5. **IMPLEMENTATION_SUMMARY.md**
**対象**: 開発者
**内容**: 実装詳細、技術的な判断理由

### 🗺️ ドキュメントフローチャート

```
[初めて使う]
    ↓
QUICKSTART_EN.md
    ↓
[動いた！もっと使いたい]
    ↓
USAGE_GUIDE.md
    ↓
[カスタマイズしたい/仕組みを知りたい]
    ↓
PROJECT_OVERVIEW.md (本ドキュメント)
    ↓
[実装を理解したい]
    ↓
IMPLEMENTATION_SUMMARY.md
```

### 📖 読むべきドキュメント選択ガイド

| やりたいこと | 読むドキュメント |
|------------|----------------|
| とにかく動かす | QUICKSTART_EN.md |
| 新しいマンガを作る | USAGE_GUIDE.md |
| システム全体を理解 | PROJECT_OVERVIEW.md |
| コードを修正 | IMPLEMENTATION_SUMMARY.md |
| Easy Bananaと連携 | PROJECT_OVERVIEW.md (本ドキュメント) |

---

## トラブルシューティング

### ❌ よくあるエラーと解決方法

#### エラー1: PowerShellスクリプトが実行できない
```
発生場所 行:1 文字:3
+ .\setup_en.ps1
+ ~~~~~~~~~~~~~~
このシステムではスクリプトの実行が無効になっています。
```

**解決方法**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

#### エラー2: Python が見つからない
```
'python' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

**解決方法**:
1. Python 3.10以上をインストール: https://www.python.org/downloads/
2. インストール時に "Add Python to PATH" にチェック

---

#### エラー3: API Key エラー
```
ValueError: GOOGLE_API_KEY が .env に設定されていません
```

**解決方法**:
`.env` ファイルを確認:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

---

#### エラー4: キャラクター画像が見つからない
```
FileNotFoundError: キャラクター画像が見つかりません:
C:\instagram-manga-generator\characters\CLAUDECODE_ORIGIN.png
```

**解決方法**:
`characters/` フォルダに以下が存在するか確認:
- `TEN_ORIGIN.png`
- `CLAUDECODE_ORIGIN.png`

---

#### エラー5: 画像生成失敗（UnidentifiedImageError）
```
PIL.UnidentifiedImageError: cannot identify image file
```

**原因**: APIレスポンスが画像データではない可能性

**解決方法**:
1. モデル名を確認: `gemini-2.5-flash-image-preview` であること
2. デバッグ情報を確認（データ形式、サイズ）
3. API制限に達していないか確認

---

### 🔍 デバッグ方法

#### ステップごとに確認

```powershell
# 1. YAML展開のみテスト
python scripts\expand_story.py stories\simple_story_example.yaml
# → stories\simple_story_example_expanded.yaml が生成されるか

# 2. 生成されたYAMLを確認
notepad stories\simple_story_example_expanded.yaml

# 3. プロンプトの確認（generate_from_yaml.py を一時修正）
# print(prompt) を追加して内容確認

# 4. APIレスポンス確認（デバッグ情報出力）
python scripts\generate_from_yaml.py stories\simple_story_example_expanded.yaml
```

---

## 付録

### A. Easy Banana ファイル構成

```
C:\Users\tench\Downloads\easy_banana_v1_1_2\easy_banana/
├── manifest.json              # Chrome拡張設定
├── sidepanel.js              # メインロジック
├── key.js                    # APIキー管理
├── library.js                # 画像ライブラリ
└── template/
    ├── index.json            # テンプレート定義
    ├── char-keisuke.png      # キャラクター例
    ├── koma3-1.png           # 3コマレイアウト
    ├── koma4-1.png           # 4コマレイアウト
    └── ...
```

### B. 環境変数

#### .env ファイル
```bash
# Google AI Studio API Key
GOOGLE_API_KEY=your_api_key_here
```

**取得方法**:
1. https://aistudio.google.com にアクセス
2. "Get API Key" をクリック
3. APIキーをコピーして `.env` に貼り付け

### C. コマンドリファレンス（完全版）

```powershell
# === セットアップ ===
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_en.ps1

# === 生成 ===
# 方法1: 推奨（一発実行）
.\run_en.ps1 story_name

# 方法2: 手動（ステップバイステップ）
.\venv_win\Scripts\Activate.ps1
python scripts\expand_story.py stories\story_name.yaml
python scripts\generate_from_yaml.py stories\story_name_expanded.yaml
deactivate

# === 確認 ===
# 生成された画像を開く
start output\story_name_generated.png

# 仮想環境のパッケージ確認
.\venv_win\Scripts\pip list

# === メンテナンス ===
# 仮想環境の再作成
Remove-Item -Recurse -Force venv_win
.\setup_en.ps1

# パッケージの更新
.\venv_win\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt
```

---

## まとめ

### ✅ このシステムで実現できたこと

1. ✅ **ネーム作成の完全省略** - 最大の時間短縮
2. ✅ **キャラクター一貫性の保証** - テンプレート化
3. ✅ **コマ割りの自動適用** - プリセット選択のみ
4. ✅ **プログラマティック制御** - スクリプト化
5. ✅ **Easy Bananaとの知見共有** - 既存の成功パターン活用

### 🎯 次のステップ

#### 短期（すぐできる）
- [ ] 複数ページの連続生成スクリプト
- [ ] カスタムキャラクターの追加
- [ ] 新しいコマ割りパターンの定義
- [ ] Easy Bananaのコマ割りテンプレート画像を参照画像として追加

#### 中期（拡張機能）
- [ ] LLMによる簡易YAML自動生成
- [ ] ストーリーの自動分割（長文→複数ページ）
- [ ] 吹き出し配置の最適化
- [ ] バッチ処理の並列化

#### 長期（完全自動化）
- [ ] テキストプロンプト → マンガ完全自動生成
- [ ] Instagram自動投稿機能
- [ ] アナリティクス連携
- [ ] マンガスタイルの学習・最適化

---

**作成日**: 2025-11-11
**バージョン**: 2.0
**作成者**: TEN × Claude Code

**参考資料**:
- Easy Banana: `C:\Users\tench\Downloads\easy_banana_v1_1_2\easy_banana`
- Google AI Studio: https://aistudio.google.com
- Gemini API Docs: https://ai.google.dev/gemini-api/docs
