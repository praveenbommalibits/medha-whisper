#!/usr/bin/env python3
"""
Build MedhaWhisper.app — a native macOS .app bundle.

Usage:
    source venv/bin/activate
    pip install -r requirements.txt
    python build_app.py

Output: dist/MedhaWhisper.app  (drag to /Applications)
"""

import subprocess
import sys

def main():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "MedhaWhisper",
        "--windowed",                    # .app bundle, no terminal window
        "--noconfirm",
        "--clean",
        "--osx-bundle-identifier", "com.medhalink.medhawhisper",
        "--add-data", "config.yaml:.",
        "--add-data", ".env.example:.",
        "--hidden-import", "rumps",
        "--hidden-import", "pynput.keyboard._darwin",
        "--hidden-import", "pynput._util.darwin",
        "medha_whisper.py",
    ]

    # Add icon if it exists
    import os
    if os.path.exists("icon.icns"):
        cmd.extend(["--icon", "icon.icns"])

    print("Building MedhaWhisper.app …")
    subprocess.check_call(cmd)

    # Copy .env into the app bundle if it exists
    import shutil
    app_resources = "dist/MedhaWhisper.app/Contents/MacOS"
    if os.path.exists(".env"):
        shutil.copy(".env", app_resources)
        print("Copied .env into app bundle.")

    print("\n✅ Built: dist/MedhaWhisper.app")
    print("   Drag it to /Applications, then right-click → Open on first launch.")
    print("   To auto-start on login: System Settings → General → Login Items → add MedhaWhisper")


if __name__ == "__main__":
    main()
