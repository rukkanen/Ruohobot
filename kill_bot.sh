#!/bin/bash

# Ruohobot Kill Script
# Safely stops all running Ruohobot processes

echo "🤖 Stopping Ruohobot..."

# Find and kill any running Python processes with main.py
PIDS=$(pgrep -f "python.*main.py")

if [ -z "$PIDS" ]; then
    echo "✅ No Ruohobot processes found running"
else
    echo "🔍 Found Ruohobot processes: $PIDS"
    
    # Try graceful shutdown first
    echo "⏳ Sending SIGTERM (graceful shutdown)..."
    pkill -TERM -f "python.*main.py"
    
    # Wait a moment for graceful shutdown
    sleep 2
    
    # Check if still running
    REMAINING=$(pgrep -f "python.*main.py")
    if [ -n "$REMAINING" ]; then
        echo "⚠️  Processes still running, forcing shutdown..."
        pkill -KILL -f "python.*main.py"
        sleep 1
        
        # Final check
        FINAL_CHECK=$(pgrep -f "python.*main.py")
        if [ -n "$FINAL_CHECK" ]; then
            echo "❌ Failed to stop some processes: $FINAL_CHECK"
            exit 1
        fi
    fi
    
    echo "✅ Ruohobot stopped successfully"
fi

# Also check for any other Python processes that might be related
OTHER_PIDS=$(pgrep -f "Ruohobot")
if [ -n "$OTHER_PIDS" ]; then
    echo "🔍 Found other Ruohobot-related processes: $OTHER_PIDS"
    pkill -TERM -f "Ruohobot"
    sleep 1
    pkill -KILL -f "Ruohobot" 2>/dev/null
fi

echo "🏁 Kill script complete"
