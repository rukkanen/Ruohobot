#!/usr/bin/env python3
"""
Step-by-step robot initialization test to isolate GPIO interference
"""

import sys
import os

# Add src directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

def test_gpio_basic():
    """Test basic GPIO before any robot imports"""
    print("=== Step 1: Basic GPIO Test ===")
    import RPi.GPIO as GPIO
    try:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(12, GPIO.BOTH)
        print("✓ Basic GPIO edge detection works")
        GPIO.remove_event_detect(12)
        GPIO.cleanup()
        return True
    except Exception as e:
        print(f"❌ Basic GPIO failed: {e}")
        GPIO.cleanup()
        return False

def test_after_logging():
    """Test GPIO after importing logging"""
    print("\n=== Step 2: After Logging Import ===")
    from utils.logger import setup_logging
    setup_logging()
    
    import RPi.GPIO as GPIO
    try:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(12, GPIO.BOTH)
        print("✓ GPIO works after logging import")
        GPIO.remove_event_detect(12)
        GPIO.cleanup()
        return True
    except Exception as e:
        print(f"❌ GPIO failed after logging: {e}")
        GPIO.cleanup()
        return False

def test_after_config():
    """Test GPIO after importing config manager"""
    print("\n=== Step 3: After Config Import ===")
    from core.config_manager import ConfigManager
    config = ConfigManager()
    
    import RPi.GPIO as GPIO
    try:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(12, GPIO.BOTH)
        print("✓ GPIO works after config import")
        GPIO.remove_event_detect(12)
        GPIO.cleanup()
        return True
    except Exception as e:
        print(f"❌ GPIO failed after config: {e}")
        GPIO.cleanup()
        return False

def test_with_robot_encoder():
    """Test using the robot's actual Encoder class"""
    print("\n=== Step 4: Robot Encoder Class ===")
    from core.encoder import Encoder
    
    try:
        encoder = Encoder(pin=12, pulses_per_rev=20, wheel_diameter=0.065)
        print("✓ Robot Encoder class works")
        encoder.cleanup()
        return True
    except Exception as e:
        print(f"❌ Robot Encoder class failed: {e}")
        import RPi.GPIO as GPIO
        GPIO.cleanup()
        return False

def test_with_hardware_manager():
    """Test with full hardware manager"""
    print("\n=== Step 5: Hardware Manager ===")
    from core.config_manager import ConfigManager
    from core.hardware_manager import HardwareManager
    
    try:
        config = ConfigManager()
        hardware = HardwareManager(config.hardware)
        print("✓ Hardware manager works")
        if hardware.sensors.left_encoder:
            print("✓ Left encoder created successfully")
        else:
            print("❌ Left encoder not created")
        return True
    except Exception as e:
        print(f"❌ Hardware manager failed: {e}")
        return False

if __name__ == "__main__":
    print("GPIO Interference Detection Test")
    print("=" * 40)
    
    results = []
    results.append(("Basic GPIO", test_gpio_basic()))
    results.append(("After Logging", test_after_logging()))
    results.append(("After Config", test_after_config()))
    results.append(("Robot Encoder", test_with_robot_encoder()))
    results.append(("Hardware Manager", test_with_hardware_manager()))
    
    print("\n" + "=" * 40)
    print("RESULTS:")
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")
    
    # Find where it breaks
    fail_point = None
    for i, (name, result) in enumerate(results):
        if not result:
            fail_point = name
            break
    
    if fail_point:
        print(f"\n🎯 GPIO breaks at: {fail_point}")
    else:
        print("\n🤔 All tests passed - issue may be timing-related")
