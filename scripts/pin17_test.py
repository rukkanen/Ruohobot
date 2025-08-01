#!/usr/bin/env python3
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
print("Testing pin 17 directly...")

try:
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("Pin 17 setup: OK")
    
    state = GPIO.input(17)
    print(f"Pin 17 state: {state}")
    
    GPIO.add_event_detect(17, GPIO.BOTH)
    print("Pin 17 edge detection: OK")
    
    GPIO.remove_event_detect(17)
    print("Pin 17 cleanup: OK")
    
except Exception as e:
    print(f"Pin 17 test failed: {e}")
    import traceback
    traceback.print_exc()

finally:
    GPIO.cleanup()
    print("GPIO cleanup done")
