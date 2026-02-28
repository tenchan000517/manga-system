#!/usr/bin/env python3
"""
YouTube Shorts スクレイピングスクリプト
AI関連のショート動画タイトルを収集する
"""

import os
import json
from datetime import datetime
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# 対象キーワード
TARGET_KEYWORDS = [
    "Claude Code",
    "Claude",
    "ChatGPT",
    "GPT",
    "GPT-4",
    "GPT-5",
    "GPT6",
    "Sora",
    "Veo3",
    "Suno",
    "Gemini",
    "Copilot",
    "AI",
    "人工知能",
    "LLM",
    "エージェント"
]


class YouTubeScraper:
    """YouTube Shorts のタイトルを収集するクラス"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: YouTube Data API v3 の API キー
        """
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def search_shorts(self, keyword: str, max_results: int = 50) -> List[Dict]:
        """
        指定キーワードでショート動画を検索

        Args:
            keyword: 検索キーワード
            max_results: 取得する最大件数

        Returns:
            動画情報のリスト
        """
        try:
            # Shorts は通常60秒以下の動画
            request = self.youtube.search().list(
                part='snippet',
                q=keyword,
                type='video',
                videoDuration='short',  # 4分以下の動画
                order='viewCount',  # 視聴回数順
                maxResults=max_results,
                relevanceLanguage='ja'  # 日本語優先
            )

            response = request.execute()

            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']

                # 動画の詳細情報を取得（視聴回数など）
                video_details = self._get_video_details(video_id)

                videos.append({
                    'title': snippet['title'],
                    'url': f'https://youtube.com/shorts/{video_id}',
                    'published_at': snippet['publishedAt'],
                    'channel_title': snippet['channelTitle'],
                    'view_count': video_details.get('view_count', 0),
                    'like_count': video_details.get('like_count', 0),
                    'comment_count': video_details.get('comment_count', 0),
                    'detected_keywords': [keyword]
                })

            return videos

        except HttpError as e:
            print(f'YouTube API Error: {e}')
            return []

    def _get_video_details(self, video_id: str) -> Dict:
        """
        動画の詳細情報を取得

        Args:
            video_id: 動画ID

        Returns:
            詳細情報の辞書
        """
        try:
            request = self.youtube.videos().list(
                part='statistics',
                id=video_id
            )

            response = request.execute()

            if response.get('items'):
                stats = response['items'][0]['statistics']
                return {
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0))
                }

            return {}

        except HttpError:
            return {}

    def collect_all_keywords(self, max_results_per_keyword: int = 30) -> List[Dict]:
        """
        すべてのターゲットキーワードで検索を実行

        Args:
            max_results_per_keyword: キーワードごとの最大取得件数

        Returns:
            すべての動画情報
        """
        all_videos = []

        for keyword in TARGET_KEYWORDS:
            print(f'Searching for: {keyword}')
            videos = self.search_shorts(keyword, max_results_per_keyword)
            all_videos.extend(videos)
            print(f'  Found: {len(videos)} videos')

        # 重複を削除（URLでユニーク化）
        unique_videos = []
        seen_urls = set()

        for video in all_videos:
            if video['url'] not in seen_urls:
                unique_videos.append(video)
                seen_urls.add(video['url'])

        print(f'\nTotal unique videos: {len(unique_videos)}')
        return unique_videos


def save_results(videos: List[Dict], output_dir: str = 'ideas/trend_data'):
    """
    結果をJSONファイルに保存

    Args:
        videos: 動画情報のリスト
        output_dir: 保存先ディレクトリ
    """
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.join(output_dir, f'youtube_{today}.json')

    data = {
        'collected_at': datetime.now().isoformat(),
        'source': 'youtube_shorts',
        'total_count': len(videos),
        'posts': videos
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'\nResults saved to: {filename}')


def main():
    """メイン処理"""
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key:
        print('Error: YOUTUBE_API_KEY not found in environment variables')
        print('Please create a .env file with your YouTube API key:')
        print('  YOUTUBE_API_KEY=your_api_key_here')
        return

    print('Starting YouTube Shorts scraping...\n')

    scraper = YouTubeScraper(api_key)
    videos = scraper.collect_all_keywords(max_results_per_keyword=30)

    save_results(videos)

    print('\nDone!')


if __name__ == '__main__':
    main()
