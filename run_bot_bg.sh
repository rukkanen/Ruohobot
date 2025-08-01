#!/bin/bash

# Ruohobot Background Start Script
# Starts the robot in the background (daemon mode)
export PYTHONPATH=~/git/Ruohobot/src
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 Starting Ruohobot in background mode..."

# Check if running as root or with sudo capability
if [ "$EUID" -eq 0 ]; then
    echo "✅ Running as root - GPIO access available"
elif sudo -n true 2>/dev/null; then
    echo "✅ Sudo access available - will use sudo for GPIO"
else
    echo "❌ Root access required for GPIO operations"
    echo "💡 Please run with: sudo ./run_bot_bg.sh"
    exit 1
fi

# Check if already running
EXISTING=$(pgrep -f "python.*main.py")
if [ -n "$EXISTING" ]; then
    echo "⚠️  Ruohobot is already running (PID: $EXISTING)"
    echo "🛑 Use ./kill_bot.sh to stop it first"
    exit 1
fi

# Start robot in background
echo "🚀 Starting Ruohobot in background..."

# Start with system Python (requires sudo for GPIO)
if [ "$EUID" -eq 0 ]; then
    nohup python3 src/main.py > logs/robot_output.log 2>&1 &
else
    nohup sudo python3 src/main.py > logs/robot_output.log 2>&1 &
fi
ROBOT_PID=$!

# Wait a moment and check if it started successfully
sleep 2
if kill -0 $ROBOT_PID 2>/dev/null; then
    echo "✅ Ruohobot started successfully in background (PID: $ROBOT_PID)"
    echo "📋 Logs: logs/ruohobot.log"
    echo "📊 Output: logs/robot_output.log"
    echo "🌐 Web interface: http://localhost:8080"
    echo "🛑 Stop with: ./kill_bot.sh"
else
    echo "❌ Failed to start Ruohobot"
    echo "📋 Check logs/robot_output.log for errors"
    exit 1
fi
