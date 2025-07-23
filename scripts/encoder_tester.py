#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import sys
import os

# Add src/ to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from core.motors import MotorController
import yaml

# Use BCM numbering
LEFT_ENCODER_PIN = 23
RIGHT_ENCODER_PIN = 24

left_count = 0
right_count = 0

def left_encoder_callback(channel):
    global left_count
    left_count += 1
    # Optional debug
    # print("LEFT encoder pulse")

def right_encoder_callback(channel):
    global right_count
    right_count += 1
    # Optional debug
    # print("RIGHT encoder pulse")

def setup_encoders():
    print("Setting up GPIO for encoders...")
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(LEFT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(LEFT_ENCODER_PIN, GPIO.BOTH, callback=left_encoder_callback)
    print(f"[OK] Left encoder setup on GPIO{LEFT_ENCODER_PIN}")

    #GPIO.setup(RIGHT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.add_event_detect(RIGHT_ENCODER_PIN, GPIO.BOTH, callback=right_encoder_callback)
    print(f"[OK] Right encoder setup on GPIO{RIGHT_ENCODER_PIN}")

def load_motor_config():
    config_path = os.path.join(ROOT_DIR, 'config', 'robot_config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('motors', {})
    return {}

def main():
    GPIO.cleanup()  # Reset any old pin states
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
    motors.set_velocity(0.5, 0.0)
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