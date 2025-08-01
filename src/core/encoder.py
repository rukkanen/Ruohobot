"""
Encoder sensor class for Ruohobot
Counts pulses from Omron slit-wheel encoders using GPIO interrupts.
"""
import time
import threading
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

class Encoder:
    # Class variable to track if GPIO mode has been set
    _gpio_mode_set = False
    
    def __init__(self, pin, pulses_per_rev, wheel_diameter):
        if GPIO is None:
            raise ImportError("RPi.GPIO is required for encoder support on Raspberry Pi.")
        
        self.pin = pin
        self.pulses_per_rev = pulses_per_rev
        self.wheel_diameter = wheel_diameter
        self.count = 0
        self.last_time = time.time()
        self.lock = threading.Lock()
        
        # Only set GPIO mode once
        if not Encoder._gpio_mode_set:
            GPIO.setmode(GPIO.BCM)
            Encoder._gpio_mode_set = True
        
        # Setup pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Add edge detection with error handling and retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Small delay to let GPIO settle
                time.sleep(0.1)
                GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self._pulse_callback)
                break  # Success, exit retry loop
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise RuntimeError(f"Failed to add edge detection on pin {self.pin} after {max_retries} attempts: {e}")
                else:
                    # Retry after cleaning up
                    try:
                        GPIO.remove_event_detect(self.pin)
                    except:
                        pass
                    time.sleep(0.2)

    def _pulse_callback(self, channel):
        with self.lock:
            self.count += 1
            self.last_time = time.time()

    def get_count(self):
        with self.lock:
            return self.count

    def reset(self):
        with self.lock:
            self.count = 0

    def get_distance(self):
        # Distance = (count / pulses_per_rev) * (pi * diameter)
        with self.lock:
            revolutions = self.count / self.pulses_per_rev
        return revolutions * 3.141592653589793 * self.wheel_diameter

    def cleanup(self):
        if GPIO is not None:
            try:
                GPIO.remove_event_detect(self.pin)
            except Exception:
                # Ignore cleanup errors
                pass
