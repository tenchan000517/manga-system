# 🚀 クイックスタートガイド

## 最速でマンガを生成する

### ステップ1: セットアップ（初回のみ）

Windowsのコマンドプロンプトを開いて：

```bash
cd C:\instagram-manga-generator
setup.bat
```

または手動で：

```bash
pip install -r requirements.txt
```

### ステップ2: 環境テスト

```bash
cd scripts
python test_setup.py
```

すべて ✓ になっていればOK！

### ステップ3: マンガを生成！

```bash
python generate_manga.py ../stories/episode1.yaml
```

または、ルートディレクトリから：

```bash
generate.bat episode1
```

### ステップ4: 結果を確認

`output/` フォルダを開いて、生成されたマンガをチェック！

```
output/
├── AIマンガシステム誕生秘話_#1_page1.png
├── AIマンガシステム誕生秘話_#1_page2.png
└── AIマンガシステム誕生秘話_#1_page3.png
```

---

## 🎨 新しいストーリーを作る

### 1. YAMLファイルを作成

`stories/episode2.yaml`:

```yaml
title: "新しいエピソード"
pages:
  - page: 1
    panels:
      - panel: 1
        character: user
        prompt: "TENがコーヒーを飲みながらコードを書いている"
        dialogue: "今日は新機能を実装するぞ"

      - panel: 2
        character: claude
        expression: "提案"
        prompt: "Claude Codeが画面に現れる"
        dialogue: "テスト駆動開発でいきましょう！"

      # ... 残りのパネル
```

### 2. 生成

```bash
generate.bat episode2
```

---

## 💡 Tips

### キャラクターの指定

- `character: user` → TEN（エンジニア）
- `character: claude` → Claude Code（AIアシスタント）

### プロンプトのコツ

**良い例**:
```yaml
prompt: "TENがパソコンの前で驚いた表情。画面には大量のエラーメッセージが表示されている。背景は暗めのオフィス"
```

**悪い例**:
```yaml
prompt: "驚く"  # 具体性が足りない
```

### 生成時間の目安

- 1パネル: 10-20秒
- 4パネル（1ページ）: 約1分
- 3ページ: 約3分

---

## ⚠️ よくある問題と解決法

### 「モジュールが見つかりません」エラー

```bash
pip install [モジュール名]
```

### API接続エラー

1. インターネット接続を確認
2. `.env` のAPIキーを確認
3. Google AI Studioのステータスを確認

### 生成が遅い

- レート制限の可能性（少し待つ）
- 1日の無料枠を使い切った可能性

---

## 📱 Instagramに投稿

### フィード投稿の場合

1. `output/` から画像を選択
2. Instagramアプリで「複数選択」
3. 順番に投稿（スワイプ可能）

### サイズ

- 既に最適サイズ（1080×1350px）で生成済み
- そのまま投稿OK！

---

## 🎯 次のステップ

1. **第1話を見る**: `output/` フォルダを開く
2. **第2話を作る**: `stories/episode2.yaml` を作成
3. **カスタマイズ**: プロンプトを調整して好みのスタイルを探す
4. **Instagramに投稿**: フォロワーを増やそう！

---

楽しんでください！ 🎨✨
