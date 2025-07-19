#!/bin/bash

# Ruohobot Start Script
# Starts the robot with proper environment and error handling

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 Starting Ruohobot..."
echo "📂 Working directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found at .venv"
    echo "💡 Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if already running
EXISTING=$(pgrep -f "python.*main.py")
if [ -n "$EXISTING" ]; then
    echo "⚠️  Ruohobot is already running (PID: $EXISTING)"
    echo "🛑 Use ./kill_bot.sh to stop it first, or use -f flag to force restart"
    
    if [ "$1" = "-f" ] || [ "$1" = "--force" ]; then
        echo "🔄 Force restart requested, stopping existing processes..."
        ./kill_bot.sh
        sleep 2
    else
        exit 1
    fi
fi

# Check if main.py exists
if [ ! -f "src/main.py" ]; then
    echo "❌ src/main.py not found"
    exit 1
fi

# Check if config exists
if [ ! -f "config/robot_config.yaml" ]; then
    echo "❌ config/robot_config.yaml not found"
    exit 1
fi

# Activate virtual environment and start robot
echo "🚀 Starting Ruohobot main process..."
echo "📋 Logs will be written to logs/ruohobot.log"
echo "🌐 Web interface will be available at http://localhost:8080"
echo "⌨️  Press Ctrl+C to stop"
echo ""

# Start the robot
.venv/bin/python src/main.py

# If we get here, the robot has stopped
echo ""
echo "🏁 Ruohobot has stopped"
