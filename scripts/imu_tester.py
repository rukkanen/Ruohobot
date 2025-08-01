#!/usr/bin/env python3
"""
Simple IMU Test Script for GY-521 (MPU-6050) on Raspberry Pi
Reads and prints accelerometer and gyroscope data.
"""

import time

try:
    from mpu6050 import mpu6050
except ImportError:
    print("mpu6050 library not found. Install with: pip install mpu6050-raspberrypi")
    exit(1)

def main():
    # Default I2C address for GY-521 is 0x68
    sensor = mpu6050(0x68)
    print("Reading IMU data (Ctrl+C to stop)...")
    try:
        while True:
            accel = sensor.get_accel_data()
            gyro = sensor.get_gyro_data()
            print(f"Accel: {accel} | Gyro: {gyro}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting IMU test.")

if __name__ == "__main__":
    main()
