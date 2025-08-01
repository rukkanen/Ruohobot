#!/usr/bin/env python3
"""
Test script using the robot's actual Encoder class
"""

import sys
import os

# Add src directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("RPi.GPIO library not found. Install with: pip install RPi.GPIO")
    exit(1)

from core.encoder import Encoder

def main():
    print("Testing robot's Encoder class directly")
    print("=" * 40)
    
    # Clean up any previous GPIO state
    GPIO.cleanup()
    print("✓ GPIO cleanup completed")
    
    try:
        # Test left encoder (pin 17)
        print(f"\nTesting left encoder on pin 17...")
        left_encoder = Encoder(pin=17, pulses_per_rev=20, wheel_diameter=0.065)
        print("✓ Left encoder created successfully")
        
        # Test right encoder (pin 27)
        print(f"\nTesting right encoder on pin 27...")
        right_encoder = Encoder(pin=27, pulses_per_rev=20, wheel_diameter=0.065)
        print("✓ Right encoder created successfully")
        
        print("\n🎉 Both encoders initialized successfully!")
        print("Monitor for 5 seconds...")
        
        import time
        start_time = time.time()
        while time.time() - start_time < 5:
            left_count = left_encoder.get_count()
            right_count = right_encoder.get_count()
            print(f"Left: {left_count}, Right: {right_count}", end='\r')
            time.sleep(0.1)
        
        print(f"\nFinal - Left: {left_encoder.get_count()}, Right: {right_encoder.get_count()}")
        
        # Cleanup
        left_encoder.cleanup()
        right_encoder.cleanup()
        
    except Exception as e:
        print(f"❌ Encoder test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        GPIO.cleanup()
        print("\n✓ GPIO cleanup completed")

if __name__ == "__main__":
    main()
