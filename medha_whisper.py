#!/usr/bin/env python3
"""MedhaWhisper — Voice-to-text everywhere on macOS. 100% local, no API keys."""

import io
import os
import struct
import subprocess
import sys
import tempfile
import threading
import time
import wave

import pyaudio
import pyperclip
import requests
import rumps
import yaml
from dotenv import load_dotenv
from pynput import keyboard

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def _base_dir() -> str:
    if getattr(sys, "_MEIPASS", None):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = _base_dir()
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.expanduser("~/.medhawhisper/.env"))


def _load_config() -> dict:
    cfg = {}
    for p in [os.path.join(BASE_DIR, "config.yaml"),
              os.path.expanduser("~/.medhawhisper/config.yaml")]:
        if os.path.exists(p):
            with open(p) as f:
                cfg = yaml.safe_load(f) or {}
            break
    return {
        "hotkey": os.getenv("HOTKEY", cfg.get("hotkey", "ctrl+shift+space")),
        "whisper_model": os.getenv("WHISPER_MODEL", cfg.get("whisper_model", "small")),
        "language": os.getenv("LANGUAGE", cfg.get("language", "auto")),
        "cleanup_enabled": os.getenv("CLEANUP_ENABLED", str(cfg.get("cleanup_enabled", False))).lower() == "true",
        "cleanup_model": os.getenv("CLEANUP_MODEL", cfg.get("cleanup_model", "llama3.2")),
        "output_mode": os.getenv("OUTPUT_MODE", cfg.get("output_mode", "type")),
        "silence_threshold": float(os.getenv("SILENCE_THRESHOLD", cfg.get("silence_threshold", 2.0))),
        "sample_rate": int(os.getenv("SAMPLE_RATE", cfg.get("sample_rate", 16000))),
    }


CONFIG = _load_config()

# ---------------------------------------------------------------------------
# Local Whisper model (faster-whisper, runs on CPU/Metal)
# ---------------------------------------------------------------------------

_whisper_model = None


def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel(
            CONFIG["whisper_model"],
            device="cpu",
            compute_type="int8",
        )
    return _whisper_model

# ---------------------------------------------------------------------------
# Audio recorder
# ---------------------------------------------------------------------------

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = CONFIG["sample_rate"]


class Recorder:
    def __init__(self):
        self._pa = pyaudio.PyAudio()
        self._frames: list[bytes] = []
        self._stream = None
        self._recording = False
        self._silence_start: float | None = None

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self):
        self._frames = []
        self._silence_start = None
        self._recording = True
        self._stream = self._pa.open(
            format=FORMAT, channels=CHANNELS, rate=RATE,
            input=True, frames_per_buffer=CHUNK,
            stream_callback=self._callback,
        )
        self._stream.start_stream()

    def stop(self) -> bytes:
        self._recording = False
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        return self._wav_bytes()

    def _callback(self, in_data, frame_count, time_info, status):
        if not self._recording:
            return (None, pyaudio.paComplete)
        self._frames.append(in_data)
        rms = self._rms(in_data)
        if rms < 300:
            if self._silence_start is None:
                self._silence_start = time.time()
            elif time.time() - self._silence_start >= CONFIG["silence_threshold"]:
                self._recording = False
                return (None, pyaudio.paComplete)
        else:
            self._silence_start = None
        return (None, pyaudio.paContinue)

    @staticmethod
    def _rms(data: bytes) -> float:
        shorts = struct.unpack(f"<{len(data)//2}h", data)
        return (sum(s * s for s in shorts) / len(shorts)) ** 0.5 if shorts else 0

    def _wav_bytes(self) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self._pa.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(self._frames))
        return buf.getvalue()

# ---------------------------------------------------------------------------
# Transcription (local) + cleanup (Ollama)
# ---------------------------------------------------------------------------

def transcribe(audio_bytes: bytes) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.write(audio_bytes)
    tmp.close()
    try:
        model = _get_whisper()
        lang = None if CONFIG["language"] == "auto" else CONFIG["language"]
        segments, _ = model.transcribe(tmp.name, language=lang, beam_size=5)
        return " ".join(seg.text.strip() for seg in segments).strip()
    finally:
        os.unlink(tmp.name)


