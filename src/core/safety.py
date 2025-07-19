"""
Safety System for Ruohobot

Implements safety monitoring and emergency procedures.
"""

import logging
import time
from typing import Dict, Any, Callable, Optional


class SafetySystem:
    """Robot safety monitoring and emergency response"""
    
    def __init__(self, config: Dict[str, Any], hardware_manager):
        """Initialize safety system"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.hardware = hardware_manager
        
        # Safety configuration
        self.emergency_stop_enabled = config.get('emergency_stop_enabled', True)
        self.max_tilt_angle = config.get('max_tilt_angle', 30)  # degrees
        self.battery_low_threshold = config.get('battery_low_threshold', 11.0)  # volts
        
        # Safety state
        self.safe_state = True
        self.emergency_active = False
        self.safety_violations = []
        self.last_safety_check = time.time()
        
        # Emergency callback
        self.emergency_callback: Optional[Callable] = None
        
        # Safety check counters
        self.check_interval = 0.1  # 100ms
        self.violation_counts = {}
        
        self.logger.info("Safety system initialized")
        self.logger.info(f"Emergency stop enabled: {self.emergency_stop_enabled}")
        self.logger.info(f"Max tilt angle: {self.max_tilt_angle}°")
        self.logger.info(f"Battery low threshold: {self.battery_low_threshold}V")
    
    def set_emergency_callback(self, callback: Callable):
        """Set callback for emergency situations"""
        self.emergency_callback = callback
    
    def is_safe(self) -> bool:
        """Check if robot is safe to operate"""
        return self.safe_state
    
    def check_safety(self) -> bool:
        """Perform safety checks"""
        try:
            current_time = time.time()
            self.last_safety_check = current_time
            
            # Clear previous violations
            self.safety_violations = []
            
            # Check battery level (if available)
            # TODO: Implement actual battery monitoring
            battery_ok = True
            if not battery_ok:
                self.safety_violations.append("Low battery")
            
            # Check sensors
            # TODO: Implement actual sensor monitoring
            sensors_ok = True
            if not sensors_ok:
                self.safety_violations.append("Sensor failure")
            
            # Check motor temperatures and status
            # TODO: Implement actual motor monitoring
            motors_ok = True
            if not motors_ok:
                self.safety_violations.append("Motor fault")
            
            # Update safety state
            self.safe_state = len(self.safety_violations) == 0
            
            if not self.safe_state:
                self.logger.warning(f"Safety violations: {', '.join(self.safety_violations)}")
            
            return self.safe_state
            
        except Exception as e:
            self.logger.error(f"Safety check failed: {e}")
            self.safe_state = False
            return False
    
    def _check_hardware_safety(self) -> list:
        """Check hardware-related safety conditions"""
        violations = []
        
        try:
            # Check motor controller status
            motor_status = self.hardware.motors.get_status()
            
            if motor_status.get('motor_fault', False):
                violations.append("Motor fault detected")
            
            if motor_status.get('no_power', False):
                violations.append("Motor power loss")
            
            if motor_status.get('command_timeout', False):
                violations.append("Motor command timeout")
            
            # Check for hardware errors
            if motor_status.get('protocol_error', False):
                violations.append("Motor communication error")
            
        except Exception as e:
            violations.append(f"Hardware check error: {e}")
        
        return violations
    
    def _check_environmental_safety(self) -> list:
        """Check environmental safety conditions"""
        violations = []
        
        try:
            # Get sensor data
            sensor_data = self.hardware.get_sensor_data()
            
            # Check battery voltage
            battery_voltage = sensor_data.get('battery_voltage', 12.0)
            if battery_voltage < self.battery_low_threshold:
                violations.append(f"Low battery: {battery_voltage:.1f}V")
            
            # Check tilt angle (if IMU available)
            tilt_angle = sensor_data.get('tilt_angle', 0.0)
            if abs(tilt_angle) > self.max_tilt_angle:
                violations.append(f"Excessive tilt: {tilt_angle:.1f}°")
            
            # Check for external emergency signals
            emergency_signal = sensor_data.get('emergency_stop_signal', False)
            if emergency_signal:
                violations.append("External emergency stop activated")
            
        except Exception as e:
            violations.append(f"Environmental check error: {e}")
        
        return violations
    
    def _check_system_safety(self) -> list:
        """Check system-level safety conditions"""
        violations = []
        
        try:
            # Check system health
            system_status = self.hardware.get_system_status()
            
            if system_status.get('low_power_mode', False):
                violations.append("System in low power mode")
            
            # Check for excessive current draw
            for motor_id in [1, 2, 3]:
                try:
                    current = self.hardware.motors.get_motor_current(motor_id)
                    if current > 15000:  # 15A threshold (adjust as needed)
                        violations.append(f"Motor {motor_id} overcurrent: {current}mA")
                except:
                    pass  # Current sensing may not be available
            
        except Exception as e:
            violations.append(f"System check error: {e}")
        
        return violations
    
    def _handle_safety_violations(self, violations: list):
        """Handle detected safety violations"""
        for violation in violations:
            # Count violations to avoid spam
            if violation not in self.violation_counts:
                self.violation_counts[violation] = 0
            self.violation_counts[violation] += 1
            
            # Log first occurrence and every 50th occurrence
            if self.violation_counts[violation] == 1 or self.violation_counts[violation] % 50 == 0:
                self.logger.warning(f"Safety violation: {violation} (count: {self.violation_counts[violation]})")
        
        self.safety_violations = violations
        
        # Determine if emergency stop is needed
        critical_violations = [
            v for v in violations 
            if any(keyword in v.lower() for keyword in ['fault', 'emergency', 'overcurrent', 'excessive tilt'])
        ]
        
        if critical_violations:
            self.safe_state = False
            if not self.emergency_active:
                self._trigger_emergency(f"Critical safety violations: {', '.join(critical_violations)}")
        else:
            # Non-critical violations - just warn
            self.safe_state = len(violations) == 0
    
    def _clear_safety_violations(self):
        """Clear safety violations when conditions are normal"""
        if self.safety_violations:
            self.logger.info("Safety violations cleared")
            self.safety_violations = []
            self.violation_counts = {}
        
        self.safe_state = True
    
    def _trigger_emergency(self, reason: str):
        """Trigger emergency stop"""
        if self.emergency_active:
            return  # Already in emergency state
        
        self.emergency_active = True
        self.safe_state = False
        
        self.logger.critical(f"EMERGENCY STOP TRIGGERED: {reason}")
        
        try:
            # Stop all motors immediately
            self.hardware.motors.emergency_stop()
            
            # Disable other actuators
            self.hardware.disable_all_actuators()
            
            # Call emergency callback
            if self.emergency_callback:
                self.emergency_callback()
                
        except Exception as e:
            self.logger.error(f"Error during emergency stop: {e}")
    
    def reset_emergency(self):
        """Reset emergency state (manual intervention required)"""
        if not self.emergency_active:
            return
        
        self.logger.info("Resetting emergency state...")
        
        # Check if it's safe to reset
        if self.safety_violations:
            remaining_violations = [
                v for v in self.safety_violations 
                if not any(keyword in v.lower() for keyword in ['timeout', 'communication'])
            ]
            
            if remaining_violations:
                self.logger.warning(f"Cannot reset emergency - active violations: {remaining_violations}")
                return False
        
        # Reset emergency state
        self.emergency_active = False
        self.safety_violations = []
        self.violation_counts = {}
        
        # Reset motor controller
        try:
            self.hardware.motors.reset_emergency_stop()
        except Exception as e:
            self.logger.error(f"Error resetting motor emergency stop: {e}")
        
        self.logger.info("Emergency state reset - robot ready for operation")
        return True
    
    def force_reset_emergency(self):
        """Force reset emergency state (use with caution)"""
        self.logger.warning("FORCE RESETTING EMERGENCY STATE")
        self.emergency_active = False
        self.safety_violations = []
        self.violation_counts = {}
        self.safe_state = True
        
        try:
            self.hardware.motors.reset_emergency_stop()
        except Exception as e:
            self.logger.error(f"Error resetting motor emergency stop: {e}")
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get comprehensive safety status"""
        return {
            'is_safe': self.is_safe(),
            'emergency_active': self.emergency_active,
            'safety_violations': self.safety_violations.copy(),
            'emergency_stop_enabled': self.emergency_stop_enabled,
            'last_safety_check': self.last_safety_check,
            'violation_counts': self.violation_counts.copy()
        }
    
    def manual_emergency_stop(self):
        """Manually trigger emergency stop"""
        self._trigger_emergency("Manual emergency stop")
    
    def get_violation_history(self) -> Dict[str, int]:
        """Get history of safety violations"""
        return self.violation_counts.copy()
