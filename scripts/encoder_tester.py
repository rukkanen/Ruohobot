#!/usr/bin/env python3
"""
Encoder and Motor Tester for Ruohobot
- Spins both wheels forward for 5 seconds using the Pololu Motoron M3H550 controller
- Reads encoder pulses from GPIO17 (left) and GPIO27 (right)
- Prints encoder counts in real time

sudo /home/lapanen/git/Ruohobot/.venv/bin/python ./scripts/encoder_tester.py

"""

import RPi.GPIO as GPIO
import time
import sys
import os

# Add src/ to sys.path to import robot modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from core.motors import MotorController
import yaml

# Pin assignments (BCM numbering)
LEFT_ENCODER_PIN = 17
RIGHT_ENCODER_PIN = 27

left_count = 0
right_count = 0

def left_encoder_callback(channel):
    global left_count
    left_count += 1

def right_encoder_callback(channel):
    global right_count
    right_count += 1

def setup_encoders():
    print("Setting up GPIO for encoders...")
    GPIO.setmode(GPIO.BCM)
    print("Using BCM GPIO numbering")
    # Test left encoder pin
    try:
        GPIO.setup(LEFT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"GPIO.setup(LEFT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)")
        GPIO.add_event_detect(LEFT_ENCODER_PIN, GPIO.FALLING, callback=left_encoder_callback)
        print(f"[OK] Edge detection set up on LEFT_ENCODER_PIN (GPIO{LEFT_ENCODER_PIN})")
    except Exception as e:
        print(f"[ERROR] Failed to set up LEFT_ENCODER_PIN (GPIO{LEFT_ENCODER_PIN}): {e}")
        print("  - Check wiring: OUT -> GPIO, VCC -> 3.3V, GND -> GND")
        print("  - Try a different GPIO pin or disconnect the encoder and use a jumper from GND to GPIO.")
        raise

    # Test right encoder pin
    try:
        GPIO.setup(RIGHT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(RIGHT_ENCODER_PIN, GPIO.FALLING, callback=right_encoder_callback)
        print(f"[OK] Edge detection set up on RIGHT_ENCODER_PIN (GPIO{RIGHT_ENCODER_PIN})")
    except Exception as e:
        print(f"[ERROR] Failed to set up RIGHT_ENCODER_PIN (GPIO{RIGHT_ENCODER_PIN}): {e}")
        print("  - Check wiring: OUT -> GPIO, VCC -> 3.3V, GND -> GND")
        print("  - Try a different GPIO pin or disconnect the encoder and use a jumper from GND to GPIO.")
        raise

def load_motor_config():
    # Try to load config/robot_config.yaml for motor controller config
    config_path = os.path.join(ROOT_DIR, 'config', 'robot_config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('motors', {})
    return {}


def main():
    setup_encoders()
    print("Initializing Motoron M3H550 motor controller...")
    motor_config = load_motor_config()
    try:
        motors = MotorController({'pololu_m3h550': motor_config})
    except Exception as e:
        print(f"Failed to initialize MotorController: {e}")
        GPIO.cleanup()
        return
    print("Starting motors and counting encoder pulses for 5 seconds...")
    motors.set_velocity(0.5, 0.0)  # Forward, moderate speed
    start_time = time.time()
    try:
        while time.time() - start_time < 5:
            print(f"Left: {left_count}  Right: {right_count}", end='\r')
            time.sleep(0.1)
    finally:
        motors.stop()
        GPIO.cleanup()
        print(f"\nFinal counts - Left: {left_count}  Right: {right_count}")

if __name__ == "__main__":
    main()
