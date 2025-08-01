#!/bin/bash

# Ruohobot Start Script
# Starts the robot with proper environment and error handling
export PYTHONPATH=~/git/Ruohobot/src
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 Starting Ruohobot..."
echo "📂 Working directory: $SCRIPT_DIR"

# Check if running as root or with sudo capability
if [ "$EUID" -eq 0 ]; then
    echo "✅ Running as root - GPIO access available"
elif sudo -n true 2>/dev/null; then
    echo "✅ Sudo access available - will use sudo for GPIO"
else
    echo "❌ Root access required for GPIO operations"
    echo "💡 Please run with: sudo ./run_bot.sh"
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

# Start the robot with system Python (requires sudo for GPIO)
if [ "$EUID" -eq 0 ]; then
    python3 src/main.py
else
    sudo python3 src/main.py
fi

# If we get here, the robot has stopped
echo ""
echo "🏁 Ruohobot has stopped"
