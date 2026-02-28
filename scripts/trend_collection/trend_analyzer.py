#!/usr/bin/env python3
"""
トレンド分析スクリプト
収集したタイトルから固有名詞の頻度を分析し、文脈を抽出する
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Tuple
from collections import Counter, defaultdict

# 対象の固有名詞（LLM、AI関連）
TARGET_KEYWORDS = [
    # Claude系
    "Claude Code",
    "Claude",
    "Anthropic",

    # OpenAI系
    "ChatGPT",
    "GPT-4",
    "GPT-5",
    "GPT6",
    "GPT",
    "OpenAI",
    "Sora",

    # Google系
    "Gemini",
    "Bard",
    "Google AI",
    "Veo3",
    "Veo",

    # Microsoft系
    "Copilot",
    "Bing AI",

    # その他
    "Suno",
    "Midjourney",
    "Stable Diffusion",
    "Runway",
    "Pika",

    # 汎用
    "AI",
    "人工知能",
    "LLM",
    "エージェント",
    "生成AI"
]

# 文脈パターン（どのように紹介されているか）
CONTEXT_PATTERNS = [
    # リリース・アップデート系
    (r'(.{0,20})(リリース|発表|登場|公開|アップデート)(.{0,20})', 'リリース・アップデート'),
    (r'(.{0,20})(出る|来た|キタ)(!|！|？|\?)', '速報・噂'),

    # 使い方・Tips系
    (r'(.{0,20})(使い方|方法|やり方|活用|テクニック)(.{0,20})', '使い方・Tips'),
    (r'(.{0,20})(便利|すごい|最強|神)(.{0,20})', '評価・レビュー'),

    # 比較系
    (r'(.{0,20})(vs|比較|違い)(.{0,20})', '比較'),

    # 問題・注意系
    (r'(.{0,20})(危険|注意|問題|ヤバい)(.{0,20})', '問題・注意'),

    # その他
    (r'(.{0,20})(裏技|秘密|知らない|初心者)(.{0,20})', 'ハウツー'),
]


class TrendAnalyzer:
    """トレンド分析クラス"""

    def __init__(self, data_dir: str = 'ideas/trend_data'):
        """
        Args:
            data_dir: 生データが保存されているディレクトリ
        """
        self.data_dir = data_dir
        self.posts = []

    def load_latest_data(self):
        """最新の収集データを読み込む"""
        today = datetime.now().strftime('%Y-%m-%d')

        youtube_file = os.path.join(self.data_dir, f'youtube_{today}.json')
        instagram_file = os.path.join(self.data_dir, f'instagram_{today}.json')

        for filepath in [youtube_file, instagram_file]:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.posts.extend(data.get('posts', []))
                    print(f'Loaded: {filepath} ({len(data.get("posts", []))} posts)')

        print(f'Total posts loaded: {len(self.posts)}')

    def extract_keywords(self) -> Counter:
        """
        タイトルから固有名詞を抽出し、出現頻度をカウント

        Returns:
            Counter: キーワードと出現回数
        """
        keyword_counter = Counter()

        for post in self.posts:
            title = post.get('title', '')

            # 各キーワードの出現をチェック
            for keyword in TARGET_KEYWORDS:
                # 大文字小文字を区別しない検索
                if re.search(re.escape(keyword), title, re.IGNORECASE):
                    keyword_counter[keyword] += 1

        return keyword_counter

    def extract_contexts(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        キーワードごとの文脈を抽出

        Returns:
            Dict: {キーワード: [(タイトル, 文脈カテゴリ), ...]}
        """
        keyword_contexts = defaultdict(list)

        for post in self.posts:
            title = post.get('title', '')

            # キーワードを検出
            detected_keywords = []
            for keyword in TARGET_KEYWORDS:
                if re.search(re.escape(keyword), title, re.IGNORECASE):
                    detected_keywords.append(keyword)

            # 文脈パターンをマッチング
            for keyword in detected_keywords:
                context_category = 'その他'

                for pattern, category in CONTEXT_PATTERNS:
                    if re.search(pattern, title):
                        context_category = category
                        break

                keyword_contexts[keyword].append((title, context_category))

        return keyword_contexts

    def analyze(self) -> Dict:
        """
        トレンド分析を実行

        Returns:
            分析結果の辞書
        """
        keyword_freq = self.extract_keywords()
        keyword_contexts = self.extract_contexts()

        # ランキング作成
        ranking = []
        for keyword, count in keyword_freq.most_common(20):
            contexts = keyword_contexts.get(keyword, [])

            # 文脈カテゴリごとに集計
            context_summary = Counter([ctx[1] for ctx in contexts])

            # サンプルタイトル（最大5件）
            sample_titles = [ctx[0] for ctx in contexts[:5]]

            ranking.append({
                'keyword': keyword,
                'count': count,
                'contexts': dict(context_summary),
                'sample_titles': sample_titles
            })

        return {
            'analyzed_at': datetime.now().isoformat(),
            'total_posts': len(self.posts),
            'ranking': ranking
        }


def save_analysis(analysis: Dict, output_dir: str = 'ideas/trend_analysis'):
    """
    分析結果を保存

    Args:
        analysis: 分析結果
        output_dir: 保存先ディレクトリ
    """
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime('%Y-%m-%d')

    # JSON形式で保存
    json_file = os.path.join(output_dir, f'analysis_{today}.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    # Markdown形式でも保存（読みやすい）
    md_file = os.path.join(output_dir, f'analysis_{today}.md')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f'# トレンド分析 - {today}\n\n')
        f.write(f'分析日時: {analysis["analyzed_at"]}\n')
        f.write(f'総投稿数: {analysis["total_posts"]}\n\n')

        f.write('## 固有名詞ランキング\n\n')

        for i, item in enumerate(analysis['ranking'], 1):
            stars = '⭐' * min(5, item['count'] // 5)  # 5回ごとに⭐1つ
            f.write(f'### {i}. {item["keyword"]} - {item["count"]}回 {stars}\n\n')

            # 文脈カテゴリ
            if item['contexts']:
                f.write('**主な文脈:**\n')
                for ctx, cnt in sorted(item['contexts'].items(), key=lambda x: x[1], reverse=True):
                    f.write(f'- {ctx}: {cnt}回\n')
                f.write('\n')

            # サンプルタイトル
            f.write('**サンプルタイトル:**\n')
            for title in item['sample_titles']:
                f.write(f'- {title}\n')

            # ピックアップ候補の星
            if item['count'] >= 20:
                f.write('\n**ピックアップ候補:** ⭐⭐⭐⭐⭐ 超おすすめ！\n')
            elif item['count'] >= 10:
                f.write('\n**ピックアップ候補:** ⭐⭐⭐ おすすめ\n')

            f.write('\n---\n\n')

    print(f'\nAnalysis saved to:')
    print(f'  JSON: {json_file}')
    print(f'  Markdown: {md_file}')


def main():
    """メイン処理"""
    print('Starting trend analysis...\n')

    analyzer = TrendAnalyzer()
    analyzer.load_latest_data()

    if not analyzer.posts:
        print('No data found. Please run scraping scripts first.')
        return

    analysis = analyzer.analyze()
    save_analysis(analysis)

    print('\nDone!')
    print(f'\nTop 5 keywords:')
    for i, item in enumerate(analysis['ranking'][:5], 1):
        print(f"  {i}. {item['keyword']} - {item['count']}回")


if __name__ == '__main__':
    main()
