#!/bin/bash

# Script untuk menjalankan bot dengan proper shutdown handling
# Gunakan: bash run_bot.sh

echo "🤖 Starting Telegram Bot with Graceful Shutdown..."
echo "💡 Press Ctrl+C anytime to stop the bot safely"
echo ""

cd "$(dirname "$0")" || exit 1

# Run bot
python3 bot.py

# Cleanup setelah bot stop
echo "✅ Bot shutdown complete!"
exit 0
