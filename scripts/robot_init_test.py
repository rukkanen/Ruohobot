#!/usr/bin/env python3
"""
Test script that mimics robot initialization sequence to isolate GPIO issue
"""

import sys
import os
import logging

# Add src directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Import robot modules in the same order as the robot
print("=== Robot Initialization Sequence Test ===")

print("1. Setting up logging...")
from utils.logger import setup_logging
setup_logging()
logging.getLogger("core.lidar").setLevel(logging.WARNING)
logging.getLogger("core.slam").setLevel(logging.WARNING)

print("2. Loading configuration...")
from core.config_manager import ConfigManager
config = ConfigManager()

print("3. Importing robot modules...")
from core.robot import Robot
from core.hardware_manager import HardwareManager
from core.sensors import SensorManager
from core.external_modules import ExternalModuleManager

print("4. Testing encoder creation directly...")
try:
    # Test creating encoders in the same way as SensorManager
    enc_cfg = config.hardware.get('sensors', {}).get('encoders', {})
    print(f"Encoder config: {enc_cfg}")
    
    if enc_cfg and 'left_pin' in enc_cfg and 'right_pin' in enc_cfg:
        print("5. Creating encoder instances...")
        from core.encoder import Encoder
        
        print("  Creating left encoder...")
        left_encoder = Encoder(
            pin=enc_cfg['left_pin'],
            pulses_per_rev=enc_cfg.get('pulses_per_rev', 20),
            wheel_diameter=enc_cfg.get('wheel_diameter', 0.065)
        )
        print("  ✓ Left encoder created successfully")
        
        print("  Creating right encoder...")
        right_encoder = Encoder(
            pin=enc_cfg['right_pin'],
            pulses_per_rev=enc_cfg.get('pulses_per_rev', 20),
            wheel_diameter=enc_cfg.get('wheel_diameter', 0.065)
        )
        print("  ✓ Right encoder created successfully")
        
        print("6. Testing encoder readings...")
        import time
        for i in range(5):
            left_count = left_encoder.get_count()
            right_count = right_encoder.get_count()
            print(f"  Counts: Left={left_count}, Right={right_count}")
            time.sleep(1)
        
        print("7. Cleaning up encoders...")
        left_encoder.cleanup()
        right_encoder.cleanup()
        print("  ✓ Cleanup complete")
        
    else:
        print("No encoder config found")
        
except Exception as e:
    print(f"❌ Encoder test failed: {e}")
    import traceback
    traceback.print_exc()

print("8. Testing full hardware manager...")
try:
    hardware = HardwareManager(config.hardware)
    print("✓ HardwareManager created successfully")
    
    if hardware.sensors.left_encoder:
        print("✓ Left encoder exists in HardwareManager")
    else:
        print("❌ Left encoder missing in HardwareManager")
        
    if hardware.sensors.right_encoder:
        print("✓ Right encoder exists in HardwareManager")
    else:
        print("❌ Right encoder missing in HardwareManager")
        
except Exception as e:
    print(f"❌ HardwareManager test failed: {e}")
    import traceback
    traceback.print_exc()

print("=== Test Complete ===")
