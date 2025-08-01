#!/usr/bin/env python3
"""
Test which import is breaking GPIO edge detection
"""

import RPi.GPIO as GPIO
import time

def test_gpio_before_imports():
    """Test GPIO before any imports"""
    print("=== Testing GPIO BEFORE robot imports ===")
    try:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(12, GPIO.BOTH)
        print("✅ GPIO edge detection works BEFORE imports")
        GPIO.remove_event_detect(12)
        GPIO.cleanup()
        return True
    except Exception as e:
        print(f"❌ GPIO failed BEFORE imports: {e}")
        GPIO.cleanup()
        return False

def test_gpio_after_imports():
    """Test GPIO after robot imports"""
    print("\n=== Testing GPIO AFTER robot imports ===")
    
    # Add path and import modules
    import sys
    import os
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
    SRC_DIR = os.path.join(ROOT_DIR, 'src')
    if SRC_DIR not in sys.path:
        sys.path.insert(0, SRC_DIR)
    
    print("Importing robot modules...")
    from core.motors import MotorController
    import yaml
    
    try:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(12, GPIO.BOTH)
        print("✅ GPIO edge detection works AFTER imports")
        GPIO.remove_event_detect(12)
        GPIO.cleanup()
        return True
    except Exception as e:
        print(f"❌ GPIO failed AFTER imports: {e}")
        GPIO.cleanup()
        return False

if __name__ == "__main__":
    result1 = test_gpio_before_imports()
    result2 = test_gpio_after_imports()
    
    print(f"\n=== Results ===")
    print(f"Before imports: {'PASS' if result1 else 'FAIL'}")
    print(f"After imports: {'PASS' if result2 else 'FAIL'}")
    
    if result1 and not result2:
        print("🎯 CONFIRMED: Robot imports are breaking GPIO!")
    elif not result1:
        print("🤔 GPIO is broken even before imports")
    else:
        print("✅ GPIO works fine - issue is elsewhere")
