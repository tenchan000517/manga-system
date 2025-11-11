"""
セットアップテストスクリプト
環境が正しく設定されているか確認します
"""
import sys
from pathlib import Path

print("=" * 60)
print("  セットアップテスト")
print("=" * 60)

# 1. Pythonバージョン確認
print(f"\n✓ Python: {sys.version}")

# 2. 必要なパッケージの確認
packages = {
    'PIL': 'Pillow',
    'yaml': 'PyYAML',
    'google.generativeai': 'google-generativeai',
    'dotenv': 'python-dotenv'
}

print("\n📦 パッケージ確認:")
missing = []
for module_name, package_name in packages.items():
    try:
        __import__(module_name)
        print(f"  ✓ {package_name}")
    except ImportError:
        print(f"  ✗ {package_name} (未インストール)")
        missing.append(package_name)

if missing:
    print(f"\n⚠ 以下のパッケージをインストールしてください:")
    print(f"   pip install {' '.join(missing)}")
    sys.exit(1)

# 3. ディレクトリ確認
print("\n📁 ディレクトリ確認:")
PROJECT_ROOT = Path(__file__).parent.parent
dirs_to_check = {
    'characters': PROJECT_ROOT / 'characters',
    'stories': PROJECT_ROOT / 'stories',
    'output': PROJECT_ROOT / 'output',
    'scripts': PROJECT_ROOT / 'scripts'
}

for name, path in dirs_to_check.items():
    if path.exists():
        print(f"  ✓ {name}/ ")
    else:
        print(f"  ✗ {name}/ (存在しません)")

# 4. キャラクター画像確認
print("\n👤 キャラクター画像:")
char_dir = PROJECT_ROOT / 'characters'
for char_file in ['TEN_ORIGIN.png', 'CLAUDECODE_ORIGIN.png']:
    char_path = char_dir / char_file
    if char_path.exists():
        size = char_path.stat().st_size / 1024 / 1024
        print(f"  ✓ {char_file} ({size:.1f}MB)")
    else:
        print(f"  ✗ {char_file} (見つかりません)")

# 5. .env確認
print("\n🔑 APIキー確認:")
env_path = PROJECT_ROOT / '.env'
if env_path.exists():
    print(f"  ✓ .env ファイル存在")
    from dotenv import load_dotenv
    import os
    load_dotenv(env_path)
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"  ✓ GOOGLE_API_KEY 設定済み ({api_key[:10]}...)")
    else:
        print(f"  ✗ GOOGLE_API_KEY が設定されていません")
else:
    print(f"  ✗ .env ファイルが見つかりません")

# 6. ストーリーファイル確認
print("\n📖 ストーリーファイル:")
story_dir = PROJECT_ROOT / 'stories'
yaml_files = list(story_dir.glob('*.yaml'))
if yaml_files:
    for yaml_file in yaml_files:
        print(f"  ✓ {yaml_file.name}")
else:
    print(f"  ⚠ YAMLファイルがありません")

print("\n" + "=" * 60)
print("  テスト完了！")
print("=" * 60)
print("\n次のステップ:")
print("  python generate_manga.py ../stories/episode1.yaml")
print("=" * 60)
