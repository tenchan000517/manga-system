"""
Instagram用マンガ生成ユーティリティ
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import google.generativeai as genai

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent
CHARACTERS_DIR = PROJECT_ROOT / "characters"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMP_DIR = PROJECT_ROOT / "temp"

# Instagram最適サイズ
INSTAGRAM_FEED_SIZE = (1080, 1350)  # 4:5
PANEL_SIZE = (1080, 337)  # 4コマの場合の1コマサイズ（高さ÷4）

# .envファイル読み込み
load_dotenv(PROJECT_ROOT / ".env")

def init_gemini():
    """Gemini APIの初期化"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY が .env ファイルに設定されていません")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash-image')

def load_character_image(character_name):
    """キャラクター画像を読み込む"""
    char_path = CHARACTERS_DIR / f"{character_name}_ORIGIN.png"
    if not char_path.exists():
        raise FileNotFoundError(f"キャラクター画像が見つかりません: {char_path}")
    return Image.open(char_path)

def save_image(image, filename, subdir=""):
    """画像を保存"""
    if subdir:
        save_dir = OUTPUT_DIR / subdir
    else:
        save_dir = OUTPUT_DIR

    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / filename
    image.save(save_path)
    print(f"✓ 保存完了: {save_path}")
    return save_path

def create_instagram_canvas(num_panels=4):
    """Instagram用のキャンバスを作成"""
    return Image.new('RGB', INSTAGRAM_FEED_SIZE, 'white')

def combine_panels_vertical(panel_images):
    """複数のパネルを縦に結合"""
    num_panels = len(panel_images)
    canvas = create_instagram_canvas(num_panels)

    panel_height = INSTAGRAM_FEED_SIZE[1] // num_panels

    for i, panel_img in enumerate(panel_images):
        # パネルをリサイズ
        panel_resized = panel_img.resize((INSTAGRAM_FEED_SIZE[0], panel_height), Image.Resampling.LANCZOS)
        # キャンバスに貼り付け
        canvas.paste(panel_resized, (0, i * panel_height))

    return canvas

def add_text_to_image(image, text, position=(50, 50), font_size=40, color='black'):
    """画像にテキストを追加"""
    draw = ImageDraw.Draw(image)
    try:
        # システムフォントを試す（環境によって異なる）
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        # フォントが見つからない場合はデフォルトフォント
        font = ImageFont.load_default()

    draw.text(position, text, fill=color, font=font)
    return image

def ensure_directories():
    """必要なディレクトリを確保"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ ディレクトリ確認完了")

if __name__ == "__main__":
    print("=== ユーティリティモジュール ===")
    print(f"プロジェクトルート: {PROJECT_ROOT}")
    print(f"キャラクターディレクトリ: {CHARACTERS_DIR}")
    print(f"出力ディレクトリ: {OUTPUT_DIR}")
    ensure_directories()
