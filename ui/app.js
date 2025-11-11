// Instagram Manga Generator - Main App Logic

const API_KEY_STORAGE = 'instagram_manga_api_key';
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent';

// DOM Elements
const apiKeyInput = document.getElementById('apiKey');
const saveApiKeyBtn = document.getElementById('saveApiKey');
const clearApiKeyBtn = document.getElementById('clearApiKey');
const apiStatus = document.getElementById('apiStatus');
const yamlInput = document.getElementById('yamlInput');
const yamlStatus = document.getElementById('yamlStatus');
const loadExampleBtn = document.getElementById('loadExample');
const generateBtn = document.getElementById('generateBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultSection = document.getElementById('resultSection');
const resultImage = document.getElementById('resultImage');
const downloadBtn = document.getElementById('downloadBtn');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const closeErrorBtn = document.getElementById('closeError');

// State
let currentApiKey = null;
let currentYamlData = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadApiKey();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    saveApiKeyBtn.addEventListener('click', saveApiKey);
    clearApiKeyBtn.addEventListener('click', clearApiKey);
    loadExampleBtn.addEventListener('click', loadExampleYaml);
    yamlInput.addEventListener('input', validateYaml);
    generateBtn.addEventListener('click', generateManga);
    downloadBtn.addEventListener('click', downloadImage);
    closeErrorBtn.addEventListener('click', () => {
        errorSection.style.display = 'none';
    });
}

// API Key Management
function loadApiKey() {
    const savedKey = localStorage.getItem(API_KEY_STORAGE);
    if (savedKey) {
        currentApiKey = savedKey;
        apiKeyInput.value = savedKey;
        updateApiStatus(true);
    } else {
        updateApiStatus(false);
    }
    updateGenerateButton();
}

function saveApiKey() {
    const key = apiKeyInput.value.trim();
    if (!key) {
        showError('APIキーを入力してください');
        return;
    }
    localStorage.setItem(API_KEY_STORAGE, key);
    currentApiKey = key;
    updateApiStatus(true);
    updateGenerateButton();
    showSuccess('APIキーを保存しました');
}

function clearApiKey() {
    localStorage.removeItem(API_KEY_STORAGE);
    currentApiKey = null;
    apiKeyInput.value = '';
    updateApiStatus(false);
    updateGenerateButton();
    showSuccess('APIキーをクリアしました');
}

function updateApiStatus(connected) {
    if (connected) {
        apiStatus.textContent = '設定済み';
        apiStatus.className = 'status connected';
    } else {
        apiStatus.textContent = '未設定';
        apiStatus.className = 'status disconnected';
    }
}

// YAML Validation
function validateYaml() {
    const yamlText = yamlInput.value.trim();

    if (!yamlText) {
        yamlStatus.textContent = 'YAMLを入力してください';
        yamlStatus.className = 'info-text';
        currentYamlData = null;
        updateGenerateButton();
        return;
    }

    try {
        const parsed = jsyaml.load(yamlText);

        // Validate structure
        if (!parsed.comic_page) {
            throw new Error('comic_page キーが見つかりません');
        }

        if (!parsed.comic_page.panels || parsed.comic_page.panels.length === 0) {
            throw new Error('panels が定義されていません');
        }

        currentYamlData = parsed;
        yamlStatus.textContent = `✓ 有効なYAML (${parsed.comic_page.panels.length}コマ)`;
        yamlStatus.className = 'info-text valid';
        updateGenerateButton();
    } catch (e) {
        yamlStatus.textContent = `✗ エラー: ${e.message}`;
        yamlStatus.className = 'info-text invalid';
        currentYamlData = null;
        updateGenerateButton();
    }
}

function updateGenerateButton() {
    generateBtn.disabled = !(currentApiKey && currentYamlData);
}

