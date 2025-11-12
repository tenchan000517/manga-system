"""
構造化YAMLからNanobanana APIでマンガを生成

使い方:
    python generate_from_yaml.py ../stories/simple_story_example_expanded.yaml
"""
import sys
import io

# Windows環境でのUTF-8出力対応
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import yaml
import base64
import os
import argparse
from pathlib import Path
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
CHARACTERS_DIR = PROJECT_ROOT / "characters"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# .env読み込み
load_dotenv(PROJECT_ROOT / ".env")

def get_next_output_path(base_filename, session_folder=None):
    """年月/日付/ナンバリング形式で次の出力パスを生成

    優先順位:
    1. session_folder引数（コマンドラインから指定）
    2. 環境変数 MANGA_SESSION_ID
    3. 自動採番（既存フォルダの次の番号）

    例: output/2025-11/12/1/story_name_generated.png
        output/2025-11/12/2/another_story_generated.png
    """
    now = datetime.now()
    year_month = now.strftime("%Y-%m")  # 例: 2025-11
    day = now.strftime("%d")  # 例: 12

    # 年月/日付フォルダを作成
    date_dir = OUTPUT_DIR / year_month / day

    # セッションフォルダを決定（優先順位順）
    if session_folder is not None:
        # 1. コマンドライン引数
        folder_id = str(session_folder)
        output_folder = date_dir / folder_id
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)
    elif os.getenv('MANGA_SESSION_ID'):
        # 2. 環境変数
        folder_id = os.getenv('MANGA_SESSION_ID')
        output_folder = date_dir / folder_id
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=True)
    else:
        # 3. 自動採番
        if date_dir.exists():
            # 既存のナンバリングフォルダを取得（数字のみ）
            existing_numbers = []
            for item in date_dir.iterdir():
                if item.is_dir() and item.name.isdigit():
                    existing_numbers.append(int(item.name))

            # 次のナンバーを決定
            next_number = max(existing_numbers) + 1 if existing_numbers else 1
        else:
            next_number = 1

        output_folder = date_dir / str(next_number)
        output_folder.mkdir(parents=True, exist_ok=True)

    # 最終的なパス
    output_path = output_folder / base_filename
    return output_path

def load_yaml(filepath):
    """YAMLファイルを読み込む"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def image_to_base64(image_path):
    """画像をbase64エンコード"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def load_character_image(character_name):
    """キャラクター画像を読み込む"""
    # スペースを削除してファイル名を生成
    char_name_clean = character_name.upper().replace(" ", "")
    char_path = CHARACTERS_DIR / f"{char_name_clean}_ORIGIN.png"
    if not char_path.exists():
        raise FileNotFoundError(f"キャラクター画像が見つかりません: {char_path}")

    return Image.open(char_path)

def yaml_to_prompt(comic_page_data):
    """構造化YAMLを詳細なプロンプトに変換"""

    # 基本情報
    language = comic_page_data.get('language', 'Japanese')
    style = comic_page_data.get('style', 'japanese manga')
    color_mode = comic_page_data.get('color_mode', 'カラー')
    aspect_ratio = comic_page_data.get('aspect_ratio', '1:1.4')
    instructions = comic_page_data.get('instructions', '')
    layout_constraints = comic_page_data.get('layout_constraints', '')

    # キャラクター情報
    character_infos = comic_page_data.get('character_infos', [])
    char_descriptions = "\n\n".join([
        f"Character: {char['name']}\n{char['base_prompt']}"
        for char in character_infos
    ])

    # パネル情報
    panels = comic_page_data.get('panels', [])
    panel_descriptions = []

    for panel in panels:
        panel_num = panel['number']
        position = panel.get('page_position', 'middle')
        background = panel.get('background', '')
        description = panel.get('description', '')

        # キャラクター詳細
        characters = panel.get('characters', [])
        char_details = []
        for char in characters:
            char_name = char['name']
            emotion = char.get('emotion', '')
            facing = char.get('facing', '')
            shot = char.get('shot', '')
            pose = char.get('pose', '')

            # セリフ
            lines = char.get('lines', [])
            dialogue = lines[0]['text'] if lines else ''

            char_detail = f"""
  - Character: {char_name}
    Position: {char.get('panel_position', 'center')}
    Emotion: {emotion}
    Facing: {facing}
    Shot type: {shot}
    Pose: {pose}
    Dialogue: "{dialogue}"
"""
            char_details.append(char_detail)

        panel_desc = f"""
Panel {panel_num} (位置: {position}):
  Background: {background}
  Scene description: {description}
  Characters:
{''.join(char_details)}
  Camera angle: {panel.get('camera_angle', 'medium shot')}
"""
        panel_descriptions.append(panel_desc)

    # 完全なプロンプトを構築
    full_prompt = f"""
Generate a complete manga page following these specifications:

=== LAYOUT CONSTRAINTS ===
{layout_constraints}

=== STYLE SPECIFICATIONS ===
- Language: {language}
- Art style: {style}
- Color mode: {color_mode}
- Aspect ratio: {aspect_ratio}
- Writing mode: {comic_page_data.get('writing-mode', 'vertical-rl')}

=== INSTRUCTIONS ===
{instructions}

=== CHARACTER DESIGNS ===
{char_descriptions}

=== PANEL DETAILS ===
{''.join(panel_descriptions)}

IMPORTANT:
- Use the attached character reference images to maintain consistent character designs
- Follow the layout constraints strictly
- Include speech bubbles with the specified dialogue in Japanese
- Maintain the aspect ratio of 1:1.4 (width:height)
- Generate the complete page as a single image with all panels
"""

    return full_prompt

