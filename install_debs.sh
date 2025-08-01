#!/bin/bash
set -e

# Install core Python dependencies
venv/bin/pip install -U pip
venv/bin/pip install -r requirements.txt

# Install runtime dependencies
venv/bin/pip install flask opencv-python RPi.GPIO mpu6050-raspberrypi

# Install Pololu Motoron library from GitHub
venv/bin/pip install git+https://github.com/pololu/motoron-python.git

echo "All dependencies installed!"