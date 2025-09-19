#!/bin/zsh
# build_mac.sh
# Build the DIY Animation Scan Aligner macOS .app

APP_NAME="DIY Animation Scan Aligner"
ICON_PATH="icons/align_icon.icns"
SOURCE_SCRIPT="align_gui.py"

echo "🧹 Cleaning old build files..."
rm -rf build dist *.spec

# Ensure PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "⚠️ PyInstaller not found. Installing now..."
    python3 -m pip install --user pyinstaller
fi

echo "📦 Building $APP_NAME..."
python3 -m PyInstaller \
    --noconsole \
    --windowed \
    --name "$APP_NAME" \
    --icon "$ICON_PATH" \
    "$SOURCE_SCRIPT"

echo "✅ Build complete!"
echo "App bundle is in: dist/$APP_NAME.app"
