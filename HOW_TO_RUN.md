# How to Run Ruohobot

This guide explains how to run the Ruohobot autonomous lawn mower system.

## Quick Start

**TL;DR**: Use system Python with sudo (virtual environment has GPIO conflicts):

```bash
sudo python3 src/main.py
```

## Prerequisites

### Hardware Setup
- Raspberry Pi with GPIO access
- Pololu Motoron M3H550 motor controller (I2C address 16)
- Omron slit-wheel encoders connected to:
  - **Left encoder**: GPIO pin 12
  - **Right encoder**: GPIO pin 27
- GY-521 IMU (I2C address 0x68) - optional
- LD-19 LiDAR sensor - optional

### Software Dependencies

The robot requires several Python packages installed globally (not in a virtual environment due to GPIO conflicts):

```bash
# Install required packages globally
sudo python3 -m pip install --break-system-packages \
    git+https://github.com/pololu/motoron-python.git \
    mpu6050-raspberrypi \
    opencv-python \
    flask \
    smbus2
```

**Note**: The `--break-system-packages` flag is required on modern Raspberry Pi OS versions.

## Running the Robot

### Main Robot Application

```bash
# Navigate to the robot directory
cd /home/lapanen/git/Ruohobot

# Option 1: Run directly with system Python
sudo python3 src/main.py

# Option 2: Use the provided script (will auto-detect sudo needs)
sudo ./run_bot.sh

# Option 3: Run in background mode
sudo ./run_bot_bg.sh
```

### Expected Output

When running successfully, you should see:

```
2025-07-31 23:48:37 - root - INFO - Ruohobot logging initialized
2025-07-31 23:48:37 - core.config_manager - INFO - Configuration loaded
2025-07-31 23:48:38 - core.sensors - INFO - Encoders initialized on pins 12 and 27
2025-07-31 23:48:38 - core.sensors - INFO - IMU initialized at I2C address 0x68
2025-07-31 23:48:38 - core.hardware_manager - INFO - Hardware manager initialized
2025-07-31 23:48:38 - core.communication - INFO - HTTP server started on port 8080
2025-07-31 23:48:39 - core.robot - INFO - Starting robot main loop
```

## Testing Components

### Test Encoders Only

```bash
# Test encoders with manual triggering (no motor movement)
sudo python3 scripts/minimal_encoder_test.py
```

### Test Encoders + Motors

```bash
# Test encoders with motor movement (will move the robot!)
sudo python3 scripts/encoder_tester.py
```

### Test Motors Only

```bash
# Test just motor control
sudo python3 motor_test.py
```

### Test IMU

```bash
# Test IMU sensor (comprehensive test suite)
sudo python3 scripts/imu_tester.py
```

**Expected Output (with IMU connected):**
```
🤖 Ruohobot GY-521 IMU Test
========================================
🔍 Testing raw MPU-6050 communication...
✅ Raw MPU-6050 communication successful
   Temperature: 26.4°C
   Accelerometer: X=0.123, Y=-0.045, Z=0.987 g
   Gyroscope: X=1.2, Y=-0.8, Z=0.3 °/s

🔍 Testing robot IMU class...
✅ Robot IMU class working correctly
   I2C Address: 0x68
   [... sensor data ...]
```

## Convenience Scripts

The robot includes several helper scripts for easy operation:

```bash
# Start robot interactively (can see output and use Ctrl+C)
sudo ./run_bot.sh

# Start robot in background (daemon mode)
sudo ./run_bot_bg.sh

# Check if robot is running
./status_bot.sh

# Stop the robot
./kill_bot.sh
```

**Script Features:**
- `run_bot.sh`: Interactive mode with live output
- `run_bot_bg.sh`: Background mode, logs to files
- `status_bot.sh`: Shows robot status and process info
- `kill_bot.sh`: Safely stops all robot processes

All scripts automatically detect sudo requirements and use system Python.

## Configuration

The robot configuration is stored in `config/robot_config.yaml`. Key settings:

```yaml
hardware:
  sensors:
    encoders:
      left_pin: 12      # GPIO pin for left encoder
      right_pin: 27     # GPIO pin for right encoder
      wheel_diameter: 0.065
      pulses_per_rev: 20
    imu:
      type: mpu6050
      i2c_address: 0x68
```

## Troubleshooting

