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

def load_layout_reference_image(layout_pattern):
    """レイアウトパターンの参照画像を読み込む

    Args:
        layout_pattern: レイアウトパターン名（例: "pattern_4panel_equal"）

    Returns:
        Image or None: レイアウト参照画像（見つからない場合はNone）
    """
    # layout_patterns.yamlを読み込んで参照画像パスを取得
    layout_patterns_path = TEMPLATES_DIR / "layout_patterns.yaml"
    if not layout_patterns_path.exists():
        print(f"  ⚠ layout_patterns.yaml が見つかりません")
        return None

    with open(layout_patterns_path, 'r', encoding='utf-8') as f:
        layout_patterns = yaml.safe_load(f)

    pattern_data = layout_patterns.get(layout_pattern)
    if not pattern_data:
        print(f"  ⚠ レイアウトパターン '{layout_pattern}' が見つかりません")
        return None

    ref_image_name = pattern_data.get('reference_image')
    if not ref_image_name:
        print(f"  ⚠ レイアウトパターン '{layout_pattern}' に reference_image が定義されていません")
        return None

    # ui/assets/layout/ 配下を探す
    ref_image_path = PROJECT_ROOT / "ui" / "assets" / "layout" / ref_image_name
    if not ref_image_path.exists():
        print(f"  ⚠ レイアウト参照画像が見つかりません: {ref_image_path}")
        return None

    return Image.open(ref_image_path)

def load_character_emotion_image(character_name, emotion):
    """キャラクターの感情別参照画像を読み込む

    Args:
        character_name: キャラクター名（例: "TEN"）
        emotion: 感情（例: "悩み"）

    Returns:
        Image or None: キャラクター参照画像（見つからない場合はNone）
    """
    # character_templates.yamlを読み込んで参照画像パスを取得
    char_templates_path = TEMPLATES_DIR / "character_templates.yaml"
    if not char_templates_path.exists():
        print(f"  ⚠ character_templates.yaml が見つかりません")
        return None

    with open(char_templates_path, 'r', encoding='utf-8') as f:
        char_templates = yaml.safe_load(f)

    characters = char_templates.get('characters', {})
    char_data = characters.get(character_name)
    if not char_data:
        print(f"  ⚠ キャラクター '{character_name}' が見つかりません")
        return None

    emotions_data = char_data.get('emotions', {})
    emotion_data = emotions_data.get(emotion)
    if not emotion_data:
        print(f"  ⚠ キャラクター '{character_name}' の感情 '{emotion}' が見つかりません")
        return None

    ref_image_name = emotion_data.get('reference_image')
    if not ref_image_name:
        print(f"  ⚠ 感情 '{emotion}' に reference_image が定義されていません")
        return None

    # characters/ 配下を探す
    ref_image_path = CHARACTERS_DIR / ref_image_name
    if not ref_image_path.exists():
        print(f"  ⚠ キャラクター参照画像が見つかりません: {ref_image_path}")
        return None

    return Image.open(ref_image_path)

