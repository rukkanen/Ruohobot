"""
Hardware Manager

Manages all hardware interfaces including motors, sensors, and communication
with external modules like the Arduino distance scanner and NodeMCU sentinel.
"""

import logging
import serial
import json
from typing import Dict, Any, Optional

from .motors import MotorController
from .sensors import SensorManager
from .external_modules import ExternalModuleManager


class HardwareManager:
    """Manages all hardware components"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize hardware manager"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize hardware components
        self.motors = MotorController(config.get('motors', {}))
        self.sensors = SensorManager(config.get('sensors', {}))
        self.external_modules = ExternalModuleManager(config.get('external_modules', {}))
        
        self.low_power_mode = False
        
        self.logger.info("Hardware manager initialized")
    
    def get_sensor_data(self) -> Dict[str, Any]:
        """Get current sensor readings"""
        data = {}
        
        # Local sensors
        data.update(self.sensors.get_all_readings())
        
        # External module data
        data.update(self.external_modules.get_all_data())
        
        return data
    
    def set_low_power_mode(self, enabled: bool):
        """Enable/disable low power mode"""
        self.low_power_mode = enabled
        self.sensors.set_low_power_mode(enabled)
        self.external_modules.set_low_power_mode(enabled)
        
        if enabled:
            self.logger.info("Entered low power mode")
        else:
            self.logger.info("Exited low power mode")
    
    def disable_all_actuators(self):
        """Disable all actuators for safety"""
        self.motors.emergency_stop()
        # Add any other actuators here
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'motors': self.motors.get_status(),
            'sensors': self.sensors.get_status(),
            'external_modules': self.external_modules.get_status(),
            'low_power_mode': self.low_power_mode
        }
    
    def shutdown(self):
        """Shutdown all hardware components"""
        self.logger.info("Shutting down hardware...")
        
        self.motors.shutdown()
        self.sensors.shutdown()
        self.external_modules.shutdown()
        
        self.logger.info("Hardware shutdown complete")
