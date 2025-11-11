"""
簡易ストーリー記述から完全な構造化YAMLを生成

使い方:
    python expand_story.py ../stories/simple_story_example.yaml
"""
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"

def load_yaml(filepath):
    """YAMLファイルを読み込む"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_character_templates():
    """キャラクター情報テンプレートを読み込む"""
    template_path = TEMPLATES_DIR / "character_templates.yaml"
    data = load_yaml(template_path)
    return data['character_infos']

def load_layout_patterns():
    """コマ割りパターンを読み込む"""
    pattern_path = TEMPLATES_DIR / "layout_patterns.yaml"
    return load_yaml(pattern_path)

def get_emotion_description(character, emotion):
    """感情表現を英語のプロンプトに変換"""
    emotion_map = {
        'TEN': {
            '通常': 'neutral, calm expression',
            '悩み': 'troubled, thinking hard, hand on chin',
            '驚き': 'surprised, eyes wide, mouth open',
            '喜び': 'happy, smiling brightly, excited',
            '決意': 'determined, confident, fist clenched',
            '説明': 'explaining, pointing, gesturing',
        },
        'CLAUDECODE': {
            '通常': 'neutral, standing ready',
            '提案': 'suggesting, one finger raised, helpful gesture',
            '作業中': 'working, focused, typing gesture',
            '発見': 'excited discovery, both hands raised',
            '承認': 'thumbs up, approving gesture',
            '説明': 'explaining, gesturing, helpful pose',
        }
    }

    char_map = emotion_map.get(character.upper(), {})
    return char_map.get(emotion, 'neutral expression')

def get_facing_direction(panel_number, total_panels):
    """パネル番号から視線方向を決定（会話のキャッチボールを自然に）"""
    # 奇数パネル: 右向き、偶数パネル: 左向き（対話感を出す）
    return "右" if panel_number % 2 == 1 else "左"

def get_shot_type(description):
    """descriptionから適切なショットタイプを推測"""
    if any(word in description for word in ['全身', '立っている', '座っている']):
        return "全身"
    elif any(word in description for word in ['顔', '表情', 'クローズアップ']):
        return "顔のクローズアップ"
    else:
        return "バストアップ"  # デフォルト

def expand_simple_story(simple_story_path, output_path=None):
    """簡易ストーリーを完全な構造化YAMLに展開"""

    # 簡易ストーリー読み込み
    simple_data = load_yaml(simple_story_path)

    # テンプレート読み込み
    character_infos = load_character_templates()
    layout_patterns = load_layout_patterns()

    # レイアウトパターン取得
    pattern_name = simple_data.get('layout_pattern', 'pattern_3panel')
    pattern = layout_patterns.get(pattern_name)

    if not pattern:
        raise ValueError(f"レイアウトパターン '{pattern_name}' が見つかりません")

    # 完全なYAML構造を構築
    full_yaml = {
        'comic_page': {
            'language': 'Japanese',
            'style': 'japanese manga, chibi/deformed style',
            'writing-mode': 'vertical-rl',
            'color_mode': 'カラー',
            'aspect_ratio': '1:1.4',
            'instructions': (
                'このYAMLは漫画ページの仕様です。添付の画像データ（キャラクター等、コマ割り画像）がある場合は、'
                'それらを外見の基準として忠実に反映し、このプロンプトの指示に従ってページを生成してください。'
            ),
            'layout_constraints': pattern['layout_constraints'],
            'character_infos': character_infos,
            'panels': []
        }
    }

    # 各シーンをパネルに変換
    scenes = simple_data.get('scenes', [])
    total_panels = len(scenes)

    for i, scene in enumerate(scenes, 1):
        character = scene.get('character', 'TEN')
        emotion = scene.get('emotion', '通常')
        dialogue = scene.get('dialogue', '')
        background = scene.get('background', 'シンプルな背景')
        description = scene.get('description', '')

        # パネルポジション取得
        panel_position = pattern['panel_positions'].get(i, 'middle')

        # 感情表現を英語プロンプトに変換
        emotion_prompt = get_emotion_description(character, emotion)

        # 視線方向を自動決定
        facing = get_facing_direction(i, total_panels)

        # ショットタイプを推測
        shot = get_shot_type(description)

        # パネル構造を構築
        panel = {
            'number': i,
            'page_position': panel_position,
            'background': background,
            'description': description,
            'characters': [
                {
                    'name': character,
                    'panel_position': 'center',
                    'emotion': emotion_prompt,
                    'facing': facing,
                    'shot': shot,
                    'pose': description,
                    'description': description,
                    'lines': [
                        {
                            'text': dialogue,
                            'char_text_position': 'right' if facing == '左' else 'left',
                            'type': 'speech'
                        }
                    ] if dialogue else []
                }
            ],
            'effects': [],
            'monologues': [],
            'camera_angle': 'medium shot'
        }

        full_yaml['comic_page']['panels'].append(panel)

    # 出力
    if output_path is None:
        # 入力ファイル名から出力ファイル名を生成
        input_path = Path(simple_story_path)
        output_path = input_path.parent / f"{input_path.stem}_expanded.yaml"

    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(full_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"✓ 完全なYAMLを生成しました: {output_path}")
    return output_path

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使い方: python expand_story.py <simple_story.yaml>")
        sys.exit(1)

    simple_story_path = sys.argv[1]

    print("=" * 60)
    print("  簡易ストーリー → 完全YAML 変換")
    print("=" * 60)

    try:
        output_path = expand_simple_story(simple_story_path)
        print(f"\n出力: {output_path}")
    except Exception as e:
        print(f"\n✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
