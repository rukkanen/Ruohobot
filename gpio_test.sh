#!/bin/bash
# GPIO Test Script for Encoder Pins 17 and 27

echo "GPIO Test for Ruohobot Encoders"
echo "================================"

# Navigate to project root
cd "$(dirname "$0")"

# Check if running as root (required for GPIO)
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script requires root privileges for GPIO access"
    echo "Run with: sudo $0"
    exit 1
fi

echo "✓ Running with root privileges"

# Run the GPIO test - use system python3 since we just need GPIO
echo "Running GPIO test..."
echo "--------------------"
python3 scripts/gpio_test.py
