#!/usr/bin/env python3
"""
Test to isolate which robot module import is causing GPIO interference
"""

import sys
import os
import RPi.GPIO as GPIO

# Add src directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

def test_pin17():
    """Test pin 17 GPIO functionality"""
    try:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        state = GPIO.input(17)
        print(f"  Pin 17 state: {state}")
        GPIO.add_event_detect(17, GPIO.BOTH)
        print(f"  Pin 17 edge detection: OK")
        GPIO.remove_event_detect(17)
        GPIO.cleanup()
        return True
    except Exception as e:
        print(f"  Pin 17 test failed: {e}")
        GPIO.cleanup()
        return False

print("=== GPIO Import Interference Test ===")

print("1. Testing pin 17 before any robot imports...")
test_pin17()

print("2. Importing utils.logger...")
from utils.logger import setup_logging
print("   Testing pin 17 after utils.logger import...")
test_pin17()

print("3. Importing core.config_manager...")
from core.config_manager import ConfigManager
print("   Testing pin 17 after config_manager import...")
test_pin17()

print("4. Importing core.motors...")
from core.motors import MotorController
print("   Testing pin 17 after motors import...")
test_pin17()

print("5. Importing core.sensors...")
from core.sensors import SensorManager
print("   Testing pin 17 after sensors import...")
test_pin17()

print("6. Importing core.external_modules...")
from core.external_modules import ExternalModuleManager
print("   Testing pin 17 after external_modules import...")
test_pin17()

print("7. Importing core.hardware_manager...")
from core.hardware_manager import HardwareManager
print("   Testing pin 17 after hardware_manager import...")
test_pin17()

print("8. Importing core.robot...")
from core.robot import Robot
print("   Testing pin 17 after robot import...")
test_pin17()

print("=== Test Complete ===")
