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

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python src/main.py
```

## Safety

⚠️ **IMPORTANT**: This bot has had all cutting blades removed for safety.
