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
        
        # Encoder and IMU support
        self.left_encoder = None
        self.right_encoder = None
        self.imu = None
        
        # Try to load real sensors if config present
        enc_cfg = config.get('encoders', {})
        if enc_cfg and 'left_pin' in enc_cfg and 'right_pin' in enc_cfg:
            try:
                from .encoder import Encoder
                self.left_encoder = Encoder(
                    pin=enc_cfg['left_pin'],
                    pulses_per_rev=enc_cfg.get('pulses_per_rev', 20),
                    wheel_diameter=enc_cfg.get('wheel_diameter', 0.065)
                )
                self.right_encoder = Encoder(
                    pin=enc_cfg['right_pin'],
                    pulses_per_rev=enc_cfg.get('pulses_per_rev', 20),
                    wheel_diameter=enc_cfg.get('wheel_diameter', 0.065)
                )
                self.logger.info(f"Encoders initialized on pins {enc_cfg['left_pin']} and {enc_cfg['right_pin']}")
            except Exception as e:
                self.logger.warning(f"Encoder init failed: {e}")
        
        imu_cfg = config.get('imu', {})
        if imu_cfg:
            try:
                from .imu import IMU
                self.imu = IMU(i2c_address=imu_cfg.get('i2c_address', 0x68))
                self.logger.info(f"IMU initialized at I2C address {hex(imu_cfg.get('i2c_address', 0x68))}")
            except Exception as e:
                self.logger.warning(f"IMU init failed: {e}")
        
        # Only log on error or startup
    
    def get_all_readings(self) -> Dict[str, Any]:
        """Get readings from all sensors"""
        current_time = time.time()
        
        # Update sensor readings
        self._update_sensors()
        
        data = {
            'battery_voltage': self.battery_voltage,
            'tilt_angle': self.tilt_angle,
            'timestamp': current_time,
            'sensors_enabled': self.sensors_enabled,
            'low_power_mode': self.low_power_mode
        }
        # Add encoder readings if available
        if self.left_encoder:
            data['left_encoder_count'] = self.left_encoder.get_count()
            data['left_encoder_distance'] = self.left_encoder.get_distance()
        if self.right_encoder:
            data['right_encoder_count'] = self.right_encoder.get_count()
            data['right_encoder_distance'] = self.right_encoder.get_distance()
        # Add IMU readings if available
        if self.imu:
            try:
                data['imu'] = self.imu.get_all()
                data['imu_temp'] = self.imu.get_temperature()
            except Exception as e:
                self.logger.warning(f"IMU read failed: {e}")
        
        return data
    
    def _update_sensors(self):
        """Update sensor readings (simulated)"""
        # Remove repetitive sensor update log

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
            pass  # Only log on error
        else:
            pass  # Only log on error
    
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
        # Only log on error
        self.sensors_enabled = False
        if self.left_encoder:
            self.left_encoder.cleanup()
        if self.right_encoder:
            self.right_encoder.cleanup()
