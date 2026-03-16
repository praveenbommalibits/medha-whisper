#!/bin/bash
# First-time setup: creates ~/.medhawhisper with your config
set -e

CONFIG_DIR="$HOME/.medhawhisper"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/.env" ]; then
  cp "$SCRIPT_DIR/.env.example" "$CONFIG_DIR/.env"
  echo "Created $CONFIG_DIR/.env — edit it to add your OPENAI_API_KEY"
else
  echo "$CONFIG_DIR/.env already exists, skipping."
fi

if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
  cp "$SCRIPT_DIR/config.yaml" "$CONFIG_DIR/config.yaml"
  echo "Created $CONFIG_DIR/config.yaml"
else
  echo "$CONFIG_DIR/config.yaml already exists, skipping."
fi

echo ""
echo "✅ Setup complete. Edit $CONFIG_DIR/.env and add your OpenAI API key."
echo "   Then run: python build_app.py"
