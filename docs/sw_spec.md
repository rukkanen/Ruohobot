# Ruohobot Software Specification

## Overview
Ruohobot is a modular, Python-based robot control system designed for autonomous navigation, mapping, and remote operation. It integrates real hardware (LiDAR, encoders, motor controller, sensors) with simulation and debugging features. The system exposes a web interface and HTTP API for control and telemetry.

## Main Components
- **Core Robot Logic**: Handles state machine, safety, navigation, and SLAM.
- **SLAM System**: Real-time occupancy grid mapping using LiDAR and odometry.
- **Motor Control**: Pololu Motoron M3H550 via I2C, supports velocity and emergency stop.
- **Encoder Integration**: Wheel encoders for odometry, GPIO event detection.
- **Sensor Integration**: LiDAR (LD19), IR, sound, and other sensors.
- **Web Interface**: HTTP server (port 8080), dashboard, WASD controls, API endpoints.
- **Configuration**: YAML-based config files for hardware, debug, and SLAM settings.
- **Logging**: Centralized logging to file and console.

## Key Features
- Autonomous and manual control modes
- Real-time SLAM map generation and saving
- Robust LiDAR protocol parsing (LD19)
- Encoder-based odometry and sensor fusion
- Remote control via web dashboard and API
- Safety system with emergency stop
- Modular hardware abstraction (easy to extend)
- Debugging and telemetry tools

## API Endpoints
- `/` : Main dashboard (HTML)
- `/status` : Robot status (JSON)
- `/api/command` : Send control commands (POST)
- `/api/slam_map` : Get current SLAM map (PNG)
- `/api/telemetry` : Extended telemetry (JSON)
- `/api/safety` : Safety status (JSON)

## Hardware Requirements
- Raspberry Pi (Linux)
- Pololu Motoron M3H550 motor controller
- LD19 LiDAR (or simulation)
- Wheel encoders (GPIO)
- Optional: IR, sound, GPS, IMU

## Software Requirements
- Python 3.8+
- RPi.GPIO, motoron, numpy, opencv-python, flask (for some features), pyyaml
- All dependencies installed in a Python virtual environment

## Usage
- Start robot: `python src/main.py` (in venv)
- Access web interface: `http://ROBOT_IP:8080/`
- Run encoder/motor test: `sudo /path/to/venv/bin/python scripts/encoder_tester.py`

## Safety & Debugging
- Emergency stop via web or API
- SLAM map saved to disk for inspection
- Logging to `logs/ruohobot.log`
- Configurable debug flags in YAML

## Extensibility
- Add new sensors via hardware_manager.py
- Extend API endpoints in communication.py
- Add new control modes in robot.py

---
For detailed module documentation, see the `docs/` directory and code comments.
