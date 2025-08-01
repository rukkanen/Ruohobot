#!/usr/bin/env python3
"""
GPIO reset and recovery script
"""

import RPi.GPIO as GPIO
import time

print("=== GPIO Reset and Recovery ===")

print("1. Aggressive GPIO cleanup...")
try:
    GPIO.cleanup()
    print("   ✓ GPIO cleanup completed")
except Exception as e:
    print(f"   Warning: {e}")

print("2. Resetting GPIO mode...")
try:
    GPIO.setmode(GPIO.BCM)
    print("   ✓ GPIO mode set to BCM")
except Exception as e:
    print(f"   Error: {e}")

print("3. Testing and resetting pin 17...")
try:
    # Try different configurations to unstick the pin
    GPIO.setup(17, GPIO.OUT)
    GPIO.output(17, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(17, GPIO.LOW)
    time.sleep(0.1)
    print("   ✓ Pin 17 output test completed")
    
    # Now set it back to input
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    time.sleep(0.1)
    state = GPIO.input(17)
    print(f"   Pin 17 state after reset: {state}")
    
    # Test edge detection
    GPIO.add_event_detect(17, GPIO.BOTH)
    print("   ✓ Pin 17 edge detection working")
    GPIO.remove_event_detect(17)
    
except Exception as e:
    print(f"   Error: {e}")

print("4. Testing pin 27...")
try:
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    state = GPIO.input(27)
    print(f"   Pin 27 state: {state}")
    
    GPIO.add_event_detect(27, GPIO.BOTH)
    print("   ✓ Pin 27 edge detection working")
    GPIO.remove_event_detect(27)
    
except Exception as e:
    print(f"   Error: {e}")

print("5. Final cleanup...")
GPIO.cleanup()
print("   ✓ GPIO cleanup completed")

print("=== Reset Complete ===")
