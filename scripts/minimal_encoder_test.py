#!/usr/bin/env python3
"""
Minimal encoder test without robot imports
"""

import RPi.GPIO as GPIO
import time

# Use BCM numbering - pins from robot_config.yaml
LEFT_ENCODER_PIN = 12
RIGHT_ENCODER_PIN = 27

left_count = 0
right_count = 0

def left_encoder_callback(channel):
    global left_count
    left_count += 1
    print(f"Left encoder pulse: {left_count}")

def right_encoder_callback(channel):
    global right_count
    right_count += 1
    print(f"Right encoder pulse: {right_count}")

def setup_encoders():
    print("Setting up GPIO for encoders...")
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(LEFT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(LEFT_ENCODER_PIN, GPIO.BOTH, callback=left_encoder_callback)
    print(f"[OK] Left encoder setup on GPIO{LEFT_ENCODER_PIN}")

    GPIO.setup(RIGHT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(RIGHT_ENCODER_PIN, GPIO.BOTH, callback=right_encoder_callback)
    print(f"[OK] Right encoder setup on GPIO{RIGHT_ENCODER_PIN}")

def main():
    GPIO.cleanup()  # Reset any old pin states
    setup_encoders()

    print("Monitoring encoders for 10 seconds...")
    print("Manually trigger encoders to see pulses...")
    
    start_time = time.time()
    try:
        while time.time() - start_time < 10:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        GPIO.cleanup()
        print(f"\nFinal counts - Left: {left_count}  Right: {right_count}")

if __name__ == "__main__":
    main()
