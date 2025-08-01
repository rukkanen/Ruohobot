#!/usr/bin/env python3
"""
Simple Motor Test Script for Ruohobot M3H550

This script allows you to quickly test your Pololu M3H550 motor controller
without running the full robot stack.
"""

import sys
import time
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.motors import MotorController


def setup_logging():
    """Setup simple logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # Ensure debug is off for less spam
    logging.getLogger().setLevel(logging.INFO)


def test_motor_controller():
    """Test the motor controller functionality"""
    print("=== Ruohobot M3H550 Motor Test ===")
    print("This script will test your Pololu M3H550 motor controller")
    print("Make sure your robot is secure and motors are safe to run!")
    print()
    
    # Simple configuration for testing
    config = {
        'pololu_m3h550': {
            'i2c_bus': 1,                    # Standard I2C bus on Raspberry Pi
            'i2c_address': 16,               # Default Motoron address (detected at 0x10)
            'max_speed': 400,                # Conservative speed for testing
            'motor_1_acceleration': 100,     # Gentle acceleration
            'motor_1_deceleration': 200,
            'motor_2_acceleration': 100,
            'motor_2_deceleration': 200,
            'motor_3_acceleration': 100,
            'motor_3_deceleration': 200,
        }
    }
    
    try:
        # Initialize motor controller
        print("Initializing motor controller...")
        mc = MotorController(config)
        print("✓ Motor controller initialized successfully!")
        print()
        
        # Get initial status
        status = mc.get_status()
        print("Initial status:")
        for key, value in status.items():
            if key != 'motoron_status_flags':  # Skip raw status flags
                print(f"  {key}: {value}")
        print()
        
        # Interactive test menu
        while True:
            print("\n=== Motor Test Menu ===")
            print("1. Test individual motor")
            print("2. Test all motors sequentially")
            print("3. Manual motor control")
            print("4. Test differential drive")
            print("5. Show motor status")
            print("6. Emergency stop")
            print("7. Reset emergency stop")
            print("8. Exit")
            print()
            
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == '1':
                test_individual_motor(mc)
            elif choice == '2':
                test_all_motors_sequential(mc)
            elif choice == '3':
                manual_motor_control(mc)
            elif choice == '4':
                test_differential_drive(mc)
            elif choice == '5':
                show_motor_status(mc)
            elif choice == '6':
                mc.emergency_stop()
                print("✓ Emergency stop activated!")
            elif choice == '7':
                mc.reset_emergency_stop()
                print("✓ Emergency stop reset!")
            elif choice == '8':
                break
            else:
                print("Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your I2C connections and make sure the Motoron is powered and connected.")
    finally:
        try:
            if 'mc' in locals():
                mc.shutdown()
        except:
            pass
        print("\nTest completed. Motors stopped.")


def test_individual_motor(mc):
    """Test a single motor"""
    try:
        motor_id = int(input("Enter motor number (1, 2, or 3): "))
        if motor_id not in [1, 2, 3]:
            print("Invalid motor number!")
            return
        
        print(f"\nTesting motor {motor_id}...")
        print("Forward direction...")
        mc.set_speed(motor_id, 200)
        time.sleep(2)
        
        print("Stopping...")
        mc.set_speed(motor_id, 0)
        time.sleep(1)
        
        print("Reverse direction...")
        mc.set_speed(motor_id, -200)
        time.sleep(2)
        
        print("Stopping...")
        mc.set_speed(motor_id, 0)
        print(f"✓ Motor {motor_id} test complete!")
        
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"Error during motor test: {e}")


def test_all_motors_sequential(mc):
    """Test all motors one by one"""
    print("\nTesting all motors sequentially...")
    mc.test_motors()
    print("✓ All motor tests complete!")


def manual_motor_control(mc):
    """Manual motor control interface"""
    print("\nManual Motor Control")
    print("Enter motor commands in format: motor_id speed")
    print("Example: '1 300' sets motor 1 to speed 300")
    print("Speed range: -800 to +800")
    print("Enter 'stop' to stop all motors, 'quit' to exit")
    print()
    
    while True:
        try:
            cmd = input("Motor command: ").strip().lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'stop':
                mc.stop()
                print("✓ All motors stopped")
                continue
            
            parts = cmd.split()
            if len(parts) != 2:
                print("Invalid format. Use: motor_id speed")
                continue
            
            motor_id = int(parts[0])
            speed = int(parts[1])
            
            if motor_id not in [1, 2, 3]:
                print("Motor ID must be 1, 2, or 3")
                continue
            
            if abs(speed) > 800:
                print("Speed must be between -800 and +800")
                continue
            
            mc.set_speed(motor_id, speed)
            print(f"✓ Motor {motor_id} speed set to {speed}")
            
        except ValueError:
            print("Invalid input. Use numbers only.")
        except KeyboardInterrupt:
            print("\nExiting manual control...")
            break
        except Exception as e:
            print(f"Error: {e}")


def test_differential_drive(mc):
    """Test differential drive functionality"""
    print("\nTesting differential drive...")
    print("This assumes motors 1 and 2 are your drive wheels")
    
    movements = [
        ("Forward", 0.5, 0.0),
        ("Backward", -0.5, 0.0),
        ("Turn Left", 0.0, -0.5),
        ("Turn Right", 0.0, 0.5),
        ("Forward + Left", 0.3, -0.3),
        ("Forward + Right", 0.3, 0.3),
    ]
    
    for movement_name, linear, angular in movements:
        print(f"  {movement_name} (linear={linear}, angular={angular})...")
        mc.set_velocity(linear, angular)
        time.sleep(2)
        mc.stop()
        time.sleep(1)
    
    print("✓ Differential drive test complete!")


def show_motor_status(mc):
    """Display current motor status"""
    print("\n=== Motor Status ===")
    status = mc.get_status()
    
    for key, value in status.items():
        if key == 'current_speeds':
            print(f"{key}:")
            for motor_id, speed in value.items():
                print(f"  Motor {motor_id}: {speed}")
        elif key != 'motoron_status_flags':  # Skip raw status flags
            print(f"{key}: {value}")
    
    # Try to get motor currents
    print("\nMotor currents:")
    for motor_id in [1, 2, 3]:
        try:
            current = mc.get_motor_current(motor_id)
            print(f"  Motor {motor_id}: {current:.2f} (raw units)")
        except:
            print(f"  Motor {motor_id}: Not available")


if __name__ == "__main__":
    setup_logging()
    test_motor_controller()
