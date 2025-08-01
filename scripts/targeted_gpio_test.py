#!/usr/bin/env python3
"""
Targeted test to identify the exact point where GPIO edge detection fails in robot context
"""

import sys
import os

# Add src directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import RPi.GPIO as GPIO

def test_encoder_direct():
    """Test encoder creation without any robot imports"""
    print("=== Direct Encoder Test (no robot imports) ===")
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    
    # Test pin 17
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    state = GPIO.input(17)
    print(f"Pin 17 state: {state}")
    
    try:
        GPIO.add_event_detect(17, GPIO.BOTH)
        print("Pin 17 edge detection: OK")
        GPIO.remove_event_detect(17)
    except Exception as e:
        print(f"Pin 17 edge detection failed: {e}")
        return False
    
    GPIO.cleanup()
    return True

def test_encoder_with_robot_imports():
    """Test encoder creation after robot imports but before initialization"""
    print("\n=== Encoder Test with Robot Imports ===")
    
    # Import all robot modules
    print("Importing robot modules...")
    from utils.logger import setup_logging
    from core.config_manager import ConfigManager
    from core.encoder import Encoder
    
    # Setup minimal environment
    setup_logging()
    config = ConfigManager()
    
    GPIO.cleanup()
    
    try:
        print("Creating encoder instance...")
        encoder = Encoder(pin=17, pulses_per_rev=20, wheel_diameter=0.065)
        print("✓ Encoder created successfully")
        encoder.cleanup()
        GPIO.cleanup()
        return True
    except Exception as e:
        print(f"❌ Encoder creation failed: {e}")
        GPIO.cleanup()
        return False

def test_encoder_step_by_step():
    """Test encoder creation step by step to isolate the exact failure point"""
    print("\n=== Step-by-Step Encoder Creation ===")
    
    # Import encoder class
    from core.encoder import Encoder
    
    GPIO.cleanup()
    
    # Manually replicate encoder.__init__ steps
    print("1. Setting GPIO mode...")
    GPIO.setmode(GPIO.BCM)
    
    print("2. Setting up pin 17...")
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    state = GPIO.input(17)
    print(f"   Pin 17 state: {state}")
    
    print("3. Creating callback function...")
    def test_callback(channel):
        print(f"   Callback triggered on channel {channel}")
    
    print("4. Adding edge detection...")
    try:
        GPIO.add_event_detect(17, GPIO.BOTH, callback=test_callback)
        print("   ✓ Edge detection added successfully")
        
        print("5. Testing for 2 seconds...")
        import time
        time.sleep(2)
        
        print("6. Removing edge detection...")
        GPIO.remove_event_detect(17)
        print("   ✓ Edge detection removed successfully")
        
        GPIO.cleanup()
        return True
        
    except Exception as e:
        print(f"   ❌ Edge detection failed: {e}")
        import traceback
        traceback.print_exc()
        GPIO.cleanup()
        return False

# Run all tests
if __name__ == "__main__":
    result1 = test_encoder_direct()
    result2 = test_encoder_with_robot_imports()
    result3 = test_encoder_step_by_step()
    
    print(f"\n=== Results ===")
    print(f"Direct GPIO test: {'PASS' if result1 else 'FAIL'}")
    print(f"Robot imports test: {'PASS' if result2 else 'FAIL'}")
    print(f"Step-by-step test: {'PASS' if result3 else 'FAIL'}")
    
    if result1 and not result2:
        print("\n🎯 Issue is with robot module imports!")
    elif result2 and not result3:
        print("\n🎯 Issue is with manual encoder creation steps!")
    else:
        print("\n🤔 Results are inconsistent - may be a timing issue")