CLEANUP_PROMPT = (
    "You are a speech-to-text post-processor. Your ONLY job is to clean up "
    "transcribed speech. Rules:\n"
    "1. Fix grammar, spelling, and punctuation\n"
    "2. Remove filler words (um, uh, like, you know)\n"
    "3. Fix sentence boundaries and capitalization\n"
    "4. If the input is Hinglish, output clean English\n"
    "5. NEVER add new information or change meaning\n"
    "6. Return ONLY the cleaned text, no explanations\n\n"
    "Transcribed speech:\n"
)


def cleanup_text(text: str) -> str:
    """Polish text via Ollama (local LLM). Fails silently if Ollama isn't running."""
    if not CONFIG["cleanup_enabled"] or not text:
        return text
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": CONFIG["cleanup_model"],
                "prompt": CLEANUP_PROMPT + text,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 1024},
            },
            timeout=30,
        )
        if resp.ok:
            cleaned = resp.json().get("response", "").strip()
            return cleaned if cleaned else text
    except Exception:
        pass
    return text

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def output_text(text: str):
    if CONFIG["output_mode"] == "clipboard":
        pyperclip.copy(text)
    else:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        script = f'tell application "System Events" to keystroke "{escaped}"'
        subprocess.run(["osascript", "-e", script], check=False)

# ---------------------------------------------------------------------------
# Menu bar app
# ---------------------------------------------------------------------------

class MedhaWhisperApp(rumps.App):
    def __init__(self):
        super().__init__("MedhaWhisper", icon=None, title="🎙")
        self.recorder = Recorder()
        self._busy = False
        self.menu = [
            rumps.MenuItem("Start / Stop Recording  (Ctrl+Shift+Space)", callback=self._toggle),
            None,
            rumps.MenuItem(f"Model: {CONFIG['whisper_model']}"),
            rumps.MenuItem(f"Mode: {CONFIG['output_mode']}", callback=self._toggle_mode),
            rumps.MenuItem(f"Cleanup: {'on' if CONFIG['cleanup_enabled'] else 'off'}", callback=self._toggle_cleanup),
            None,
        ]
        self._start_hotkey_listener()
        # Pre-load whisper model in background
        threading.Thread(target=_get_whisper, daemon=True).start()

    def _start_hotkey_listener(self):
        mapping = {"ctrl": "<ctrl>", "shift": "<shift>", "alt": "<alt>", "cmd": "<cmd>", "space": "<space>"}
        parts = [mapping.get(p.strip().lower(), p.strip().lower()) for p in CONFIG["hotkey"].split("+")]
        combo = "+".join(parts)
        listener = keyboard.GlobalHotKeys({combo: self._toggle})
        listener.daemon = True
        listener.start()

    def _toggle(self, _=None):
        if self._busy:
            return
        if self.recorder.is_recording:
            self._stop_and_transcribe()
        else:
            self._start_recording()

    def _start_recording(self):
        self.title = "🔴"
        self.recorder.start()
        rumps.notification("MedhaWhisper", "Recording…", "Speak now. Press hotkey or pause to stop.")
        threading.Thread(target=self._watch_silence, daemon=True).start()

    def _watch_silence(self):
        while self.recorder.is_recording:
            time.sleep(0.2)
        if not self._busy:
            self._stop_and_transcribe()

    def _stop_and_transcribe(self):
        self._busy = True
        self.title = "⏳"
        audio = self.recorder.stop()
        threading.Thread(target=self._process, args=(audio,), daemon=True).start()

    def _process(self, audio: bytes):
        try:
            text = transcribe(audio)
            if text:
                text = cleanup_text(text)
                output_text(text)
                rumps.notification("MedhaWhisper", "Done ✓", text[:80])
            else:
                rumps.notification("MedhaWhisper", "No speech detected", "Try again.")
        except Exception as e:
            rumps.notification("MedhaWhisper", "Error", str(e)[:120])
        finally:
            self.title = "🎙"
            self._busy = False

    def _toggle_mode(self, sender):
        CONFIG["output_mode"] = "clipboard" if CONFIG["output_mode"] == "type" else "type"
        sender.title = f"Mode: {CONFIG['output_mode']}"

    def _toggle_cleanup(self, sender):
        CONFIG["cleanup_enabled"] = not CONFIG["cleanup_enabled"]
        sender.title = f"Cleanup: {'on' if CONFIG['cleanup_enabled'] else 'off'}"


def main():
    MedhaWhisperApp().run()


if __name__ == "__main__":
    main()
