"""
Configuration Manager

Handles loading and managing configuration from YAML files.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages robot configuration"""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration manager"""
        self.logger = logging.getLogger(__name__)
        
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "robot_config.yaml"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                return config
            else:
                self.logger.warning(f"Config file {self.config_path} not found, using defaults")
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'hardware': {
                'motors': {
                    'pololu_m3h550': {
                        'i2c_bus': 1,  # Standard I2C bus on Raspberry Pi
                        'i2c_address': 16,
                        'max_speed': 800,
                        # Motor mapping for Ruohobot
                        # Motor 1: Not used (bad solder connections)
                        # Motor 2: Right drive motor
                        # Motor 3: Left drive motor
                        'motor_mapping': {
                            'left_motor': 3,
                            'right_motor': 2,
                            'unused_motor': 1
                        },
                        'motor_1_acceleration': 140,
                        'motor_1_deceleration': 300,
                        'motor_1_reversed': False,
                        'motor_1_enabled': False,  # Disabled due to bad solder connections
                        'motor_2_acceleration': 140,
                        'motor_2_deceleration': 300,
                        'motor_2_reversed': False,
                        'motor_2_enabled': True,   # Right motor - enabled
                        'motor_3_acceleration': 140,
                        'motor_3_deceleration': 300,
                        'motor_3_reversed': False,
                        'motor_3_enabled': True    # Left motor - enabled
                    }
                },
                'sensors': {
                    'distance_scanner': {
                        'port': '/dev/ttyUSB0',
                        'baudrate': 9600
                    },
                    'sentinel': {
                        'port': '/dev/ttyUSB1',
                        'baudrate': 115200
                    }
                },
                'external_modules': {
                    'distance_scanner': {
                        'enabled': True,
                        'port': '/dev/ttyUSB0'
                    },
                    'sentinel': {
                        'enabled': True,
                        'port': '/dev/ttyUSB1'
                    }
                }
            },
            'safety': {
                'emergency_stop_enabled': True,
                'max_tilt_angle': 30,
                'battery_low_threshold': 11.0
            },
            'navigation': {
                'max_speed': 0.5,
                'turn_speed': 0.3,
                'obstacle_distance': 0.5
            },
            'communication': {
                'wifi_enabled': True,
                'telemetry_port': 8080
            },
            'behavior': {
                'default_state': 'idle',
                'patrol_mode': True
            }
        }
    
    @property
    def hardware(self):
        """Get hardware configuration"""
        return ConfigDict(self._config.get('hardware', {}))
    
    @property
    def safety(self):
        """Get safety configuration"""
        return ConfigDict(self._config.get('safety', {}))
    
    @property
    def navigation(self):
        """Get navigation configuration"""
        return ConfigDict(self._config.get('navigation', {}))
    
    @property
    def communication(self):
        """Get communication configuration"""
        return ConfigDict(self._config.get('communication', {}))
    
    @property
    def behavior(self):
        """Get behavior configuration"""
        return ConfigDict(self._config.get('behavior', {}))


class ConfigDict(dict):
    """Dictionary that allows dot notation access"""
    
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def get(self, key, default=None):
        """Get value with default"""
        return super().get(key, default)
