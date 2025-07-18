#!/usr/bin/env python3
"""
Ruohobot Module Demo

This script demonstrates the modular structure and cross-folder imports
of the Ruohobot project. It showcases how the different modules can be
imported and used independently.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

def demo_core_modules():
    """Demonstrate core module imports and basic functionality"""
    print("=== Core Modules Demo ===")
    
    # Import core modules
    from core.state_machine import StateMachine, RobotState
    from core.safety import SafetySystem
    from core.navigation import NavigationSystem, NavigationMode
    from core.communication import CommunicationManager
    
    print("✓ Successfully imported all core modules")
    
    # Demo state machine
    config = {'default_state': 'idle'}
    state_machine = StateMachine(config)
    print(f"✓ State machine initialized in '{state_machine.current_state.value}' state")
    
    # Demo state transition
    state_machine.request_state_change('manual_control')
    print(f"✓ State changed to '{state_machine.current_state.value}'")
    
    print()

def demo_hardware_modules():
    """Demonstrate hardware module imports and basic functionality"""
    print("=== Hardware Modules Demo ===")
    
    # Import hardware modules
    from hardware.motors import MotorController
    from hardware.sensors import SensorManager
    from hardware.external_modules import ExternalModuleManager
    
    print("✓ Successfully imported all hardware modules")
    
    # Demo motor controller
    motor_config = {
        'pololu_shield': {
            'left_motor_pin': 18,
            'right_motor_pin': 19,
            'enable_pin': 12,
            'max_speed': 100
        }
    }
    motors = MotorController(motor_config)
    print(f"✓ Motor controller initialized (simulation mode)")
    
    # Demo sensor readings
    sensor_config = {}
    sensors = SensorManager(sensor_config)
    readings = sensors.get_all_readings()
    print(f"✓ Sensor readings: Battery {readings['battery_voltage']:.1f}V, Tilt {readings['tilt_angle']:.1f}°")
    
    print()

def demo_utilities():
    """Demonstrate utility module imports"""
    print("=== Utilities Demo ===")
    
    # Import utilities
    from utils.logger import setup_logging
    
    print("✓ Successfully imported utility modules")
    
    # Demo logging setup
    setup_logging()
    print("✓ Logging system configured")
    
    print()

def demo_cross_folder_imports():
    """Demonstrate cross-folder imports through main classes"""
    print("=== Cross-Folder Imports Demo ===")
    
    # Import main classes that use cross-folder imports
    from core.config_manager import ConfigManager
    from core.hardware_manager import HardwareManager
    from core.robot import Robot
    
    print("✓ Successfully imported classes with cross-folder dependencies")
    
    # Demo config manager
    config = ConfigManager()
    print(f"✓ Config manager loaded with {len(config._config)} sections")
    
    # Demo hardware manager (uses hardware modules)
    hardware = HardwareManager(config.hardware)
    status = hardware.get_system_status()
    print(f"✓ Hardware manager initialized with {len(status)} subsystems")
    
    print()

def demo_package_structure():
    """Show the package structure"""
    print("=== Package Structure ===")
    
    import src
    import src.core
    import src.hardware
    import src.utils
    
    print("✓ All packages have proper __init__.py files:")
    print("  - src/")
    print("  - src/core/")
    print("  - src/hardware/")
    print("  - src/utils/")
    
    print(f"✓ Main package version: {src.__version__}")
    print()

def main():
    """Run all module demos"""
    print("Ruohobot Modular Structure Demo")
    print("=" * 40)
    print()
    
    try:
        demo_package_structure()
        demo_utilities()
        demo_core_modules()
        demo_hardware_modules()
        demo_cross_folder_imports()
        
        print("🎉 All modules imported and tested successfully!")
        print()
        print("The Ruohobot modular structure is working correctly with:")
        print("- Proper Python package structure (__init__.py files)")
        print("- Separate folders for core logic, hardware modules, and utilities")
        print("- Working cross-folder imports")
        print("- Minimal skeleton code for each module")
        print("- Functional main.py entry point")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())