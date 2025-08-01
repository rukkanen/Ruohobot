#!/usr/bin/env python3
"""
GY-521 (MPU-6050) IMU Test Script for Ruohobot
Tests IMU initialization, data reading, and basic functionality.
"""

import time
import sys
import os

# Add src/ to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

try:
    from mpu6050 import mpu6050
except ImportError:
    print("❌ mpu6050 library not found.")
    print("Install with: sudo python3 -m pip install --break-system-packages mpu6050-raspberrypi")
    exit(1)

from core.imu import IMU
import yaml

# I2C address for GY-521
IMU_I2C_ADDRESS = 0x68

def load_imu_config():
    """Load IMU configuration from robot_config.yaml"""
    config_path = os.path.join(ROOT_DIR, 'config', 'robot_config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('hardware', {}).get('sensors', {}).get('imu', {})
    return {}

def test_raw_mpu6050():
    """Test raw MPU-6050 communication"""
    print("🔍 Testing raw MPU-6050 communication...")
    try:
        sensor = mpu6050(IMU_I2C_ADDRESS)
        
        # Test basic read
        accel = sensor.get_accel_data()
        gyro = sensor.get_gyro_data()
        temp = sensor.get_temp()
        
        if accel is None or gyro is None:
            print("❌ Failed to read IMU data")
            return False
        
        print(f"✅ Raw MPU-6050 communication successful")
        print(f"   Temperature: {temp:.1f}°C")
        print(f"   Accelerometer: X={accel['x']:.3f}, Y={accel['y']:.3f}, Z={accel['z']:.3f} g")
        print(f"   Gyroscope: X={gyro['x']:.3f}, Y={gyro['y']:.3f}, Z={gyro['z']:.3f} °/s")
        return True
    except Exception as e:
        print(f"❌ Raw MPU-6050 test failed: {e}")
        return False

def test_robot_imu_class():
    """Test the robot's IMU class"""
    print("\n🔍 Testing robot IMU class...")
    try:
        config = load_imu_config()
        i2c_addr = config.get('i2c_address', IMU_I2C_ADDRESS)
        
        imu = IMU(i2c_address=i2c_addr)
        
        # Test all methods
        accel = imu.get_accel()
        gyro = imu.get_gyro()
        all_data = imu.get_all()
        temp = imu.get_temperature()
        
        if accel is None or gyro is None:
            print("❌ Failed to read IMU data from robot class")
            return False
        
        print(f"✅ Robot IMU class working correctly")
        print(f"   I2C Address: 0x{i2c_addr:02X}")
        print(f"   Temperature: {temp:.1f}°C")
        print(f"   Accelerometer: X={accel['x']:.3f}, Y={accel['y']:.3f}, Z={accel['z']:.3f} g")
        print(f"   Gyroscope: X={gyro['x']:.3f}, Y={gyro['y']:.3f}, Z={gyro['z']:.3f} °/s")
        return True
    except Exception as e:
        print(f"❌ Robot IMU class test failed: {e}")
        return False

def test_tilt_detection():
    """Test basic tilt detection (Z-axis should be ~1g when upright)"""
    print("\n🔍 Testing tilt detection...")
    try:
        sensor = mpu6050(IMU_I2C_ADDRESS)
        accel = sensor.get_accel_data()
        
        if accel is None:
            print("❌ Failed to read accelerometer data")
            return False
        
        z_axis = accel['z']
        is_upright = abs(z_axis - 1.0) < 0.3  # Within 0.3g of 1g
        
        if is_upright:
            print(f"✅ Robot appears to be upright (Z-axis: {z_axis:.3f}g)")
        else:
            print(f"⚠️  Robot may be tilted (Z-axis: {z_axis:.3f}g, expected ~1.0g)")
        
        return True
    except Exception as e:
        print(f"❌ Tilt detection test failed: {e}")
        return False

def live_data_test():
    """Show live IMU data for 10 seconds"""
    print("\n📊 Live IMU data test (10 seconds)...")
    try:
        sensor = mpu6050(IMU_I2C_ADDRESS)
        start_time = time.time()
        
        print("    Time |  Accel X |  Accel Y |  Accel Z |  Gyro X |  Gyro Y |  Gyro Z | Temp")
        print("    -----|----------|----------|----------|---------|---------|---------|-----")
        
        while time.time() - start_time < 10:
            accel = sensor.get_accel_data()
            gyro = sensor.get_gyro_data()
            temp = sensor.get_temp()
            
            if accel is None or gyro is None:
                print("❌ Failed to read IMU data during live test")
                return False
            
            elapsed = time.time() - start_time
            print(f"  {elapsed:6.1f}s | {accel['x']:8.3f} | {accel['y']:8.3f} | {accel['z']:8.3f} | "
                  f"{gyro['x']:7.1f} | {gyro['y']:7.1f} | {gyro['z']:7.1f} | {temp:4.1f}°C")
            time.sleep(0.5)
        
        print("✅ Live data test completed")
        return True
    except KeyboardInterrupt:
        print("\n⚠️  Live data test interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Live data test failed: {e}")
        return False

def main():
    print("🤖 Ruohobot GY-521 IMU Test")
    print("=" * 40)
    
    # Test sequence
    tests = [
        test_raw_mpu6050,
        test_robot_imu_class, 
        test_tilt_detection,
        live_data_test
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📋 Test Summary: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All IMU tests passed! GY-521 is working correctly.")
    else:
        print("⚠️  Some tests failed. Check connections and I2C setup.")
        print("💡 Troubleshooting tips:")
        print("   - Verify GY-521 is connected to I2C (SDA/SCL)")
        print("   - Check I2C address with: sudo i2cdetect -y 1")
        print("   - Ensure IMU has power (3.3V/5V and GND)")
        print("   - Try running with sudo if permission issues")

if __name__ == "__main__":
    main()