// Load Example YAML
function loadExampleYaml() {
    const exampleYaml = `comic_page:
  language: Japanese
  style: japanese manga, chibi/deformed style
  writing-mode: vertical-rl
  color_mode: カラー
  aspect_ratio: '1:1.4'
  instructions: このYAMLは漫画ページの仕様です。添付の画像データ（キャラクター等、コマ割り画像）がある場合は、それらを外見の基準として忠実に反映し、このプロンプトの指示に従ってページを生成してください。
  layout_constraints: |
    指示: 以下のレイアウト制約を厳守して画像を生成してください。
    - ページ全体のアスペクト比は 1:1.4（幅:高さ）を絶対に厳守する。必要に応じて余白やトリミングで合わせる。
    - パネルは3つ。上から順に panel 1, 2, 3 を縦方向に配置する。
    - パネルの追加・削除・結合・回転・順序入替えは禁止。与えられた panel.number の順に配置する。
    - 各パネルの内容（人物・背景・効果・吹き出し・文字）はそのパネル枠の内部に完全に収める。
    - 収まりが難しい場合は、構図・スケール・軽微なトリミングで調整し、枠構成（コマ数や順序）は変えない。
    - 読み順は panel.number の昇順。
  character_infos:
  - name: TEN
    base_prompt: |
      A young male engineer character in chibi/deformed anime style.
      - Black messy hair with bangs
      - Round black-framed glasses
      - Black t-shirt and blue jeans
      - Casual, friendly appearance
      - Chibi proportions (large head, small body)
      - Expressive eyes visible through glasses
      This is a consistent character design that must be maintained across all panels.
  - name: CLAUDECODE
    base_prompt: |
      A cute robot character in chibi/deformed anime style wearing an astronaut suit.
      - White/silver astronaut helmet and suit
      - Orange circular face panel (like a visor)
      - Blue accents on the body
      - Small, round body with short limbs
      - Cable/cord extending from the back like a tail
      - Friendly, helpful appearance
      - Chibi proportions
      This is a consistent character design that must be maintained across all panels.
  panels:
  - number: 1
    page_position: top
    background: 深夜のデスク、モニターにInstagramが映っている
    description: パソコンの前で腕組みして考え込んでいる
    characters:
    - name: TEN
      panel_position: center
      emotion: troubled, thinking hard, hand on chin
      facing: 右
      shot: バストアップ
      pose: パソコンの前で腕組みして考え込んでいる
      description: パソコンの前で腕組みして考え込んでいる
      lines:
      - text: インスタでマンガ投稿したいけど...毎回描くの無理ゲーすぎる
        char_text_position: left
        type: speech
    effects: []
    monologues: []
    camera_angle: medium shot
  - number: 2
    page_position: middle
    background: 画面から飛び出してくる演出
    description: 元気いっぱい、片手を上げて挨拶
    characters:
    - name: CLAUDECODE
      panel_position: center
      emotion: suggesting, one finger raised, helpful gesture
      facing: 左
      shot: バストアップ
      pose: 元気いっぱい、片手を上げて挨拶
      description: 元気いっぱい、片手を上げて挨拶
      lines:
      - text: それ、AIで自動化できますよ！Google の Nano Banana 知ってます？
        char_text_position: right
        type: speech
    effects: []
    monologues: []
    camera_angle: medium shot
  - number: 3
    page_position: bottom
    background: 同じデスク
    description: 目を輝かせて身を乗り出す、メガネがキラリ
    characters:
    - name: TEN
      panel_position: center
      emotion: surprised, eyes wide, mouth open
      facing: 右
      shot: バストアップ
      pose: 目を輝かせて身を乗り出す、メガネがキラリ
      description: 目を輝かせて身を乗り出す、メガネがキラリ
      lines:
      - text: マジで!? どうやるの？
        char_text_position: left
        type: speech
    effects: []
    monologues: []
    camera_angle: medium shot`;

    yamlInput.value = exampleYaml;
    validateYaml();
}

// Convert YAML to Prompt (ported from Python)
function yamlToPrompt(comicPageData) {
    const language = comicPageData.language || 'Japanese';
    const style = comicPageData.style || 'japanese manga';
    const colorMode = comicPageData.color_mode || 'カラー';
    const aspectRatio = comicPageData.aspect_ratio || '1:1.4';
    const instructions = comicPageData.instructions || '';
    const layoutConstraints = comicPageData.layout_constraints || '';

    // Character descriptions
    const characterInfos = comicPageData.character_infos || [];
    const charDescriptions = characterInfos.map(char =>
        `Character: ${char.name}\n${char.base_prompt}`
    ).join('\n\n');

    // Panel descriptions
    const panels = comicPageData.panels || [];
    const panelDescriptions = panels.map(panel => {
        const panelNum = panel.number;
        const position = panel.page_position || 'middle';
        const background = panel.background || '';
        const description = panel.description || '';

        // Character details
        const characters = panel.characters || [];
        const charDetails = characters.map(char => {
            const charName = char.name;
            const emotion = char.emotion || '';
            const facing = char.facing || '';
            const shot = char.shot || '';
            const pose = char.pose || '';

            // Dialogue
            const lines = char.lines || [];
            const dialogue = lines.length > 0 ? lines[0].text : '';

            return `  - Character: ${charName}
    Position: ${char.panel_position || 'center'}
    Emotion: ${emotion}
    Facing: ${facing}
    Shot type: ${shot}
    Pose: ${pose}
    Dialogue: "${dialogue}"`;
        }).join('\n');

        return `Panel ${panelNum} (位置: ${position}):
  Background: ${background}
  Scene description: ${description}
  Characters:
${charDetails}
  Camera angle: ${panel.camera_angle || 'medium shot'}`;
    }).join('\n\n');

    // Build full prompt
    const fullPrompt = `Generate a complete manga page following these specifications:

=== LAYOUT CONSTRAINTS ===
${layoutConstraints}

=== STYLE SPECIFICATIONS ===
- Language: ${language}
- Art style: ${style}
- Color mode: ${colorMode}
- Aspect ratio: ${aspectRatio}
- Writing mode: ${comicPageData['writing-mode'] || 'vertical-rl'}

=== INSTRUCTIONS ===
${instructions}

=== CHARACTER DESIGNS ===
${charDescriptions}

=== PANEL DETAILS ===
${panelDescriptions}

IMPORTANT:
- Use the attached character reference images to maintain consistent character designs
- Follow the layout constraints strictly
- Include speech bubbles with the specified dialogue in Japanese
- Maintain the aspect ratio of 1:1.4 (width:height)
- Generate the complete page as a single image with all panels`;

    return fullPrompt;
}

