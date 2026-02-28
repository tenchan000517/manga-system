#!/usr/bin/env python3
"""
Instagram スクレイピングスクリプト
AI関連のReels/投稿タイトルを収集する
"""

import os
import json
from datetime import datetime
from typing import List, Dict
import instaloader
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# 対象ハッシュタグ
TARGET_HASHTAGS = [
    "claudecode",
    "claude",
    "chatgpt",
    "gpt",
    "sora",
    "veo3",
    "suno",
    "gemini",
    "copilot",
    "ai",
    "人工知能",
    "llm",
    "エージェント",
    "生成ai",
    "aiツール"
]


class InstagramScraper:
    """Instagram の投稿タイトルを収集するクラス"""

    def __init__(self):
        """初期化"""
        self.loader = instaloader.Instaloader()

        # ログインが必要な場合（オプション）
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')

        if username and password:
            try:
                self.loader.login(username, password)
                print('Instagram login successful')
            except Exception as e:
                print(f'Instagram login failed: {e}')
                print('Continuing without login (limited access)')

    def search_hashtag(self, hashtag: str, max_posts: int = 30) -> List[Dict]:
        """
        指定ハッシュタグで投稿を検索

        Args:
            hashtag: ハッシュタグ（# なし）
            max_posts: 取得する最大投稿数

        Returns:
            投稿情報のリスト
        """
        posts = []

        try:
            hashtag_obj = instaloader.Hashtag.from_name(
                self.loader.context,
                hashtag
            )

            print(f'Searching #{hashtag}...')

            for i, post in enumerate(hashtag_obj.get_posts()):
                if i >= max_posts:
                    break

                # Reels または通常投稿のキャプションを取得
                caption = post.caption or ""

                # タイトル的な部分を抽出（最初の行または最初の100文字）
                title = caption.split('\n')[0][:100] if caption else "No caption"

                posts.append({
                    'title': title,
                    'url': f'https://www.instagram.com/p/{post.shortcode}/',
                    'published_at': post.date_utc.isoformat(),
                    'likes': post.likes,
                    'comments': post.comments,
                    'is_video': post.is_video,
                    'detected_keywords': [hashtag]
                })

        except Exception as e:
            print(f'Error searching #{hashtag}: {e}')

        return posts

    def collect_all_hashtags(self, max_posts_per_tag: int = 20) -> List[Dict]:
        """
        すべてのターゲットハッシュタグで検索を実行

        Args:
            max_posts_per_tag: ハッシュタグごとの最大取得件数

        Returns:
            すべての投稿情報
        """
        all_posts = []

        for hashtag in TARGET_HASHTAGS:
            posts = self.search_hashtag(hashtag, max_posts_per_tag)
            all_posts.extend(posts)
            print(f'  Found: {len(posts)} posts')

        # 重複を削除（URLでユニーク化）
        unique_posts = []
        seen_urls = set()

        for post in all_posts:
            if post['url'] not in seen_urls:
                unique_posts.append(post)
                seen_urls.add(post['url'])

        print(f'\nTotal unique posts: {len(unique_posts)}')
        return unique_posts


def save_results(posts: List[Dict], output_dir: str = 'ideas/trend_data'):
    """
    結果をJSONファイルに保存

    Args:
        posts: 投稿情報のリスト
        output_dir: 保存先ディレクトリ
    """
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.join(output_dir, f'instagram_{today}.json')

    data = {
        'collected_at': datetime.now().isoformat(),
        'source': 'instagram',
        'total_count': len(posts),
        'posts': posts
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'\nResults saved to: {filename}')


def main():
    """メイン処理"""
    print('Starting Instagram scraping...\n')

    scraper = InstagramScraper()
    posts = scraper.collect_all_hashtags(max_posts_per_tag=20)

    save_results(posts)

    print('\nDone!')


if __name__ == '__main__':
    main()
