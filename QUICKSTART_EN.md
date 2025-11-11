# Quick Start Guide

> **Full Documentation**: See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for complete system understanding

## Setup (First time only)

```powershell
# Enable PowerShell scripts (first time only)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup
.\setup_en.ps1
```

This will:
- Create virtual environment `venv_win`
- Install all required packages

## Generate Manga

```powershell
.\run_en.ps1 simple_story_example
```

Output: `output\simple_story_example_generated.png`

## Create Your Own Story

1. Create `stories\my_story.yaml`:

```yaml
story_title: "My First Manga"
layout_pattern: "pattern_3panel"  # 3, 4, 5, or 6 panels

scenes:
  - character: TEN
    emotion: 悩み
    dialogue: "Creating manga is hard..."
    background: "At desk"
    description: "Thinking hard"

  - character: CLAUDECODE
    emotion: 提案
    dialogue: "This system makes it easy!"
    background: "Jumping from screen"
    description: "Energetic suggestion"

  - character: TEN
    emotion: 喜び
    dialogue: "It really is easy!"
    background: "Same desk"
    description: "Eyes shining with joy"
```

2. Generate:

```powershell
.\run_en.ps1 my_story
```

Done! Check `output\my_story_generated.png`

## Troubleshooting

### Script execution error

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python not found

Make sure Python 3.8+ is installed and in PATH.

```powershell
python --version
```

### Package installation fails

Try installing manually:

```powershell
.\venv_win\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Manual Execution

If scripts don't work, run manually:

```powershell
# Activate virtual environment
.\venv_win\Scripts\Activate.ps1

# Step 1: Expand YAML
python scripts\expand_story.py stories\my_story.yaml

# Step 2: Generate manga
python scripts\generate_from_yaml.py stories\my_story_expanded.yaml
```

## Files

- `setup_en.ps1` - Setup script (create venv + install packages)
- `run_en.ps1` - Generate manga (auto-use venv)
- `USAGE_GUIDE.md` - Detailed documentation (Japanese)
- `README.md` - Full documentation (Japanese)

## Next Steps

See [USAGE_GUIDE.md](USAGE_GUIDE.md) for:
- Custom characters
- Layout patterns
- Emotion variations
- Advanced usage
