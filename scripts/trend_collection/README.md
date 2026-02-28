# トレンド収集システム

YouTube Shorts と Instagram から AI 関連のトレンドを収集・分析し、マンガのネタとして活用するシステム。

## フロー

### フェーズ1: スクレイピング
YouTube Shorts と Instagram から AI 関連タイトルを収集。

### フェーズ2: トレンド分析
- 固有名詞（Claude Code、ChatGPT、Sora、Veo3、Suno など）の出現頻度を特定
- 「どのように」紹介されているか（文脈）を抽出

### フェーズ3: 深掘り & ストーリー化
- ピックアップしたネタを WebSearch で深掘り
- ストーリーに落とし込む（Claude Code が補助）

## ディレクトリ構造

```
scripts/trend_collection/
  ├── collect_trends.py          # メインスクリプト（全フェーズ統合）
  ├── youtube_scraper.py         # YouTube Shorts スクレイピング
  ├── instagram_scraper.py       # Instagram スクレイピング
  ├── trend_analyzer.py          # トレンド分析
  └── README.md                  # このファイル

ideas/trend_data/                # 生データ保存
  ├── youtube_YYYY-MM-DD.json
  └── instagram_YYYY-MM-DD.json

ideas/trend_analysis/            # 分析結果保存
  └── analysis_YYYY-MM-DD.md
```

## データ形式

### 生データ（JSON）

```json
{
  "collected_at": "2025-11-13T10:00:00",
  "source": "youtube_shorts",
  "posts": [
    {
      "title": "GPT6が出る？！",
      "url": "https://youtube.com/shorts/xxxxx",
      "published_at": "2025-11-12",
      "view_count": 50000,
      "detected_keywords": ["GPT6"],
      "context": "新バージョンリリースの噂"
    }
  ]
}
```

### 分析結果（Markdown）

```markdown
# トレンド分析 - 2025-11-13

## 固有名詞ランキング

1. Claude Code - 45回
2. ChatGPT - 38回
3. GPT6 - 25回
...

## 注目トピック

### GPT6リリース噂
- 出現頻度: 25回
- 主な文脈: 「GPT6が出る？！」「GPT6の新機能予想」
- ピックアップ候補: ⭐⭐⭐

### Claude Code活用術
- 出現頻度: 45回
- 主な文脈: 「Claude Codeで〇〇する方法」「Claude Code便利すぎ」
- ピックアップ候補: ⭐⭐⭐⭐⭐
```

## 使い方

### 1. 環境設定

```bash
# 必要なパッケージをインストール
pip install google-api-python-client instaloader python-dotenv

# .env ファイルに API キーを設定
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 2. トレンド収集

```bash
# 全フェーズを実行（スクレイピング → 分析 → 結果保存）
python scripts/trend_collection/collect_trends.py
```

### 3. 分析結果確認

```bash
# 最新の分析結果を確認
cat ideas/trend_analysis/analysis_$(date +%Y-%m-%d).md
```

### 4. ネタ選定 & 深掘り

Claude Code に「トレンド分析からネタを選んで深掘りして」と依頼。

## 対象キーワード

以下のキーワードを含むタイトルを収集：
- Claude Code
- Claude
- ChatGPT
- GPT (GPT-4, GPT-5, GPT6 など)
- Sora
- Veo3
- Suno
- Gemini
- Copilot
- AI
- 人工知能
- LLM
- エージェント

## 注意事項

- YouTube API には1日あたりのクォータ制限があります
- Instagram スクレイピングは利用規約に注意
- 収集データは個人利用目的に限定してください
