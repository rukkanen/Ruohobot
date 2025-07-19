# Ruohobot - Autonomous Lawnmower Bot

A modular autonomous robot built on Raspberry Pi 4, repurposed from a lawnmower chassis.

## Architecture

- **Core**: Python-based control system running on Raspberry Pi 4
- **Distance Scanning**: Arduino-based module (rukkanen/DistanceScanner)
- **Sentinel Module**: NodeMCU-based low-power sensor monitoring (rukkanen/sentinel)
- **Communication**: USB for Arduino modules, WiFi for remote control

## Project Structure

```
ruohobot/
├── src/                    # Main source code
├── config/                 # Configuration files
├── logs/                   # Log files
├── tests/                  # Unit and integration tests
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── data/                   # Maps, calibration data, etc.
```

## Quick Start

### Using Management Scripts (Recommended)
```bash
# Start robot interactively
./run_bot.sh

# Check robot status  
./status_bot.sh

# Stop robot safely
./kill_bot.sh

# Test motors separately
./test_motors.sh
```

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python src/main.py
```

### Web Interface
Once running, access the web interface at:
- Local: http://localhost:8080
- Network: http://ROBOT_IP:8080

**WASD Controls**: Click "Manual Control", then click the blue control zone and use W/A/S/D keys for real-time control.

## Documentation

- 📖 **[Management Scripts Guide](docs/management_scripts.md)** - Robot control scripts
- 🌐 **[Web Interface SDK](docs/web_interface_sdk.md)** - API and web interface guide  
- ⚙️ **[Drive Coding Guide](docs/drive_coding.md)** - Motor control and movement
- 📋 **[Scripts README](SCRIPTS_README.md)** - Quick reference for all scripts

## Safety

⚠️ **IMPORTANT**: This bot has had all cutting blades removed for safety.
