"""
Motor Controller for Pololu Motoron M3H550

Provides control interface for the M3H550 Triple Motor Controller for Raspberry Pi.
This module handles the low-level communication with the Motoron controller via I2C.
"""

import logging
import time
from typing import Dict, Any, Tuple
try:
    import motoron
except ImportError:
    motoron = None


class MotorController:
    """Motor controller interface for the Pololu Motoron M3H550"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the motor controller"""
        self.logger = logging.getLogger(__name__)
        self.config = config.get('pololu_m3h550', {})
        
        if motoron is None:
            self.logger.error("Motoron library not installed. Install with: pip install git+https://github.com/pololu/motoron-python.git")
            raise ImportError("Motoron library required for M3H550 motor controller")
        
        # Configuration parameters
        self.i2c_bus = self.config.get('i2c_bus', 1)
        self.i2c_address = self.config.get('i2c_address', 16)  # Default Motoron address
        self.max_speed = self.config.get('max_speed', 800)
        self.emergency_stop_active = False
        
        # Motor mapping configuration (Motor 2=Right, Motor 3=Left, Motor 1=Unused)
        self.motor_mapping = self.config.get('motor_mapping', {
            'left_motor': 3,
            'right_motor': 2,
            'unused_motor': 1
        })
        
        # Motor enabled/disabled status
        self.motor_enabled = {
            1: self.config.get('motor_1_enabled', True),
            2: self.config.get('motor_2_enabled', True),
            3: self.config.get('motor_3_enabled', True)
        }
        
        # Motor configuration
        self.motor_config = {
            1: {
                'max_acceleration': self.config.get('motor_1_acceleration', 140),
                'max_deceleration': self.config.get('motor_1_deceleration', 300),
                'reversed': self.config.get('motor_1_reversed', False)
            },
            2: {
                'max_acceleration': self.config.get('motor_2_acceleration', 140),
                'max_deceleration': self.config.get('motor_2_deceleration', 300),
                'reversed': self.config.get('motor_2_reversed', False)
            },
            3: {
                'max_acceleration': self.config.get('motor_3_acceleration', 140),
                'max_deceleration': self.config.get('motor_3_deceleration', 300),
                'reversed': self.config.get('motor_3_reversed', False)
            }
        }
        
        # Current motor speeds
        self.current_speeds = {1: 0, 2: 0, 3: 0}
        
        try:
            # Initialize Motoron controller
            self.mc = motoron.MotoronI2C(bus=self.i2c_bus, address=self.i2c_address)
            self._initialize_controller()
            # Only log on startup
        except Exception as e:
            self.logger.error(f"Failed to initialize motor controller: {e}")
            raise
    
    def _initialize_controller(self):
        """Initialize the Motoron controller with proper settings"""
        try:
            # Reset controller to default settings
            self.mc.reinitialize()
            
            # Disable CRC for simplicity (can be enabled later for robustness)
            self.mc.disable_crc()
            
            # Clear the reset flag
            self.mc.clear_reset_flag()
            
            # Configure command timeout (stop motors if no command for 1000ms)
            self.mc.set_command_timeout_milliseconds(1000)
            
            # Configure each motor
            for motor_id, config in self.motor_config.items():
                self.mc.set_max_acceleration(motor_id, config['max_acceleration'])
                self.mc.set_max_deceleration(motor_id, config['max_deceleration'])
            
            # Clear any motor faults
            self.mc.clear_motor_fault_unconditional()
            
            # Only log on startup
            
        except Exception as e:
            self.logger.error(f"Error during controller initialization: {e}")
            raise
    
    def set_speed(self, motor_id: int, speed: int):
        """
        Set speed for a specific motor
        
        Args:
            motor_id: Motor number (1, 2, or 3)
            speed: Speed from -800 to +800 (negative = reverse)
        """
        if motor_id not in [1, 2, 3]:
            self.logger.error(f"Invalid motor ID: {motor_id}. Must be 1, 2, or 3")
            return
        
        # Check if motor is enabled
        if not self.motor_enabled.get(motor_id, True):
            # Only log if debug
            return
        
        if self.emergency_stop_active:
            self.logger.warning("Emergency stop active, ignoring speed command")
            return
        
        # Clamp speed to valid range
        speed = max(-self.max_speed, min(self.max_speed, speed))
        
        # Apply motor reversal if configured
        if self.motor_config[motor_id]['reversed']:
            speed = -speed
        
        try:
            self.mc.set_speed(motor_id, speed)
            self.current_speeds[motor_id] = speed
            # Only log if debug
        except Exception as e:
            self.logger.error(f"Error setting motor {motor_id} speed: {e}")
    
    def set_all_speeds(self, speeds: Dict[int, int]):
        """
        Set speeds for multiple motors at once
        
        Args:
            speeds: Dictionary mapping motor_id to speed
        """
        for motor_id, speed in speeds.items():
            self.set_speed(motor_id, speed)
    
    def set_velocity(self, linear_speed: float, angular_speed: float):
        """
        Set robot velocity using differential drive kinematics
        
        Args:
            linear_speed: Forward/backward speed (-1.0 to 1.0)
            angular_speed: Turning speed (-1.0 to 1.0, negative = left)
        """
        # Only log if debug
        # Convert normalized speeds to motor speeds
        max_motor_speed = self.max_speed
        
        # Simple differential drive calculation
        left_speed = linear_speed - angular_speed
        right_speed = linear_speed + angular_speed
        
        # Normalize if speeds exceed maximum
        max_abs_speed = max(abs(left_speed), abs(right_speed))
        if max_abs_speed > 1.0:
            left_speed /= max_abs_speed
            right_speed /= max_abs_speed
        
        # Convert to motor speeds
        left_motor_speed = int(left_speed * max_motor_speed)
        right_motor_speed = int(right_speed * max_motor_speed)
        
        # Use motor mapping configuration (Motor 2=Right, Motor 3=Left, Motor 1=Unused)
        left_motor_id = self.motor_mapping.get('left_motor', 3)   # Motor 3
        right_motor_id = self.motor_mapping.get('right_motor', 2) # Motor 2
        
        # Only set speeds for enabled motors
        if self.motor_enabled.get(left_motor_id, True):
            self.set_speed(left_motor_id, left_motor_speed)
        
        if self.motor_enabled.get(right_motor_id, True):
            self.set_speed(right_motor_id, right_motor_speed)
        
        # Only log if debug
    
    def stop(self):
        """Stop all motors gradually (using deceleration limits)"""
        try:
            # Only stop enabled motors
            for motor_id in [1, 2, 3]:
                if self.motor_enabled.get(motor_id, True):
                    self.mc.set_speed(motor_id, 0)
                    self.current_speeds[motor_id] = 0
            # Only log on user request
        except Exception as e:
            self.logger.error(f"Error stopping motors: {e}")
    
    def emergency_stop(self):
        """Emergency stop - immediate halt of all motors"""
        self.emergency_stop_active = True
        try:
            # Set speeds to zero immediately (bypasses acceleration/deceleration)
            # Only stop enabled motors to avoid errors with disabled Motor 1
            for motor_id in [1, 2, 3]:
                if self.motor_enabled.get(motor_id, True):
                    self.mc.set_speed(motor_id, 0)
                    self.current_speeds[motor_id] = 0
            self.logger.critical("EMERGENCY STOP - All motors halted")
        except Exception as e:
            self.logger.error(f"Error during emergency stop: {e}")
    
    def reset_emergency_stop(self):
        """Reset emergency stop condition"""
        self.emergency_stop_active = False
        try:
            # Reinitialize controller to clear any error states
            self._initialize_controller()
            # Only log on user request
        except Exception as e:
            self.logger.error(f"Error resetting emergency stop: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current motor controller status"""
        try:
            # Get status from Motoron
            status_flags = self.mc.get_status_flags()
            
            # Check for various status conditions
            if motoron is not None:
                status = {
                    'emergency_stop_active': self.emergency_stop_active,
                    'current_speeds': self.current_speeds.copy(),
                    'motoron_status_flags': status_flags,
                    'protocol_error': bool(status_flags & (1 << motoron.STATUS_FLAG_PROTOCOL_ERROR)),
                    'crc_error': bool(status_flags & (1 << motoron.STATUS_FLAG_CRC_ERROR)),
                    'command_timeout': bool(status_flags & (1 << motoron.STATUS_FLAG_COMMAND_TIMEOUT)),
                    'motor_fault': bool(status_flags & (1 << motoron.STATUS_FLAG_MOTOR_FAULT_LATCHED)),
                    'no_power': bool(status_flags & (1 << motoron.STATUS_FLAG_NO_POWER_LATCHED)),
                    'reset_flag': bool(status_flags & (1 << motoron.STATUS_FLAG_RESET)),
                }
            else:
                status = {
                    'emergency_stop_active': self.emergency_stop_active,
                    'current_speeds': self.current_speeds.copy(),
                    'motoron_status_flags': status_flags,
                    'protocol_error': None,
                    'crc_error': None,
                    'command_timeout': None,
                    'motor_fault': None,
                    'no_power': None,
                    'reset_flag': None,
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting motor status: {e}")
            return {
                'emergency_stop_active': self.emergency_stop_active,
                'current_speeds': self.current_speeds.copy(),
                'error': str(e)
            }
    
    def get_motor_current(self, motor_id: int) -> float:
        """
        Get current consumption for a specific motor (if supported)
        
        Args:
            motor_id: Motor number (1, 2, or 3)
            
        Returns:
            Current in milliamps, or 0 if not available
        """
        try:
            # This feature may not be available on all Motoron variants
            processed = self.mc.get_current_sense_processed(motor_id)
            # Convert to milliamps (this conversion depends on the specific Motoron model)
            # For now, return the raw processed value
            return processed
        except Exception as e:
            # Only log if debug
            return 0.0
    
    def test_motors(self):
        """Test routine to verify motor operation"""
        # Only log on user request
        
        if self.emergency_stop_active:
            self.logger.warning("Cannot run test - emergency stop active")
            return
        
        try:
            # Test each motor individually
            for motor_id in [1, 2, 3]:
                # Only log on user request
                
                # Forward direction
                self.set_speed(motor_id, 200)
                time.sleep(1)
                
                # Stop
                self.set_speed(motor_id, 0)
                time.sleep(0.5)
                
                # Reverse direction
                self.set_speed(motor_id, -200)
                time.sleep(1)
                
                # Stop
                self.set_speed(motor_id, 0)
                time.sleep(0.5)
                
                # Only log on user request
            
            # Only log on user request
            
        except Exception as e:
            self.logger.error(f"Error during motor test: {e}")
            self.emergency_stop()
    
    def shutdown(self):
        """Graceful shutdown of motor controller"""
        # Only log on shutdown
        try:
            # Stop all motors
            self.stop()
            time.sleep(0.1)  # Give motors time to stop
            
            # Additional cleanup if needed
            # Only log on shutdown
        except Exception as e:
            self.logger.error(f"Error during motor controller shutdown: {e}")
