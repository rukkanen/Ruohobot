# Ruohobot Control Scripts

This directory contains convenient shell scripts to manage your Ruohobot.

## Scripts Overview

### 🚀 `run_bot.sh`
**Interactive mode** - Starts the robot in the foreground
```bash
./run_bot.sh
```
- Shows real-time logs in the terminal
- Press Ctrl+C to stop
- Good for development and debugging
- Includes pre-flight checks (virtual env, config files)
- Force restart with `./run_bot.sh -f` or `./run_bot.sh --force`

### 🌙 `run_bot_bg.sh` 
**Background mode** - Starts the robot as a daemon
```bash
./run_bot_bg.sh
```
- Runs in the background
- Logs saved to `logs/robot_output.log`
- Perfect for production/autonomous operation
- Returns immediately after starting

### 🛑 `kill_bot.sh`
**Stop the robot** - Safely stops all robot processes
```bash
./kill_bot.sh
```
- Tries graceful shutdown first (SIGTERM)
- Forces kill if needed (SIGKILL)
- Works for both interactive and background modes
- Safe to run multiple times

### 📊 `status_bot.sh`
**Check status** - Shows comprehensive robot status
```bash
./status_bot.sh
```
- Shows if robot is running
- Displays uptime and process info
- Tests web interface connectivity
- Shows current robot state and recent logs

## Quick Start

1. **Start the robot (interactive):**
   ```bash
   ./run_bot.sh
   ```

2. **Check if it's working:**
   ```bash
   ./status_bot.sh
   ```

3. **Stop the robot:**
   ```bash
   ./kill_bot.sh
   ```

## Web Interface

When the robot is running, the web interface is available at:
- **Local:** http://localhost:8080
- **Network:** http://YOUR_PI_IP:8080

### Using WASD Controls
1. Open the web interface
2. Click "Manual Control" button
3. Click the blue "WASD Control Zone" area
4. Use W/A/S/D keys to control the robot

## Files Created

- `logs/ruohobot.log` - Main robot log file
- `logs/robot_output.log` - Console output (background mode only)

## Troubleshooting

### Robot won't start
- Check virtual environment: `ls -la .venv/`
- Check config file: `ls -la config/robot_config.yaml`
- Check permissions: `ls -la *.sh`

### Web interface not accessible
- Check if robot is running: `./status_bot.sh`
- Check firewall settings
- Try: `curl http://localhost:8080/status`

### WASD controls not working
- Make sure robot is in "Manual Control" mode
- Click the WASD control area to give it focus
- Check browser console for JavaScript errors

## Advanced Usage

### Running on System Boot
Add to crontab for automatic startup:
```bash
@reboot cd /path/to/Ruohobot && ./run_bot_bg.sh
```

### Monitoring Logs
Watch logs in real-time:
```bash
tail -f logs/ruohobot.log
```

### Remote Access
The robot accepts connections from any IP address. Make sure your firewall allows port 8080.

---

*Need help? Check the main README.md or the docs/ directory for more information.*
