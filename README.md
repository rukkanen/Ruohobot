# Ruohobot - Autonomous Lawnmower Bot

-----------
**Rant
## I'll just say it here. Github Copilot has become the main coder in this household. 

I'll take 
responsibility and cudos only for trying to review the flood of code it provided. The bot works,
though lidar, exploration and visualization don't yet (I guess that's like 90% undone still then)
The capabilities of gpt4.1 in agent mode are starting to worry me in the sense, that there's so
much code that even reviewing it takes evening after evening. When will the point come when I 
say "screw this, the code's fine, just go woth the flow". This will lead to future LLMs being 
trained by purely llm idiosynchratic code. Could the be big filter drake/heisenberg issue (neither
are a paradox, btw)**
-----------
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

## Installation Instructions

### Prerequisites
Ensure you have Python installed on your Raspberry Pi OS. You can check this by running:

```bash
python3 --version
```

### Installing Required Python Packages

1. Update your package manager:

```bash
sudo apt update && sudo apt upgrade
```

2. Install OpenCV:

```bash
sudo apt install python3-opencv
```

3. Install Flask:

```bash
pip3 install flask
```

4. Install other dependencies:

```bash
pip3 install -r requirements.txt
```

### Running the Bot

Start the bot using:

```bash
bash run_bot.sh
```

Access the web interface at `http://localhost:8080`.