// Load Character Images
async function loadCharacterImages(characterInfos) {
    const images = [];

    for (const charInfo of characterInfos) {
        const charName = charInfo.name.toUpperCase().replace(/\s+/g, '');
        const imagePath = `public/characters/${charName}_ORIGIN.png`;

        try {
            const response = await fetch(imagePath);
            if (!response.ok) {
                console.warn(`Character image not found: ${imagePath}`);
                continue;
            }

            const blob = await response.blob();
            const base64 = await blobToBase64(blob);

            images.push({
                inlineData: {
                    mimeType: 'image/png',
                    data: base64.split(',')[1] // Remove data:image/png;base64, prefix
                }
            });
        } catch (e) {
            console.warn(`Failed to load character image: ${charName}`, e);
        }
    }

    return images;
}

// Helper: Convert Blob to Base64
function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

// Generate Manga
async function generateManga() {
    if (!currentApiKey || !currentYamlData) {
        showError('APIキーとYAMLを設定してください');
        return;
    }

    try {
        // Hide previous results/errors
        resultSection.style.display = 'none';
        errorSection.style.display = 'none';

        // Show loading
        loadingIndicator.style.display = 'block';
        generateBtn.disabled = true;

        const comicPage = currentYamlData.comic_page;

        // Generate prompt
        console.log('Generating prompt...');
        const prompt = yamlToPrompt(comicPage);
        console.log('Prompt length:', prompt.length);

        // Load character images
        console.log('Loading character images...');
        const characterImages = await loadCharacterImages(comicPage.character_infos || []);
        console.log('Loaded', characterImages.length, 'character images');

        // Build request body
        const parts = [
            ...characterImages,
            { text: prompt }
        ];

        const requestBody = {
            contents: [{
                role: 'user',
                parts: parts
            }]
        };

        // Call Gemini API
        console.log('Calling Gemini API...');
        const response = await fetch(`${GEMINI_API_URL}?key=${currentApiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`API Error: ${errorData.error?.message || response.statusText}`);
        }

        const data = await response.json();
        console.log('API Response received');

        // Extract image from response
        if (data.candidates && data.candidates.length > 0) {
            const candidate = data.candidates[0];

            if (candidate.content && candidate.content.parts) {
                for (const part of candidate.content.parts) {
                    if (part.inlineData && part.inlineData.data) {
                        console.log('Image data found!');

                        // Display image
                        const mimeType = part.inlineData.mimeType || 'image/png';
                        const imageData = part.inlineData.data;
                        const imageUrl = `data:${mimeType};base64,${imageData}`;

                        resultImage.src = imageUrl;
                        resultSection.style.display = 'block';

                        showSuccess('漫画の生成に成功しました！');
                        return;
                    }
                }
            }
        }

        throw new Error('API response did not contain image data');

    } catch (e) {
        console.error('Generation error:', e);
        showError(`生成エラー: ${e.message}`);
    } finally {
        loadingIndicator.style.display = 'none';
        generateBtn.disabled = false;
    }
}

// Download Image
function downloadImage() {
    const link = document.createElement('a');
    link.href = resultImage.src;
    link.download = `manga_${Date.now()}.png`;
    link.click();
}

// UI Feedback
function showError(message) {
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
}

function showSuccess(message) {
    // Simple console log for now
    console.log('✓', message);
    // Could add a toast notification here
}
