#!/bin/bash
# Uninstall MedhaWhisper LaunchAgent
set -e

PLIST_NAME="com.medhalink.medhawhisper"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

launchctl unload "$PLIST_PATH" 2>/dev/null || true
rm -f "$PLIST_PATH"

echo "✅ MedhaWhisper uninstalled."
