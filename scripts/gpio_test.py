#!/usr/bin/env python3
"""
Simple GPIO test for encoder pins 17 and 27
Tests basic GPIO setup and edge detection
"""

import time
import sys

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("RPi.GPIO library not found. Install with: pip install RPi.GPIO")
    sys.exit(1)

# Encoder pins from config
LEFT_ENCODER_PIN = 12
RIGHT_ENCODER_PIN = 27

# Counters
left_count = 0
right_count = 0

def left_callback(channel):
    global left_count
    left_count += 1
    print(f"Left encoder pulse: {left_count}")

def right_callback(channel):
    global right_count
    right_count += 1
    print(f"Right encoder pulse: {right_count}")

def test_gpio_basic():
    """Test basic GPIO setup without edge detection"""
    print("=== Basic GPIO Setup Test ===")
    
    try:
        GPIO.setmode(GPIO.BCM)
        print("✓ GPIO.setmode(GPIO.BCM) successful")
        
        # Test pin setup
        GPIO.setup(LEFT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"✓ GPIO.setup(pin {LEFT_ENCODER_PIN}) successful")
        
        GPIO.setup(RIGHT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"✓ GPIO.setup(pin {RIGHT_ENCODER_PIN}) successful")
        
        # Read pin states
        left_state = GPIO.input(LEFT_ENCODER_PIN)
        right_state = GPIO.input(RIGHT_ENCODER_PIN)
        print(f"✓ Pin {LEFT_ENCODER_PIN} state: {left_state}")
        print(f"✓ Pin {RIGHT_ENCODER_PIN} state: {right_state}")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic GPIO setup failed: {e}")
        return False

def test_edge_detection():
    """Test GPIO edge detection setup"""
    print("\n=== Edge Detection Test ===")
    
    try:
        # Test left encoder edge detection
        GPIO.add_event_detect(LEFT_ENCODER_PIN, GPIO.BOTH, callback=left_callback)
        print(f"✓ Edge detection on pin {LEFT_ENCODER_PIN} successful")
        
        # Test right encoder edge detection  
        GPIO.add_event_detect(RIGHT_ENCODER_PIN, GPIO.BOTH, callback=right_callback)
        print(f"✓ Edge detection on pin {RIGHT_ENCODER_PIN} successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Edge detection setup failed: {e}")
        return False

def test_pin_conflicts():
    """Check for potential pin conflicts"""
    print("\n=== Pin Conflict Check ===")
    
    # Check if pins are already in use
    try:
        # This will fail if pins are already set up
        GPIO.setup(LEFT_ENCODER_PIN, GPIO.IN)
        print(f"Pin {LEFT_ENCODER_PIN}: Available")
    except Exception as e:
        print(f"Pin {LEFT_ENCODER_PIN}: May be in use - {e}")
    
    try:
        GPIO.setup(RIGHT_ENCODER_PIN, GPIO.IN)
        print(f"Pin {RIGHT_ENCODER_PIN}: Available")
    except Exception as e:
        print(f"Pin {RIGHT_ENCODER_PIN}: May be in use - {e}")

def main():
    print("GPIO Edge Detection Test Script")
    print("Testing encoder pins 17 and 27")
    print("=" * 40)
    
    # Clean up any previous GPIO state
    GPIO.cleanup()
    print("✓ GPIO cleanup completed")
    
    # Test basic GPIO functionality
    if not test_gpio_basic():
        print("\n❌ Basic GPIO test failed. Check permissions and hardware.")
        GPIO.cleanup()
        return
    
    # Test edge detection
    if not test_edge_detection():
        print("\n❌ Edge detection test failed.")
        GPIO.cleanup()
        return
    
    print("\n🎉 All tests passed! Monitoring for 10 seconds...")
    print("Manually trigger encoders to see pulses...")
    
    # Monitor for 10 seconds
    start_time = time.time()
    try:
        while time.time() - start_time < 10:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    print(f"\nFinal counts: Left={left_count}, Right={right_count}")
    GPIO.cleanup()
    print("✓ GPIO cleanup completed")

if __name__ == "__main__":
    main()
