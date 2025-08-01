#!/bin/bash
# Run this script to test the IMU (GY-521/MPU-6050) on Raspberry Pi
set -e

sudo ./venv/bin/python3 ./scripts/imu_tester.py
