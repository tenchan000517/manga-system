"""
Instagram用マンガ自動生成スクリプト

使い方:
    python generate_manga.py stories/episode1.yaml
"""
import sys
import yaml
from pathlib import Path
from PIL import Image
import time
from utils import (
    init_gemini,
    load_character_image,
    save_image,
    combine_panels_vertical,
    ensure_directories,
    PROJECT_ROOT,
    TEMP_DIR
)

def load_story(yaml_path):
    """YAMLファイルからストーリーを読み込む"""
    # パスを解決
    story_path = Path(yaml_path)

    # 相対パスの場合は絶対パスに変換
    if not story_path.is_absolute():
        story_path = story_path.resolve()

    if not story_path.exists():
        raise FileNotFoundError(f"ストーリーファイルが見つかりません: {story_path}")

    with open(story_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_panel(model, panel_data, character_images):
    """1つのパネル（コマ）を生成"""
    character = panel_data.get('character', 'user')
    prompt = panel_data.get('prompt', '')
    dialogue = panel_data.get('dialogue', '')

    # キャラクター画像を取得
    if character == 'user':
        char_img = character_images['TEN']
    elif character == 'claude':
        char_img = character_images['CLAUDECODE']
    else:
        char_img = character_images.get(character.upper())

    # プロンプトにセリフを追加
    full_prompt = f"""
マンガのコマを1つ生成してください。

シーン: {prompt}

セリフ: "{dialogue}"

要件:
- カラーイラスト、マンガスタイル
- 背景はシンプルで読みやすく
- セリフは吹き出しに入れてください
- 1コマ完結の構図
"""

    print(f"  プロンプト: {prompt[:50]}...")

    try:
        # Nano Banana APIでコマ生成
        print(f"  🎨 Nano Banana APIを呼び出し中...")
        response = model.generate_content([
            char_img,
            full_prompt
        ])

        print(f"  📡 レスポンス受信: {type(response)}")

        # レスポンスの詳細をデバッグ表示
        if hasattr(response, 'candidates') and response.candidates:
            print(f"  ✓ Candidates: {len(response.candidates)}")
            candidate = response.candidates[0]

            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for i, part in enumerate(candidate.content.parts):
                    print(f"  Part {i}: {type(part)}")
                    if hasattr(part, 'inline_data'):
                        print(f"  ✓ 画像データ発見！")
                        import base64
                        from io import BytesIO
                        image_data = base64.b64decode(part.inline_data.data)
                        return Image.open(BytesIO(image_data))
                    elif hasattr(part, 'text'):
                        print(f"  テキストレスポンス: {part.text[:100]}")

        # 古いAPI形式も試す
        if hasattr(response, '_result') and hasattr(response._result, 'candidates'):
            for part in response._result.candidates[0].content.parts:
                if hasattr(part, 'inline_data'):
                    import base64
                    from io import BytesIO
                    image_data = base64.b64decode(part.inline_data.data)
                    return Image.open(BytesIO(image_data))

        print("  ⚠ 画像生成に失敗しました。レスポンス形式が想定外です。")
        print(f"  デバッグ: {dir(response)}")
        return create_dummy_panel(dialogue)

    except Exception as e:
        print(f"  ✗ API エラー: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return create_dummy_panel(dialogue)

def create_dummy_panel(text=""):
    """ダミーパネルを作成（テスト用）"""
    from PIL import ImageDraw, ImageFont
    img = Image.new('RGB', (1080, 337), color='lightgray')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        font = ImageFont.load_default()

    draw.text((50, 150), f"[生成中...]\n{text[:50]}", fill='black', font=font)
    return img

def generate_page(model, page_data, character_images, page_num):
    """1ページ分（4コマ）を生成"""
    print(f"\n📄 ページ {page_num} 生成中...")

    panels = page_data.get('panels', [])
    if not panels:
        print("  ⚠ パネルが定義されていません")
        return None

    panel_images = []

    for i, panel_data in enumerate(panels, 1):
        print(f"  コマ {i}/{len(panels)} 生成中...")
        panel_img = generate_panel(model, panel_data, character_images)
        panel_images.append(panel_img)

        # レート制限対策（少し待つ）
        if i < len(panels):
            time.sleep(2)

    # パネルを縦に結合
    combined = combine_panels_vertical(panel_images)
    return combined

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使い方: python generate_manga.py stories/episode1.yaml")
        sys.exit(1)

    story_file = sys.argv[1]

    print("=" * 60)
    print("  Instagram用マンガ自動生成")
    print("=" * 60)

    # ディレクトリ確認
    ensure_directories()

    # ストーリー読み込み
    print(f"\n📖 ストーリー読み込み: {story_file}")
    story = load_story(story_file)
    title = story.get('title', 'Untitled')
    print(f"   タイトル: {title}")

    # Gemini API初期化
    print("\n🤖 Gemini API 初期化中...")
    model = init_gemini()
    print("   ✓ 完了")

    # キャラクター画像読み込み
    print("\n👤 キャラクター画像読み込み中...")
    character_images = {
        'TEN': load_character_image('TEN'),
        'CLAUDECODE': load_character_image('CLAUDECODE')
    }
    print("   ✓ 完了")

    # 各ページを生成
    pages = story.get('pages', [])
    print(f"\n🎨 全 {len(pages)} ページを生成します...")

    for page_data in pages:
        page_num = page_data.get('page', 1)
        page_img = generate_page(model, page_data, character_images, page_num)

        if page_img:
            # 保存
            filename = f"{title.replace(' ', '_')}_page{page_num}.png"
            save_image(page_img, filename)

    print("\n" + "=" * 60)
    print("  ✓ マンガ生成完了！")
    print(f"  出力先: {PROJECT_ROOT / 'output'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