### Common Issues

#### "Failed to add edge detection" Error

**Problem**: This error occurs when using virtual environments with GPIO.

**Solution**: Always use system Python with globally installed packages:
```bash
# ❌ Don't use venv
sudo venv/bin/python3 src/main.py

# ✅ Use system python
sudo python3 src/main.py
```

#### Permission Denied for GPIO

**Problem**: GPIO requires root access.

**Solution**: Always run with `sudo`:
```bash
sudo python3 src/main.py
```

#### Missing Packages

**Problem**: `ModuleNotFoundError` for required packages.

**Solution**: Install packages globally:
```bash
sudo python3 -m pip install --break-system-packages <package_name>
```

#### Encoder Not Working

**Problem**: Encoders show 0 counts or fail to initialize.

**Solution**: 
1. Check GPIO pin connections (pins 12 and 27)
2. Verify 10kΩ pullup resistors are connected
3. Test with minimal encoder script:
   ```bash
   sudo python3 scripts/minimal_encoder_test.py
   ```

#### IMU Not Working

**Problem**: IMU tests fail with "Input/output error" or "Remote I/O error".

**Solution**:
1. Check I2C connections to GY-521 (SDA, SCL, VCC, GND)
2. Verify I2C address with `sudo i2cdetect -y 1` (should show device at 0x68)
3. Ensure IMU has power (3.3V or 5V)
4. Test with comprehensive IMU tester:
   ```bash
   sudo python3 scripts/imu_tester.py
   ```

#### Motor Controller Not Found

**Problem**: `Failed to initialize MotorController` error.

**Solution**:
1. Check I2C connection to Motoron M3H550
2. Verify I2C address (default: 16)
3. Test I2C communication:
   ```bash
   sudo i2cdetect -y 1
   ```

### Debug Mode

To enable verbose logging, edit `src/utils/logger.py` and change log level to `DEBUG`.

## System Architecture

The robot uses a modular architecture:

- **Hardware Manager**: Controls motors, sensors, and external modules
- **Safety System**: Emergency stop and tilt detection
- **Navigation**: Path planning and obstacle avoidance  
- **Communication**: HTTP server for remote control (port 8080)
- **State Machine**: Manages robot operational states

## Web Interface

When running, the robot starts an HTTP server on port 8080:

```
http://<robot-ip>:8080
```

This provides:
- Real-time sensor data
- Remote control interface
- System status monitoring

## Stopping the Robot

To stop the robot safely:

1. **Ctrl+C** in the terminal running the robot
2. Or use the emergency stop via web interface
3. Or kill the process:
   ```bash
   sudo pkill -f "python3 src/main.py"
   ```

## Important Notes

### Virtual Environment Issue

**⚠️ Critical**: Do NOT use virtual environments (venv, conda, etc.) when running the robot. Virtual environments cause GPIO edge detection to fail on this system. Always use system Python with globally installed packages.

### GPIO Pin Changes

If you need to change encoder pins, update both:
1. `config/robot_config.yaml` - the robot configuration
2. `scripts/encoder_tester.py` - the test script pin definitions

### Hardware Connections

- **Left Encoder (GPIO 12)**: Should have 10kΩ pullup to 3.3V
- **Right Encoder (GPIO 27)**: Should have 10kΩ pullup to 3.3V  
- **Motor Controller**: I2C connection (SDA/SCL) with address 16
- **IMU**: I2C connection with address 0x68

## Scripts Summary

| Script | Purpose | Usage |
|--------|---------|-------|
| `src/main.py` | Main robot application | `sudo python3 src/main.py` |
| `scripts/encoder_tester.py` | Test encoders + motors | `sudo python3 scripts/encoder_tester.py` |
| `scripts/minimal_encoder_test.py` | Test encoders only | `sudo python3 scripts/minimal_encoder_test.py` |
| `scripts/imu_tester.py` | Test IMU sensor | `sudo python3 scripts/imu_tester.py` |
| `motor_test.py` | Test motors only | `sudo python3 motor_test.py` |

## Support

For issues or questions, check:
1. This troubleshooting guide
2. Log files in `logs/` directory
3. System status via web interface at port 8080

---

**Last Updated**: July 31, 2025  
**Robot Version**: Ruohobot v1.0  
**Tested On**: Raspberry Pi OS with Python 3.11