def generate_manga_from_yaml(yaml_path, output_filename=None, session_folder=None):
    """YAMLからマンガを生成

    Args:
        yaml_path: YAMLファイルのパス
        output_filename: 出力ファイル名（省略可）
        session_folder: セッションフォルダ番号（省略可）
    """

    # YAML読み込み
    print(f"📖 YAML読み込み: {yaml_path}")
    data = load_yaml(yaml_path)
    comic_page = data.get('comic_page')

    if not comic_page:
        raise ValueError("YAMLに 'comic_page' キーが見つかりません")

    # API初期化
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY が .env に設定されていません")

    genai.configure(api_key=api_key)

    # モデル設定（Nano Banana = Gemini 2.5 Flash Image Preview）
    model_name = "gemini-2.5-flash-image-preview"
    print(f"🤖 モデル: {model_name}")

    model = genai.GenerativeModel(model_name)

    # プロンプト生成
    print("📝 プロンプト生成中...")
    prompt = yaml_to_prompt(comic_page)
    print(f"プロンプト長: {len(prompt)} 文字")

    # キャラクター画像を収集
    print("👤 キャラクター画像読み込み中...")
    character_infos = comic_page.get('character_infos', [])
    character_images = []

    for char_info in character_infos:
        char_name = char_info['name']
        try:
            img = load_character_image(char_name)
            character_images.append(img)
            print(f"  ✓ {char_name}")
        except FileNotFoundError as e:
            print(f"  ⚠ {e}")

    # Gemini API呼び出し
    print("\n🎨 Nanobanana API呼び出し中...")
    print("  （これには数十秒かかる場合があります）")

    try:
        # 画像 + プロンプトを送信
        content_parts = character_images + [prompt]

        response = model.generate_content(content_parts)

        # レスポンスから画像を抽出
        print("📡 レスポンス受信")

        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]

            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for i, part in enumerate(candidate.content.parts):
                    if hasattr(part, 'inline_data'):
                        print("  ✓ 画像データ発見！")

                        # デバッグ情報
                        mime_type = part.inline_data.mime_type if hasattr(part.inline_data, 'mime_type') else 'unknown'
                        data_type = type(part.inline_data.data).__name__
                        print(f"  データ形式: {mime_type}, タイプ: {data_type}")

                        # データがすでにバイト列かbase64文字列かを判定
                        if isinstance(part.inline_data.data, bytes):
                            # バイト列の場合はそのまま使用
                            image_data = part.inline_data.data
                        else:
                            # 文字列の場合はbase64デコード
                            image_data = base64.b64decode(part.inline_data.data)

                        print(f"  画像データサイズ: {len(image_data)} bytes")
                        image = Image.open(BytesIO(image_data))

                        # 保存
                        if output_filename is None:
                            yaml_file = Path(yaml_path)
                            output_filename = f"{yaml_file.stem}_generated.png"

                        output_path = get_next_output_path(output_filename, session_folder=session_folder)

                        image.save(output_path)
                        print(f"\n✓ マンガを保存しました: {output_path}")
                        print(f"  サイズ: {image.size}")

                        return output_path

                    elif hasattr(part, 'text'):
                        print(f"  テキストレスポンス: {part.text[:200]}")

        print("⚠ 画像が生成されませんでした")
        return None

    except Exception as e:
        print(f"\n✗ API エラー: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='構造化YAMLからマンガを生成')
    parser.add_argument('yaml_path', help='展開済みYAMLファイルのパス')
    parser.add_argument('--session-folder', type=int, help='セッションフォルダ番号（複数ページを同じフォルダに保存）')

    args = parser.parse_args()

    print("=" * 60)
    print("  構造化YAML → マンガ生成")
    print("=" * 60)

    try:
        output_path = generate_manga_from_yaml(args.yaml_path, session_folder=args.session_folder)
        if output_path:
            print("\n" + "=" * 60)
            print("  ✓ 生成完了！")
            print(f"  出力: {output_path}")
            print("=" * 60)
        else:
            print("\n✗ 生成に失敗しました")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
