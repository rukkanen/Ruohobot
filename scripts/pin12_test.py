#!/usr/bin/env python3
"""
Quick test for GPIO 12 edge detection
"""

import RPi.GPIO as GPIO
import time

print("Testing GPIO 12 edge detection...")

try:
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    
    # Test pin 12
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    state = GPIO.input(12)
    print(f"Pin 12 initial state: {state}")
    
    # Test edge detection
    def callback(channel):
        print(f"Pin {channel} triggered!")
    
    GPIO.add_event_detect(12, GPIO.BOTH, callback=callback)
    print("Edge detection added successfully!")
    
    print("Monitoring for 5 seconds...")
    time.sleep(5)
    
    GPIO.remove_event_detect(12)
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()

finally:
    GPIO.cleanup()
    print("GPIO cleanup done")
