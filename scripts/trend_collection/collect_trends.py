#!/usr/bin/env python3
"""
トレンド収集 統合スクリプト
フェーズ1-2を一括実行: スクレイピング → 分析 → 結果保存
"""

import sys
import argparse
from pathlib import Path

# サブモジュールをインポート
try:
    from youtube_scraper import YouTubeScraper, save_results as save_youtube
    from instagram_scraper import InstagramScraper, save_results as save_instagram
    from trend_analyzer import TrendAnalyzer, save_analysis
except ImportError:
    # スクリプトの場所をパスに追加
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))

    from youtube_scraper import YouTubeScraper, save_results as save_youtube
    from instagram_scraper import InstagramScraper, save_results as save_instagram
    from trend_analyzer import TrendAnalyzer, save_analysis

import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()


def run_phase1_scraping(skip_youtube: bool = False, skip_instagram: bool = False):
    """
    フェーズ1: スクレイピング

    Args:
        skip_youtube: YouTube スクレイピングをスキップ
        skip_instagram: Instagram スクレイピングをスキップ
    """
    print('=' * 60)
    print('フェーズ1: スクレイピング')
    print('=' * 60)
    print()

    # YouTube
    if not skip_youtube:
        api_key = os.getenv('YOUTUBE_API_KEY')

        if api_key:
            print('[1/2] YouTube Shorts を収集中...\n')
            try:
                scraper = YouTubeScraper(api_key)
                videos = scraper.collect_all_keywords(max_results_per_keyword=30)
                save_youtube(videos)
                print('\n✓ YouTube 収集完了\n')
            except Exception as e:
                print(f'✗ YouTube 収集エラー: {e}\n')
        else:
            print('[1/2] YouTube スキップ (YOUTUBE_API_KEY が設定されていません)\n')
    else:
        print('[1/2] YouTube スキップ (--skip-youtube 指定)\n')

    # Instagram
    if not skip_instagram:
        print('[2/2] Instagram を収集中...\n')
        try:
            scraper = InstagramScraper()
            posts = scraper.collect_all_hashtags(max_posts_per_tag=20)
            save_instagram(posts)
            print('\n✓ Instagram 収集完了\n')
        except Exception as e:
            print(f'✗ Instagram 収集エラー: {e}\n')
    else:
        print('[2/2] Instagram スキップ (--skip-instagram 指定)\n')


def run_phase2_analysis():
    """フェーズ2: トレンド分析"""
    print('=' * 60)
    print('フェーズ2: トレンド分析')
    print('=' * 60)
    print()

    analyzer = TrendAnalyzer()
    analyzer.load_latest_data()

    if not analyzer.posts:
        print('✗ データが見つかりません。先にスクレイピングを実行してください。')
        return

    print('\n分析中...\n')
    analysis = analyzer.analyze()
    save_analysis(analysis)

    print('\n✓ 分析完了\n')

    # トップ10を表示
    print('=' * 60)
    print('トップ10キーワード')
    print('=' * 60)
    for i, item in enumerate(analysis['ranking'][:10], 1):
        stars = '⭐' * min(5, item['count'] // 5)
        print(f"{i:2}. {item['keyword']:20} - {item['count']:3}回 {stars}")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='YouTube と Instagram からトレンドを収集・分析'
    )
    parser.add_argument(
        '--skip-youtube',
        action='store_true',
        help='YouTube のスクレイピングをスキップ'
    )
    parser.add_argument(
        '--skip-instagram',
        action='store_true',
        help='Instagram のスクレイピングをスキップ'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='分析のみ実行（スクレイピングはスキップ）'
    )

    args = parser.parse_args()

    print('\n')
    print('╔' + '=' * 58 + '╗')
    print('║' + ' ' * 15 + 'トレンド収集システム' + ' ' * 23 + '║')
    print('╚' + '=' * 58 + '╝')
    print()

    # フェーズ1: スクレイピング
    if not args.analyze_only:
        run_phase1_scraping(
            skip_youtube=args.skip_youtube,
            skip_instagram=args.skip_instagram
        )
    else:
        print('フェーズ1をスキップ (--analyze-only 指定)\n')

    # フェーズ2: 分析
    run_phase2_analysis()

    print('\n')
    print('=' * 60)
    print('完了！')
    print('=' * 60)
    print()
    print('📊 分析結果: ideas/trend_analysis/analysis_YYYY-MM-DD.md')
    print('💡 次のステップ: Claude Code に「トレンド分析からネタをピックアップ」と依頼')
    print()


if __name__ == '__main__':
    main()
