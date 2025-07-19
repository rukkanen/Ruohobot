#!/bin/bash

# Ruohobot Status Check Script
# Shows the current status of the robot

echo "🤖 Ruohobot Status Check"
echo "========================"

# Check for running processes
PIDS=$(pgrep -f "python.*main.py")
if [ -z "$PIDS" ]; then
    echo "🔴 Status: NOT RUNNING"
    echo ""
    echo "💡 To start the robot:"
    echo "   ./run_bot.sh        (interactive mode)"
    echo "   ./run_bot_bg.sh     (background mode)"
else
    echo "🟢 Status: RUNNING"
    echo "📊 Process ID(s): $PIDS"
    
    # Check how long it's been running
    for pid in $PIDS; do
        if [ -f "/proc/$pid/stat" ]; then
            START_TIME=$(stat -c %Y /proc/$pid)
            CURRENT_TIME=$(date +%s)
            UPTIME=$((CURRENT_TIME - START_TIME))
            UPTIME_HUMAN=$(date -u -d @$UPTIME +'%H:%M:%S')
            echo "⏱️  Uptime: $UPTIME_HUMAN"
        fi
    done
    
    # Check web interface
    echo ""
    echo "🌐 Testing web interface..."
    if curl -s http://localhost:8080/status > /dev/null 2>&1; then
        echo "✅ Web interface: http://localhost:8080 (ONLINE)"
        
        # Get robot status
        STATUS=$(curl -s http://localhost:8080/status 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$STATUS" ]; then
            echo ""
            echo "📋 Robot Status:"
            echo "$STATUS" | python3 -m json.tool 2>/dev/null || echo "$STATUS"
        fi
    else
        echo "❌ Web interface: OFFLINE"
    fi
    
    echo ""
    echo "🛑 To stop the robot:"
    echo "   ./kill_bot.sh"
fi

echo ""
echo "📁 Recent log entries:"
echo "======================"
if [ -f "logs/ruohobot.log" ]; then
    tail -5 logs/ruohobot.log
else
    echo "No log file found"
fi
