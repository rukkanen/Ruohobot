#!/usr/bin/env python3
"""
Test which robot import causes GPIO issues
"""

import RPi.GPIO as GPIO
import sys
import os

# Add src/ to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

def test_gpio_after_import(import_name, import_statement):
    """Test GPIO after a specific import"""
    print(f"\n=== Testing after importing {import_name} ===")
    
    try:
        # Execute the import
        exec(import_statement)
        print(f"✓ Import successful: {import_name}")
    except Exception as e:
        print(f"❌ Import failed: {import_name} - {e}")
        return False
    
    # Test GPIO
    try:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(12, GPIO.BOTH)
        GPIO.remove_event_detect(12)
        GPIO.cleanup()
        print(f"✓ GPIO test passed after {import_name}")
        return True
    except Exception as e:
        print(f"❌ GPIO test failed after {import_name}: {e}")
        GPIO.cleanup()
        return False

# Test imports one by one
imports_to_test = [
    ("yaml", "import yaml"),
    ("core.motors", "from core.motors import MotorController"),
    ("core.config_manager", "from core.config_manager import ConfigManager"),
    ("core.encoder", "from core.encoder import Encoder"),
]

print("Testing which robot import breaks GPIO...")

# Initial GPIO test
print("=== Initial GPIO test (no imports) ===")
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
try:
    GPIO.add_event_detect(12, GPIO.BOTH)
    GPIO.remove_event_detect(12)
    print("✓ Initial GPIO test passed")
except Exception as e:
    print(f"❌ Initial GPIO test failed: {e}")
GPIO.cleanup()

# Test each import
for import_name, import_statement in imports_to_test:
    test_gpio_after_import(import_name, import_statement)

print("\n=== Test Complete ===")
