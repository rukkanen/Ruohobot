# Project Structure

This document describes the modular Python structure of the Ruohobot project.

## Directory Structure

```
ruohobot/
├── src/                          # Main source code
│   ├── __init__.py              # Main package initialization
│   ├── main.py                  # Main entry point
│   ├── core/                    # Core control logic
│   │   ├── __init__.py         # Core package exports
│   │   ├── robot.py            # Main robot controller
│   │   ├── state_machine.py    # Robot state management
│   │   ├── navigation.py       # Autonomous navigation
│   │   ├── safety.py           # Safety monitoring system
│   │   ├── communication.py    # WiFi communication & telemetry
│   │   ├── hardware_manager.py # Hardware abstraction layer
│   │   └── config_manager.py   # Configuration management
│   ├── hardware/                # Hardware-specific modules
│   │   ├── __init__.py         # Hardware package exports
│   │   ├── motors.py           # Motor control (Pololu shield)
│   │   ├── sensors.py          # Local sensors (IMU, battery, etc.)
│   │   └── external_modules.py # Arduino & NodeMCU communication
│   └── utils/                   # Utility modules
│       ├── __init__.py         # Utils package exports
│       └── logger.py           # Centralized logging
├── demo_modules.py              # Module structure demonstration
├── .gitignore                   # Git ignore patterns
└── README.md                    # Project documentation
```

## Module Overview

### Core Logic (`src/core/`)
- **robot.py**: Main robot controller that orchestrates all subsystems
- **state_machine.py**: Manages robot operational states (idle, manual, autonomous, emergency)
- **navigation.py**: Autonomous navigation, path planning, and obstacle avoidance
- **safety.py**: Safety monitoring, emergency stop, and hazard detection
- **communication.py**: WiFi communication, telemetry, and remote control
- **hardware_manager.py**: Hardware abstraction layer
- **config_manager.py**: Configuration file management

### Hardware Modules (`src/hardware/`)
- **motors.py**: Motor control using Pololu motor shield on Raspberry Pi
- **sensors.py**: Local sensor management (IMU, battery monitoring, environmental)
- **external_modules.py**: Communication with Arduino distance scanner and NodeMCU sentinel

### Utilities (`src/utils/`)
- **logger.py**: Centralized logging configuration and utilities

## Key Features

✅ **Modular Architecture**: Clean separation between core logic, hardware interfaces, and utilities

✅ **Cross-Folder Imports**: Proper Python package structure with `__init__.py` files

✅ **Hardware Abstraction**: Hardware-specific code isolated in separate modules

✅ **Simulation Mode**: Runs without actual hardware for development and testing

✅ **Graceful Degradation**: Handles missing hardware gracefully with simulation fallbacks

## Running the Code

### Main Application
```bash
python src/main.py
```

### Module Structure Demo
```bash
python demo_modules.py
```

## Dependencies

The project is designed to run on Raspberry Pi with minimal dependencies:
- **Python 3.7+**
- **RPi.GPIO** (for motor control on actual hardware)
- **pyserial** (for Arduino/NodeMCU communication)

When running without hardware, the system automatically switches to simulation mode.

## Development

The modular structure allows for easy development and testing:
1. Each module can be imported and tested independently
2. Hardware modules gracefully degrade to simulation mode
3. Core logic is separated from hardware-specific implementations
4. Cross-folder imports work correctly for complex dependencies