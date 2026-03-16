#!/bin/bash
# Install MedhaWhisper as a macOS LaunchAgent (auto-start on login)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_NAME="com.medhalink.medhawhisper"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
PYTHON="$SCRIPT_DIR/venv/bin/python"
MAIN="$SCRIPT_DIR/medha_whisper.py"
LOG="$HOME/Library/Logs/medha-whisper.log"

if [ ! -f "$PYTHON" ]; then
  echo "Error: venv not found. Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$HOME/Library/Logs"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_NAME}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON}</string>
    <string>${MAIN}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${SCRIPT_DIR}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG}</string>
  <key>StandardErrorPath</key>
  <string>${LOG}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
  </dict>
</dict>
</plist>
EOF

launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo "✅ MedhaWhisper installed as LaunchAgent."
echo "   It will auto-start on login."
echo "   Logs: $LOG"
echo ""
echo "   To stop:  launchctl unload $PLIST_PATH"
echo "   To start: launchctl load $PLIST_PATH"
