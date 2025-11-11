# Instagram Manga Generator - Web UI

完全YAML → 漫画生成のWebインターフェース。Vercelにデプロイして使用します。

## 📋 特徴

- ✅ ブラウザで完結（サーバー不要）
- ✅ 完全YAMLを貼り付けるだけ
- ✅ Gemini 2.5 Flash (Nanobanana) 使用
- ✅ APIキーはlocalStorageに保存（プライバシー保護）
- ✅ 静的サイトなのでVercelで無料デプロイ可能

## 🚀 デプロイ方法

### 1. Vercel CLIでデプロイ（推奨）

```bash
# Vercel CLIをインストール（初回のみ）
npm install -g vercel

# プロジェクトディレクトリに移動
cd instagram-manga-generator-ui

# デプロイ
vercel

# 本番環境にデプロイ
vercel --prod
```

### 2. Vercel Dashboardでデプロイ

1. GitHubリポジトリにプッシュ
2. [Vercel Dashboard](https://vercel.com/dashboard) にアクセス
3. "New Project" をクリック
4. リポジトリを選択してインポート
5. 自動的にデプロイが開始

## 📂 プロジェクト構成

```
instagram-manga-generator-ui/
├── index.html          # メインUI
├── style.css           # スタイリング
├── app.js              # ロジック（YAML解析、API呼び出し）
├── public/
│   └── characters/     # キャラクター画像
│       ├── TEN_ORIGIN.png
│       └── CLAUDECODE_ORIGIN.png
├── vercel.json         # Vercel設定
└── README.md           # このファイル
```

## 🔧 使い方

### Step 1: APIキーを設定

1. [Google AI Studio](https://aistudio.google.com) にアクセス
2. "Get API Key" をクリックしてAPIキーを取得
3. UIの「API設定」セクションにAPIキーを入力して「保存」
4. APIキーはブラウザのlocalStorageに保存されます（サーバーには送信されません）

### Step 2: YAMLを入力

1. 「完全YAML入力」セクションに展開済みのYAMLを貼り付け
2. または「サンプルを読み込む」ボタンで例を表示
3. YAMLが正しく解析されると「✓ 有効なYAML」と表示されます

### Step 3: 漫画を生成

1. 「漫画を生成」ボタンをクリック
2. 生成には数十秒かかる場合があります
3. 完成した漫画が表示されたら「ダウンロード」ボタンで保存

## 🔄 ワークフロー統合

このUIは、既存のPythonワークフローと併用できます：

```bash
# ローカルで簡易YAML → 完全YAML
cd /mnt/c/instagram-manga-generator
python scripts/expand_story.py stories/my_story.yaml

# 完全YAMLをコピー
cat stories/my_story_expanded.yaml

# Web UIに貼り付けて生成
# → ブラウザで https://your-app.vercel.app にアクセス
```

## 💡 技術スタック

- **フロントエンド**: HTML + CSS + Vanilla JavaScript
- **YAML解析**: [js-yaml](https://github.com/nodeca/js-yaml) (CDN)
- **API**: Google Generative AI API (Gemini 2.5 Flash)
- **デプロイ**: Vercel (静的サイト)

## 🐛 トラブルシューティング

### エラー: "APIキーが無効です"

- APIキーが正しく入力されているか確認
- Google AI Studioで新しいAPIキーを生成

### エラー: "キャラクター画像が見つかりません"

- `public/characters/` に以下が存在するか確認:
  - `TEN_ORIGIN.png`
  - `CLAUDECODE_ORIGIN.png`

### エラー: "画像が生成されませんでした"

- YAMLが正しい構造か確認
- API制限に達していないか確認
- ブラウザのコンソールでエラーを確認

### 画像が表示されない

- ブラウザのDevTools (F12) を開いてコンソールログを確認
- ネットワークタブでAPI呼び出しが成功しているか確認

## 🔐 セキュリティ

- APIキーはlocalStorageに保存され、サーバーには送信されません
- すべての処理はクライアント側で実行されます
- APIキーは暗号化されません（ブラウザのストレージに平文保存）
- 公共のPCで使用する場合は、使用後に「クリア」ボタンでAPIキーを削除してください

## 📝 ライセンス

このプロジェクトは個人使用を想定しています。

## 🙏 クレジット

- **Gemini API**: Google
- **Easy Banana**: 先輩エンジニア
- **開発**: TEN × Claude Code
