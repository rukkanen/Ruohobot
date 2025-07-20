"""
Sensor Manager for Ruohobot

Manages local sensors (IMU, battery monitoring, etc.)
"""

import logging
import time
import random
from typing import Dict, Any


class SensorManager:
    """Manages robot's local sensors"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize sensor manager"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Sensor configuration
        self.sensors_enabled = True
        self.low_power_mode = False
        
        # Simulated sensor data (replace with real sensors)
        self.last_update = time.time()
        self.battery_voltage = 12.5  # Simulated battery voltage
        self.tilt_angle = 0.0        # Simulated tilt
        
        self.logger.info("Sensor manager initialized (simulated sensors)")
    
    def get_all_readings(self) -> Dict[str, Any]:
        """Get readings from all sensors"""
        current_time = time.time()
        
        # Update sensor readings
        self._update_sensors()
        
        return {
            'battery_voltage': self.battery_voltage,
            'tilt_angle': self.tilt_angle,
            'timestamp': current_time,
            'sensors_enabled': self.sensors_enabled,
            'low_power_mode': self.low_power_mode
        }
    
    def _update_sensors(self):
        """Update sensor readings (simulated)"""
        self.logger.info("Updating sensor readings...")  # TEST LINE

        # Simulate slowly draining battery
        self.battery_voltage -= 0.0001  # Very slow drain
        if self.battery_voltage < 10.5:
            self.battery_voltage = 12.5  # Reset for simulation
        
        # Simulate small tilt variations
        self.tilt_angle = random.uniform(-2.0, 2.0)
    
    def get_battery_voltage(self) -> float:
        """Get battery voltage"""
        return self.battery_voltage
    
    def get_tilt_angle(self) -> float:
        """Get tilt angle in degrees"""
        return self.tilt_angle
    
    def set_low_power_mode(self, enabled: bool):
        """Enable/disable low power mode"""
        self.low_power_mode = enabled
        if enabled:
            self.logger.info("Sensors entered low power mode")
        else:
            self.logger.info("Sensors exited low power mode")
    
    def get_status(self) -> Dict[str, Any]:
        """Get sensor system status"""
        return {
            'sensors_enabled': self.sensors_enabled,
            'low_power_mode': self.low_power_mode,
            'last_update': self.last_update,
            'available_sensors': ['battery_monitor', 'imu_simulated']
        }
    
    def shutdown(self):
        """Shutdown sensor system"""
        self.logger.info("Sensor manager shutdown")
        self.sensors_enabled = False
