@echo off
REM Script untuk menjalankan bot di Windows dengan graceful shutdown
REM Gunakan: run_bot.bat

echo.
echo ============================================
echo.
echo 🤖 Starting Telegram Bot...
echo 💡 Press Ctrl+C to stop the bot safely
echo.
echo ============================================
echo.

python bot.py

echo.
echo ✅ Bot shutdown complete!
echo.
pause
