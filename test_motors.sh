#!/bin/bash

# Ruohobot Motor Tester Script
# Opens the interactive motor testing interface

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 Ruohobot Motor Tester"
echo "========================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found at .venv"
    echo "💡 Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if motor_test.py exists
if [ ! -f "motor_test.py" ]; then
    echo "❌ motor_test.py not found"
    exit 1
fi

# Make sure robot is not running (motors could conflict)
EXISTING=$(pgrep -f "python.*main.py")
if [ -n "$EXISTING" ]; then
    echo "⚠️  Ruohobot is currently running (PID: $EXISTING)"
    echo "🛑 Motor testing requires exclusive access to the motor controller"
    echo ""
    read -p "Do you want to stop the robot and continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Stopping robot..."
        ./kill_bot.sh
        sleep 2
    else
        echo "❌ Aborted - robot still running"
        exit 1
    fi
fi

echo ""
echo "🚀 Starting Motor Tester..."
echo "⚠️  SAFETY WARNING:"
echo "   - Make sure your robot is secure and cannot move freely"
echo "   - Be ready to stop motors if needed"
echo "   - Use low speeds for initial testing"
echo ""
echo "📋 Features available:"
echo "   - Individual motor testing"
echo "   - Sequential motor tests"
echo "   - Manual motor control"
echo "   - Differential drive testing"
echo "   - Motor status monitoring"
echo "   - Emergency stop functions"
echo ""

# Start the motor tester
.venv/bin/python motor_test.py

echo ""
echo "🏁 Motor tester closed"
