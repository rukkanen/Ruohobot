# Encoder and Motor Tester for Ruohobot

This script helps you verify that your wheel encoders and motors are working correctly on your Raspberry Pi robot.

## Features
- Spins both wheels forward for 5 seconds using the Pololu Motoron M3H550 controller (via I2C)
- Reads encoder pulses from two GPIO pins (default: GPIO17 for left, GPIO27 for right)
- Prints encoder counts in real time
- Uses your robot's actual motor controller, not direct GPIO for motor control

## Wiring
- **Left Encoder OUT** → GPIO17 (physical pin 11)
- **Right Encoder OUT** → GPIO27 (physical pin 13)
- **Encoder VCC** → 3.3V (never 5V)
- **Encoder GND** → GND
- Motor control is handled by the Motoron M3H550 via I2C (no direct GPIO motor pins needed)
- Make sure to connect VCC and GND as required by your sensors and motors.

## Usage
1. Place your robot on a safe surface.
2. Run the script as root, using your venv's python:
   ```bash
   sudo /home/lapanen/git/Ruohobot/.venv/bin/python scripts/encoder_tester.py
   ```
3. The script will spin both wheels and print encoder counts. After 5 seconds, it will stop the motors and show the final counts.

## Customization
- If your encoders are connected to different pins, edit `LEFT_ENCODER_PIN` and `RIGHT_ENCODER_PIN` in the script.
- Motor control is handled by the Motoron controller config in `config/robot_config.yaml`.

## Safety
- Ensure your robot is secure and will not fall or collide with anything during the test.
- Motors will run at full power for 5 seconds by default.

---

For more details or troubleshooting, see the comments in `scripts/encoder_tester.py`.
