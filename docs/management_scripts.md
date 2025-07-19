# Ruohobot Management Scripts Documentation

**Version:** 1.0  
**Date:** July 19, 2025  
**Author:** Ruohobot Development Team

## Overview

The Ruohobot project includes convenient shell scripts for easy robot management. These scripts handle common tasks like starting, stopping, monitoring, and testing the robot system.

## Available Scripts

### 🚀 `run_bot.sh` - Interactive Robot Start
Starts the robot in the foreground with real-time log output.

```bash
./run_bot.sh
```

**Features:**
- ✅ Real-time log display in terminal
- ✅ Press Ctrl+C to stop
- ✅ Pre-flight environment checks
- ✅ Clear startup messages and web interface URL
- ✅ Force restart option: `./run_bot.sh --force`

**Use Cases:**
- Development and debugging
- Manual robot operation
- Testing new features
- Monitoring robot behavior

---

### 🌙 `run_bot_bg.sh` - Background Robot Start  
Starts the robot as a background daemon process.

```bash
./run_bot_bg.sh
```

**Features:**
- ✅ Runs in background (daemon mode)
- ✅ Returns immediately after starting
- ✅ Logs saved to `logs/robot_output.log`
- ✅ Perfect for autonomous operation
- ✅ Survives terminal closure

**Use Cases:**
- Production deployment
- Autonomous lawn mowing
- Remote operation
- Long-term robot tasks

---

### 🛑 `kill_bot.sh` - Safe Robot Stop
Safely stops all robot processes.

```bash
./kill_bot.sh
```

**Features:**
- ✅ Graceful shutdown attempt first (SIGTERM)
- ✅ Force kill if needed (SIGKILL)
- ✅ Handles multiple robot processes
- ✅ Safe to run multiple times
- ✅ Clear status messages

**Process:**
1. Searches for robot processes
2. Sends graceful shutdown signal
3. Waits 2 seconds for clean exit
4. Force kills if still running
5. Verifies all processes stopped

---

### 📊 `status_bot.sh` - Robot Status Check
Comprehensive robot status and health check.

```bash
./status_bot.sh
```

**Information Provided:**
- ✅ Running status and process IDs
- ✅ Robot uptime calculation
- ✅ Web interface connectivity test
- ✅ Current robot state (JSON formatted)
- ✅ Recent log entries (last 5 lines)
- ✅ Helpful next-step suggestions

**Sample Output:**
```
🤖 Ruohobot Status Check
========================
🟢 Status: RUNNING
📊 Process ID(s): 1234
⏱️  Uptime: 02:15:30

🌐 Testing web interface...
✅ Web interface: http://localhost:8080 (ONLINE)

📋 Robot Status:
{
    "robot_state": "RobotState.MANUAL_CONTROL",
    "safety_status": {
        "is_safe": true,
        "emergency_stop_active": false
    }
}
```

---

### 🔧 `test_motors.sh` - Motor Testing Interface
Interactive motor testing and diagnostics tool.

```bash
./test_motors.sh
```

**Features:**
- ✅ Automatically stops robot if running (prevents conflicts)
- ✅ Safety warnings and checks
- ✅ Interactive test menu
- ✅ Individual and sequential motor tests
- ✅ Manual motor control interface
- ✅ Emergency stop functions

**Test Menu Options:**
1. Test individual motor
2. Test all motors sequentially
3. Manual motor control  
4. Test differential drive
5. Show motor status
6. Emergency stop
7. Reset emergency stop
8. Exit

**Safety Features:**
- Exclusive motor controller access
- Pre-test safety warnings
- Emergency stop functionality
- Conservative speed limits for testing

---

## Quick Reference

### Daily Operations
```bash
# Start robot for the day
./run_bot.sh

# Check if everything is working
./status_bot.sh

# Stop robot at end of day  
./kill_bot.sh
```

### Autonomous Operation
```bash
# Start robot in background
./run_bot_bg.sh

# Check status periodically
./status_bot.sh

# Stop when needed
./kill_bot.sh
```

### Development/Testing
```bash
# Test motors separately
./test_motors.sh

# Start robot for development
./run_bot.sh

# Check status during development
./status_bot.sh
```

### Troubleshooting
```bash
# Force restart if robot is stuck
./kill_bot.sh
./run_bot.sh --force

# Check what's happening
./status_bot.sh

# Test hardware separately
./test_motors.sh
```

## Error Handling

### Common Scenarios

**Robot Already Running:**
```bash
$ ./run_bot.sh
⚠️  Ruohobot is already running (PID: 1234)
🛑 Use ./kill_bot.sh to stop it first, or use -f flag to force restart
```

**Missing Virtual Environment:**
```bash
$ ./run_bot.sh  
❌ Virtual environment not found at .venv
💡 Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

**Web Interface Offline:**
```bash
$ ./status_bot.sh
🟢 Status: RUNNING
📊 Process ID(s): 1234
❌ Web interface: OFFLINE
```

## File Locations

**Scripts:** (in project root)
- `run_bot.sh`
- `run_bot_bg.sh` 
- `kill_bot.sh`
- `status_bot.sh`
- `test_motors.sh`

**Log Files:**
- `logs/ruohobot.log` - Main robot log
- `logs/robot_output.log` - Background mode console output

**Configuration:**
- `config/robot_config.yaml` - Robot configuration
- `.venv/` - Python virtual environment

## Integration

### System Service (systemd)
For automatic startup on boot:

```bash
# Create service file
sudo tee /etc/systemd/system/ruohobot.service > /dev/null <<EOF
[Unit]
Description=Ruohobot Autonomous Lawn Mower
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Ruohobot
ExecStart=/home/pi/Ruohobot/run_bot_bg.sh
ExecStop=/home/pi/Ruohobot/kill_bot.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable ruohobot
sudo systemctl start ruohobot
```

### Cron Job
For scheduled operation:

```bash
# Edit crontab
crontab -e

# Add lines for scheduled mowing
0 9 * * 1-5 cd /home/pi/Ruohobot && ./run_bot_bg.sh
0 17 * * 1-5 cd /home/pi/Ruohobot && ./kill_bot.sh
```

## Best Practices

### Development
- Use `./run_bot.sh` for interactive development
- Check `./status_bot.sh` regularly
- Test motors separately with `./test_motors.sh`
- Always use `./kill_bot.sh` to stop (don't kill -9)

### Production
- Use `./run_bot_bg.sh` for autonomous operation
- Monitor with `./status_bot.sh` 
- Set up log rotation for `logs/` directory
- Consider systemd service for auto-restart

### Safety
- Always run `./test_motors.sh` before first use
- Use emergency stop if robot behaves unexpectedly
- Check robot status before leaving unattended
- Secure robot area when testing motors

---

*For more information, see the main README.md and web interface documentation.*
