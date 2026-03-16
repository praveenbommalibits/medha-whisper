# MedhaWhisper

**Voice-to-text everywhere on macOS. Powered by OpenAI Whisper.**

Press a hotkey → speak → text appears at your cursor. Works in VS Code, Chrome, Slack, Terminal — anywhere.

## Features

- **OpenAI Whisper API** — Uses `whisper-1` for highest accuracy transcription
- **GPT-4o text cleanup** — Optional AI polish for grammar, punctuation, formatting
- **Global hotkey** — `Ctrl+Shift+Space` to start/stop recording from anywhere
- **Auto-type** — Transcribed text is typed at your cursor position automatically
- **Background service** — Runs as a macOS LaunchAgent, always ready
- **Multi-language** — Supports Hindi, English, Hinglish, and 50+ languages
- **Clipboard mode** — Optionally copies to clipboard instead of auto-typing
- **Menu bar icon** — Quick access from macOS menu bar

## Requirements

- macOS 13+ (Ventura or later)
- Python 3.10+
- OpenAI API key
- Microphone access permission
- Accessibility permission (for auto-typing)

## Quick Start

```bash
# Clone and setup
cd medha-whisper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run
python medha_whisper.py
```

## Install as Background Service

```bash
# Install as macOS LaunchAgent (starts on login)
./install.sh

# Uninstall
./uninstall.sh
```

## Configuration

Edit `.env` or `config.yaml`:

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENAI_API_KEY` | — | Your OpenAI API key (required) |
| `HOTKEY` | `ctrl+shift+space` | Global hotkey to toggle recording |
| `MODEL` | `whisper-1` | Whisper model to use |
| `LANGUAGE` | `auto` | Language hint (e.g., `en`, `hi`, `auto`) |
| `CLEANUP_ENABLED` | `true` | Enable GPT-4o text cleanup |
| `CLEANUP_MODEL` | `gpt-4o` | Model for text cleanup |
| `OUTPUT_MODE` | `type` | `type` (auto-type) or `clipboard` |

## Models Used

| Purpose | Model | Why |
|---------|-------|-----|
| Transcription | `whisper-1` | OpenAI's best speech-to-text, supports 50+ languages |
| Text cleanup | `gpt-4o` | Fixes grammar, adds punctuation, formats cleanly |

## How It Works

1. Press `Ctrl+Shift+Space` — recording starts
2. Speak naturally in any language
3. Press hotkey again (or pause for 2s) — recording stops
4. Audio is sent to OpenAI Whisper API for transcription
5. (Optional) GPT-4o cleans up the text
6. Text is auto-typed at your cursor position via macOS Accessibility API

## Permissions

On first run, macOS will ask for:
- **Microphone** — to record your voice
- **Accessibility** — to type text into other apps (System Settings → Privacy & Security → Accessibility)

## License

MIT
