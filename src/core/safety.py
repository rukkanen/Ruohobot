"""
Safety System

Monitors robot safety conditions and provides emergency stop functionality.
"""

import logging
import time
from typing import Dict, Any, Callable, Optional


class SafetySystem:
    """
    Robot safety monitoring and emergency stop system.
    """
    
    def __init__(self, config: Dict[str, Any], hardware_manager):
        """
        Initialize the safety system.
        
        Args:
            config: Safety configuration
            hardware_manager: Hardware manager instance
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.hardware = hardware_manager
        
        # Safety parameters
        self.emergency_stop_enabled = config.get('emergency_stop_enabled', True)
        self.max_tilt_angle = config.get('max_tilt_angle', 30.0)
        self.battery_low_threshold = config.get('battery_low_threshold', 11.0)
        
        # Safety state
        self.is_emergency_stop = False
        self.safety_violations = []
        
        # Callbacks
        self.emergency_callback: Optional[Callable] = None
        
        # Last check time
        self.last_safety_check = time.time()
        self.check_interval = 0.1  # 100ms safety check interval
        
        self.logger.info("Safety system initialized")
    
    def is_safe(self) -> bool:
        """
        Check if robot is in a safe state.
        
        Returns:
            True if robot is safe to operate
        """
        current_time = time.time()
        
        # Only check safety at specified interval
        if current_time - self.last_safety_check < self.check_interval:
            return not self.is_emergency_stop and len(self.safety_violations) == 0
        
        self.last_safety_check = current_time
        
        # Clear previous violations
        self.safety_violations.clear()
        
        # Check emergency stop
        if self.is_emergency_stop:
            return False
        
        # Check tilt angle
        if not self._check_tilt_safety():
            self.safety_violations.append("excessive_tilt")
        
        # Check battery level
        if not self._check_battery_safety():
            self.safety_violations.append("low_battery")
        
        # Check obstacle detection
        if not self._check_obstacle_safety():
            self.safety_violations.append("obstacle_detected")
        
        # Check hardware status
        if not self._check_hardware_safety():
            self.safety_violations.append("hardware_failure")
        
        # Log safety violations
        if self.safety_violations:
            self.logger.warning(f"Safety violations detected: {self.safety_violations}")
        
        return len(self.safety_violations) == 0
    
    def _check_tilt_safety(self) -> bool:
        """
        Check if robot tilt is within safe limits.
        
        Returns:
            True if tilt is safe
        """
        try:
            # Get tilt from IMU sensor (placeholder)
            tilt_angle = self.hardware.get_tilt_angle()
            if abs(tilt_angle) > self.max_tilt_angle:
                self.logger.warning(f"Excessive tilt detected: {tilt_angle}°")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error checking tilt safety: {e}")
            return False
    
    def _check_battery_safety(self) -> bool:
        """
        Check if battery level is safe.
        
        Returns:
            True if battery level is safe
        """
        try:
            battery_voltage = self.hardware.get_battery_voltage()
            if battery_voltage < self.battery_low_threshold:
                self.logger.warning(f"Low battery detected: {battery_voltage}V")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error checking battery safety: {e}")
            return False
    
    def _check_obstacle_safety(self) -> bool:
        """
        Check for immediate obstacles that require emergency stop.
        
        Returns:
            True if no immediate obstacles
        """
        try:
            # Get distance readings from sensors
            distances = self.hardware.get_distance_readings()
            
            # Check for very close obstacles (emergency stop distance)
            emergency_distance = 0.1  # 10cm emergency stop distance
            
            for direction, distance in distances.items():
                if distance < emergency_distance:
                    self.logger.warning(f"Emergency obstacle detected {direction}: {distance}m")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error checking obstacle safety: {e}")
            return False
    
    def _check_hardware_safety(self) -> bool:
        """
        Check hardware system integrity.
        
        Returns:
            True if hardware is functioning properly
        """
        try:
            # Check motor controller status
            if not self.hardware.motors.is_healthy():
                self.logger.warning("Motor controller failure detected")
                return False
            
            # Check sensor communication
            if not self.hardware.check_sensor_communication():
                self.logger.warning("Sensor communication failure detected")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error checking hardware safety: {e}")
            return False
    
    def set_emergency_callback(self, callback: Callable):
        """
        Set callback function for emergency stop events.
        
        Args:
            callback: Function to call on emergency stop
        """
        self.emergency_callback = callback
    
    def trigger_emergency_stop(self, reason: str = "Manual"):
        """
        Trigger emergency stop.
        
        Args:
            reason: Reason for emergency stop
        """
        self.logger.critical(f"EMERGENCY STOP TRIGGERED: {reason}")
        self.is_emergency_stop = True
        
        if self.emergency_callback:
            try:
                self.emergency_callback()
            except Exception as e:
                self.logger.error(f"Error in emergency stop callback: {e}")
    
    def reset_emergency_stop(self):
        """Reset emergency stop state (manual intervention required)"""
        if self.is_emergency_stop:
            self.logger.info("Emergency stop reset")
            self.is_emergency_stop = False
            self.safety_violations.clear()
    
    def get_safety_status(self) -> Dict[str, Any]:
        """
        Get current safety status.
        
        Returns:
            Dictionary with safety information
        """
        return {
            'is_safe': self.is_safe(),
            'emergency_stop': self.is_emergency_stop,
            'violations': list(self.safety_violations),
            'last_check': self.last_safety_check
        }