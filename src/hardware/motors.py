"""
Motor Controller

Controls robot motors including differential drive for movement.
"""

import logging
import time
from typing import Dict, Any, Optional
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available - running in simulation mode")


class MotorController:
    """
    Controls robot motors using Pololu motor shield on Raspberry Pi.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize motor controller.
        
        Args:
            config: Motor configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Motor configuration
        pololu_config = config.get('pololu_shield', {})
        self.left_motor_pin = pololu_config.get('left_motor_pin', 18)
        self.right_motor_pin = pololu_config.get('right_motor_pin', 19)
        self.enable_pin = pololu_config.get('enable_pin', 12)
        self.max_speed = pololu_config.get('max_speed', 100)
        
        # Current motor state
        self.current_speed = 0.0
        self.current_direction = 0.0
        self.enabled = True
        self.emergency_stopped = False
        
        # Initialize GPIO if available
        if GPIO_AVAILABLE:
            self._initialize_gpio()
        else:
            self.logger.warning("Motor controller running in simulation mode")
        
        self.logger.info("Motor controller initialized")
    
    def _initialize_gpio(self):
        """Initialize GPIO pins for motor control"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.left_motor_pin, GPIO.OUT)
            GPIO.setup(self.right_motor_pin, GPIO.OUT)
            GPIO.setup(self.enable_pin, GPIO.OUT)
            
            # Initialize PWM
            self.left_pwm = GPIO.PWM(self.left_motor_pin, 1000)  # 1kHz
            self.right_pwm = GPIO.PWM(self.right_motor_pin, 1000)
            
            self.left_pwm.start(0)
            self.right_pwm.start(0)
            
            # Enable motor shield
            GPIO.output(self.enable_pin, GPIO.HIGH)
            
            self.logger.info("GPIO initialized for motor control")
            
        except Exception as e:
            self.logger.error(f"Error initializing GPIO: {e}")
            self.enabled = False
    
    def set_velocity(self, speed: float, direction: float):
        """
        Set motor velocity using differential drive.
        
        Args:
            speed: Forward/backward speed (-1.0 to 1.0)
            direction: Turn direction (-1.0 left to 1.0 right)
        """
        if self.emergency_stopped:
            self.logger.warning("Cannot set velocity - emergency stop active")
            return
        
        if not self.enabled:
            self.logger.warning("Cannot set velocity - motors disabled")
            return
        
        # Clamp values
        speed = max(-1.0, min(1.0, speed))
        direction = max(-1.0, min(1.0, direction))
        
        # Calculate differential drive
        left_speed = speed + direction
        right_speed = speed - direction
        
        # Normalize if either speed exceeds limits
        max_motor_speed = max(abs(left_speed), abs(right_speed))
        if max_motor_speed > 1.0:
            left_speed /= max_motor_speed
            right_speed /= max_motor_speed
        
        # Update current state
        self.current_speed = speed
        self.current_direction = direction
        
        # Set motor speeds
        self._set_motor_speeds(left_speed, right_speed)
        
        self.logger.debug(f"Motor velocity set: speed={speed:.2f}, direction={direction:.2f}")
    
    def _set_motor_speeds(self, left_speed: float, right_speed: float):
        """
        Set individual motor speeds.
        
        Args:
            left_speed: Left motor speed (-1.0 to 1.0)
            right_speed: Right motor speed (-1.0 to 1.0)
        """
        if not GPIO_AVAILABLE:
            # Simulation mode
            self.logger.debug(f"SIM: Left motor: {left_speed:.2f}, Right motor: {right_speed:.2f}")
            return
        
        try:
            # Convert to PWM duty cycle (0-100)
            left_duty = abs(left_speed) * self.max_speed
            right_duty = abs(right_speed) * self.max_speed
            
            # Set PWM duty cycles
            self.left_pwm.ChangeDutyCycle(left_duty)
            self.right_pwm.ChangeDutyCycle(right_duty)
            
            # Note: Direction control would typically require additional pins
            # for motor direction (forward/reverse). This is simplified.
            
        except Exception as e:
            self.logger.error(f"Error setting motor speeds: {e}")
    
    def stop(self):
        """Stop all motors"""
        self.current_speed = 0.0
        self.current_direction = 0.0
        self._set_motor_speeds(0.0, 0.0)
        self.logger.debug("Motors stopped")
    
    def emergency_stop(self):
        """Emergency stop - immediately halt all movement"""
        self.logger.critical("MOTOR EMERGENCY STOP")
        self.emergency_stopped = True
        self.stop()
        
        if GPIO_AVAILABLE:
            try:
                # Disable motor shield
                GPIO.output(self.enable_pin, GPIO.LOW)
            except Exception as e:
                self.logger.error(f"Error in emergency stop: {e}")
    
    def reset_emergency_stop(self):
        """Reset emergency stop state"""
        if self.emergency_stopped:
            self.logger.info("Motor emergency stop reset")
            self.emergency_stopped = False
            
            if GPIO_AVAILABLE:
                try:
                    # Re-enable motor shield
                    GPIO.output(self.enable_pin, GPIO.HIGH)
                except Exception as e:
                    self.logger.error(f"Error resetting emergency stop: {e}")
    
    def is_healthy(self) -> bool:
        """
        Check if motor controller is healthy.
        
        Returns:
            True if motor controller is functioning properly
        """
        if self.emergency_stopped:
            return False
        
        if not self.enabled:
            return False
        
        # Add additional health checks here (current monitoring, etc.)
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get motor controller status.
        
        Returns:
            Dictionary with motor status information
        """
        return {
            'enabled': self.enabled,
            'emergency_stopped': self.emergency_stopped,
            'current_speed': self.current_speed,
            'current_direction': self.current_direction,
            'gpio_available': GPIO_AVAILABLE,
            'healthy': self.is_healthy()
        }
    
    def shutdown(self):
        """Shutdown motor controller"""
        self.logger.info("Shutting down motor controller...")
        
        # Stop all motors
        self.stop()
        
        if GPIO_AVAILABLE:
            try:
                # Stop PWM
                self.left_pwm.stop()
                self.right_pwm.stop()
                
                # Disable motor shield
                GPIO.output(self.enable_pin, GPIO.LOW)
                
                # Cleanup GPIO
                GPIO.cleanup()
                
            except Exception as e:
                self.logger.error(f"Error during motor controller shutdown: {e}")
        
        self.logger.info("Motor controller shutdown complete")