def load_tool_image(tool_name):
    """小物の参照画像を読み込む

    Args:
        tool_name: 小物名（例: "NOTEPC"）

    Returns:
        Image or None: 小物参照画像（見つからない場合はNone）
    """
    if not tool_name or tool_name.strip() == "":
        return None

    # character_templates.yamlから小物情報を取得
    char_templates_path = TEMPLATES_DIR / "character_templates.yaml"
    if not char_templates_path.exists():
        print(f"  ⚠ character_templates.yaml が見つかりません")
        return None

    with open(char_templates_path, 'r', encoding='utf-8') as f:
        char_templates = yaml.safe_load(f)

    tools = char_templates.get('tools', {})
    tool_data = tools.get(tool_name)
    if not tool_data:
        print(f"  ⚠ 小物 '{tool_name}' が見つかりません")
        return None

    ref_image_name = tool_data.get('reference_image')
    if not ref_image_name:
        print(f"  ⚠ 小物 '{tool_name}' に reference_image が定義されていません")
        return None

    # reference_image は相対パスなので、PROJECT_ROOT から解決
    ref_image_path = PROJECT_ROOT / ref_image_name
    if not ref_image_path.exists():
        print(f"  ⚠ 小物参照画像が見つかりません: {ref_image_path}")
        return None

    return Image.open(ref_image_path)

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
- Use the attached reference images (layout pattern, character emotions, and tools) to maintain consistency
- Follow the layout constraints strictly - the panel layout reference image shows the exact panel arrangement
- Include speech bubbles with the specified dialogue in Japanese
- Maintain the aspect ratio of 1:1.4 (width:height)
- Generate the complete page as a single image with all panels
"""

    return full_prompt

def generate_manga_from_yaml(yaml_path, output_filename=None, session_folder=None, count=1):
    """YAMLからマンガを生成

    Args:
        yaml_path: YAMLファイルのパス
        output_filename: 出力ファイル名（省略可）
        session_folder: セッションフォルダ番号（省略可）
        count: 生成枚数（1-4、デフォルト1）
    """

    # 生成枚数を1-4の範囲に制限
    count = max(1, min(count, 4))

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

    # YAMLをそのまま文字列として準備（Easy Banana方式）
    print("📝 YAML指示文準備中...")
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_content = f.read()

    # Easy Banana風のシンプルなシステムプロンプト
    SYSTEM_PROMPT = ' '.join([
        'You are an expert image generation assistant.',
        'Generate one or more high-quality images that match the user\'s prompt.',
        'Return images inline using inlineData with an appropriate MIME type (prefer image/png).',
        'If you include text output, keep it to a single concise English caption.',
        'Do not add disclaimers unless required by safety policies.'
    ])

    prompt = f"{SYSTEM_PROMPT}\n\nUser prompt:\n{yaml_content}"
    print(f"指示文長: {len(prompt)} 文字")

    # 参照画像を収集
    print("🖼️ 参照画像読み込み中...")
    reference_images = []

    # 1. レイアウトパターンの参照画像
    # 元のYAMLファイルから layout_pattern を取得
    yaml_file = Path(yaml_path)
    original_yaml_path = yaml_file.parent / yaml_file.name.replace('_expanded', '')

    if original_yaml_path.exists():
        original_data = load_yaml(original_yaml_path)
        layout_pattern = original_data.get('layout_pattern')
        if layout_pattern:
            print(f"  📐 レイアウトパターン: {layout_pattern}")
            layout_img = load_layout_reference_image(layout_pattern)
            if layout_img:
                reference_images.append(layout_img)
                print(f"    ✓ レイアウト参照画像")

    # 2. 使用されるキャラクターの基本画像を収集（重複なし、感情は使わない）
    if original_yaml_path.exists():
        original_data = load_yaml(original_yaml_path)
        scenes = original_data.get('scenes', [])

        print(f"  👤 キャラクター基本画像:")
        char_images_added = set()  # 重複チェック用

        for scene in scenes:
            char_name = scene.get('character')

            # まだ追加していないキャラクターなら追加
            if char_name not in char_images_added:
                # _ORIGIN.png を読み込む（感情別ではない）
                char_name_clean = char_name.upper().replace(" ", "")
                char_path = CHARACTERS_DIR / f"{char_name_clean}_ORIGIN.png"

                if char_path.exists():
                    char_img = Image.open(char_path)
                    reference_images.append(char_img)
                    print(f"    ✓ {char_name}")
                    char_images_added.add(char_name)
                else:
                    print(f"    ⚠ {char_name}の基本画像が見つかりません: {char_path}")

    # 3. 小物は参照画像として送らない（YAMLの文章で指定）
    # Easy Banana方式では小物画像は読み込まず、YAMLの記述に任せる

    # Gemini API呼び出し（複数回生成）
    print(f"\n🎨 Nanobanana API呼び出し中... (生成枚数: {count})")
    print("  （これには数十秒かかる場合があります）")

    generated_paths = []
    errors = []

    for i in range(count):
        print(f"\n生成中... ({i + 1}/{count})")
        try:
            # 参照画像 + プロンプトを送信
            content_parts = reference_images + [prompt]

            response = model.generate_content(content_parts)

            # レスポンスから画像を抽出
            print("📡 レスポンス受信")

            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]

                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
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

                            # 保存（複数生成の場合は番号を付ける）
                            if output_filename is None:
                                yaml_file = Path(yaml_path)
                                base_name = f"{yaml_file.stem}_generated"
                            else:
                                base_name = output_filename.replace('.png', '')

                            if count > 1:
                                filename = f"{base_name}_{i + 1}.png"
                            else:
                                filename = f"{base_name}.png"

                            output_path = get_next_output_path(filename, session_folder=session_folder)

                            image.save(output_path)
                            print(f"✓ マンガを保存しました: {output_path}")
                            print(f"  サイズ: {image.size}")

                            generated_paths.append(output_path)
                            break

                        elif hasattr(part, 'text'):
                            print(f"  テキストレスポンス: {part.text[:200]}")

                if not generated_paths or len(generated_paths) <= i:
                    print("⚠ この回の生成に失敗しました")
                    errors.append(f"生成 {i + 1}: 画像が生成されませんでした")

        except Exception as e:
            print(f"\n✗ API エラー ({i + 1}/{count}): {type(e).__name__}: {e}")
            errors.append(f"生成 {i + 1}: {str(e)}")

    # 結果サマリー
    if generated_paths:
        print(f"\n{'=' * 60}")
        print(f"✓ {len(generated_paths)}/{count} 枚の生成に成功しました")
        for path in generated_paths:
            print(f"  - {path}")
        if errors:
            print(f"\n失敗: {len(errors)} 件")
            for err in errors:
                print(f"  - {err}")
        print(f"{'=' * 60}")
        return generated_paths
    else:
        print("\n✗ すべての生成に失敗しました")
        if errors:
            for err in errors:
                print(f"  - {err}")
        return None

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='構造化YAMLからマンガを生成')
    parser.add_argument('yaml_path', help='展開済みYAMLファイルのパス')
    parser.add_argument('--session-folder', type=int, help='セッションフォルダ番号（複数ページを同じフォルダに保存）')
    parser.add_argument('--count', type=int, default=1, help='生成枚数（1-4、デフォルト1）')

    args = parser.parse_args()

    print("=" * 60)
    print("  構造化YAML → マンガ生成")
    print("=" * 60)

    try:
        result = generate_manga_from_yaml(
            args.yaml_path,
            session_folder=args.session_folder,
            count=args.count
        )
        if result:
            # 成功時は何もしない（関数内で既に表示済み）
            pass
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
