# MedhaWhisper

**Voice-to-text everywhere on macOS. 100% local. No API keys. No cloud. Free.**

Press a hotkey → speak → text appears at your cursor. Works in VS Code, Chrome, Slack, Terminal — anywhere.

## Features

- **Local Whisper** — Runs OpenAI's Whisper model on your Mac via `faster-whisper` (no API key needed)
- **5 model sizes** — Tiny (75MB) to Large-V3 (3GB), pick speed vs accuracy
- **Global hotkey** — `Ctrl+Shift+Space` to start/stop recording from anywhere
- **Auto-type** — Transcribed text is typed at your cursor position automatically
- **Silence detection** — Auto-stops recording after 2s of silence
- **Multi-language** — Supports Hindi, English, Hinglish, and 50+ languages
- **Clipboard mode** — Optionally copies to clipboard instead of auto-typing
- **Menu bar icon** — Quick access from macOS menu bar
- **Optional LLM cleanup** — Polish text via Ollama (local, free)

## Models

| Model | Size | Speed | Accuracy | Best for |
|-------|------|-------|----------|----------|
| `tiny` | 75MB | Fastest | Basic | Quick notes |
| `base` | 140MB | Fast | Good | Casual use |
| `small` | 460MB | Balanced | Great | **Daily use (default)** |
| `medium` | 1.5GB | Slower | Very good | Important docs |
| `large-v3` | 3GB | Slowest | Best | Maximum accuracy |

## Requirements

- macOS 13+ (Ventura or later)
- Python 3.10+
- Microphone access permission
- Accessibility permission (for auto-typing)
- (Optional) [Ollama](https://ollama.com) for text cleanup

## Quick Start

```bash
cd medha-whisper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run directly
python medha_whisper.py
```

## Install as Native Mac App (Recommended)

```bash
# One-time setup
./setup.sh
# Optionally edit ~/.medhawhisper/.env to change model size, hotkey, etc.

# Build the .app
source venv/bin/activate
python build_app.py
```

Then:
1. Drag `dist/MedhaWhisper.app` → `/Applications`
2. Right-click → Open (first launch only, to bypass Gatekeeper)
3. Grant Microphone + Accessibility permissions when prompted

**Auto-start on login:**
System Settings → General → Login Items → click `+` → select MedhaWhisper

## Install as LaunchAgent (Alternative)

```bash
./install.sh    # Starts on login automatically
./uninstall.sh  # Remove
```

## Configuration

Edit `~/.medhawhisper/.env`:

| Setting | Default | Description |
|---------|---------|-------------|
| `HOTKEY` | `ctrl+shift+space` | Global hotkey to toggle recording |
| `WHISPER_MODEL` | `small` | Model size: tiny, base, small, medium, large-v3 |
| `LANGUAGE` | `auto` | Language hint (e.g., `en`, `hi`, `auto`) |
| `CLEANUP_ENABLED` | `false` | Enable Ollama text cleanup |
| `CLEANUP_MODEL` | `llama3.2` | Ollama model for cleanup |
| `OUTPUT_MODE` | `type` | `type` (auto-type) or `clipboard` |

## Optional: Text Cleanup with Ollama

```bash
# Install Ollama (one-time)
brew install ollama
ollama pull llama3.2

# Enable in config
echo "CLEANUP_ENABLED=true" >> ~/.medhawhisper/.env
```

## How It Works

1. Press `Ctrl+Shift+Space` — recording starts
2. Speak naturally in any language
3. Press hotkey again (or pause for 2s) — recording stops
4. Audio is transcribed locally by Whisper
5. (Optional) Ollama cleans up the text
6. Text is auto-typed at your cursor via macOS Accessibility API

## Permissions

On first run, macOS will ask for:
- **Microphone** — to record your voice
- **Accessibility** — to type text into other apps

## License

MIT
