"""
External Module Manager

Manages communication with external modules like Arduino distance scanner
and NodeMCU sentinel module.
"""

import logging
import serial
import json
import time
import threading
from typing import Dict, Any, Optional
from queue import Queue, Empty


class ExternalModuleManager:
    """
    Manages external Arduino and NodeMCU modules.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize external module manager.
        
        Args:
            config: External module configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Module connections
        self.distance_scanner = None
        self.sentinel_module = None
        
        # Communication state
        self.low_power_mode = False
        self.data_cache = {}
        
        # Distance scanner config
        distance_config = config.get('distance_scanner', {})
        self.distance_enabled = distance_config.get('enabled', True)
        self.distance_port = distance_config.get('port', '/dev/ttyUSB0')
        
        # Sentinel module config
        sentinel_config = config.get('sentinel', {})
        self.sentinel_enabled = sentinel_config.get('enabled', True)
        self.sentinel_port = sentinel_config.get('port', '/dev/ttyUSB1')
        
        # Initialize modules
        self._initialize_modules()
        
        self.logger.info("External module manager initialized")
    
    def _initialize_modules(self):
        """Initialize external module connections"""
        # Initialize distance scanner
        if self.distance_enabled:
            self._initialize_distance_scanner()
        
        # Initialize sentinel module
        if self.sentinel_enabled:
            self._initialize_sentinel_module()
    
    def _initialize_distance_scanner(self):
        """Initialize Arduino distance scanner connection"""
        try:
            # Try to connect to distance scanner
            self.distance_scanner = serial.Serial(
                port=self.distance_port,
                baudrate=9600,
                timeout=1.0
            )
            self.logger.info(f"Distance scanner connected on {self.distance_port}")
            
            # Initialize data cache
            self.data_cache['distance_readings'] = {
                'front': 1.0,
                'left': 1.0,
                'right': 1.0,
                'back': 1.0
            }
            
        except Exception as e:
            self.logger.warning(f"Could not connect to distance scanner: {e}")
            self.distance_scanner = None
            # Use simulated data
            self._initialize_simulated_distance_data()
    
    def _initialize_sentinel_module(self):
        """Initialize NodeMCU sentinel module connection"""
        try:
            # Try to connect to sentinel module
            self.sentinel_module = serial.Serial(
                port=self.sentinel_port,
                baudrate=115200,
                timeout=1.0
            )
            self.logger.info(f"Sentinel module connected on {self.sentinel_port}")
            
            # Initialize data cache
            self.data_cache['sentinel_data'] = {
                'motion_detected': False,
                'light_level': 500,
                'noise_level': 30
            }
            
        except Exception as e:
            self.logger.warning(f"Could not connect to sentinel module: {e}")
            self.sentinel_module = None
            # Use simulated data
            self._initialize_simulated_sentinel_data()
    
    def _initialize_simulated_distance_data(self):
        """Initialize simulated distance scanner data"""
        self.data_cache['distance_readings'] = {
            'front': 1.0,
            'left': 1.0,
            'right': 1.0,
            'back': 1.0
        }
        self.logger.info("Using simulated distance scanner data")
    
    def _initialize_simulated_sentinel_data(self):
        """Initialize simulated sentinel module data"""
        self.data_cache['sentinel_data'] = {
            'motion_detected': False,
            'light_level': 500,
            'noise_level': 30
        }
        self.logger.info("Using simulated sentinel module data")
    
    def get_all_data(self) -> Dict[str, Any]:
        """
        Get all external module data.
        
        Returns:
            Dictionary with all external module data
        """
        # Update data from modules
        self._update_distance_scanner_data()
        self._update_sentinel_data()
        
        return self.data_cache.copy()
    
    def _update_distance_scanner_data(self):
        """Update data from distance scanner"""
        if self.distance_scanner and self.distance_scanner.is_open:
            try:
                # Request distance readings
                self.distance_scanner.write(b'GET_DISTANCES\n')
                time.sleep(0.01)  # Small delay for response
                
                if self.distance_scanner.in_waiting > 0:
                    response = self.distance_scanner.readline().decode('utf-8').strip()
                    data = json.loads(response)
                    self.data_cache['distance_readings'] = data
                    
            except Exception as e:
                self.logger.error(f"Error reading distance scanner: {e}")
                self._simulate_distance_readings()
        else:
            # Use simulated data
            self._simulate_distance_readings()
    
    def _update_sentinel_data(self):
        """Update data from sentinel module"""
        if self.sentinel_module and self.sentinel_module.is_open:
            try:
                # Request sentinel data
                self.sentinel_module.write(b'GET_STATUS\n')
                time.sleep(0.01)  # Small delay for response
                
                if self.sentinel_module.in_waiting > 0:
                    response = self.sentinel_module.readline().decode('utf-8').strip()
                    data = json.loads(response)
                    self.data_cache['sentinel_data'] = data
                    
            except Exception as e:
                self.logger.error(f"Error reading sentinel module: {e}")
                self._simulate_sentinel_data()
        else:
            # Use simulated data
            self._simulate_sentinel_data()
    
    def _simulate_distance_readings(self):
        """Generate simulated distance readings"""
        import random
        
        # Simulate varying distances
        self.data_cache['distance_readings'] = {
            'front': random.uniform(0.2, 2.0),
            'left': random.uniform(0.3, 1.5),
            'right': random.uniform(0.3, 1.5),
            'back': random.uniform(0.5, 2.0)
        }
    
    def _simulate_sentinel_data(self):
        """Generate simulated sentinel data"""
        import random
        
        # Simulate environmental data
        self.data_cache['sentinel_data'] = {
            'motion_detected': random.choice([True, False]) if random.random() < 0.1 else False,
            'light_level': random.randint(100, 1000),
            'noise_level': random.randint(20, 60)
        }
    
    def get_distance_readings(self) -> Dict[str, float]:
        """
        Get current distance readings.
        
        Returns:
            Dictionary with distance readings for each direction
        """
        self._update_distance_scanner_data()
        return self.data_cache.get('distance_readings', {
            'front': 1.0,
            'left': 1.0,
            'right': 1.0,
            'back': 1.0
        })
    
    def check_sensor_communication(self) -> bool:
        """
        Check if external sensors are communicating properly.
        
        Returns:
            True if all enabled sensors are responding
        """
        communication_ok = True
        
        # Check distance scanner
        if self.distance_enabled:
            if not self.distance_scanner or not self.distance_scanner.is_open:
                communication_ok = False
        
        # Check sentinel module
        if self.sentinel_enabled:
            if not self.sentinel_module or not self.sentinel_module.is_open:
                communication_ok = False
        
        return communication_ok
    
    def set_low_power_mode(self, enabled: bool):
        """
        Enable/disable low power mode for external modules.
        
        Args:
            enabled: True to enable low power mode
        """
        self.low_power_mode = enabled
        
        # Send low power commands to modules
        if self.distance_scanner and self.distance_scanner.is_open:
            try:
                command = b'LOW_POWER_ON\n' if enabled else b'LOW_POWER_OFF\n'
                self.distance_scanner.write(command)
            except Exception as e:
                self.logger.error(f"Error setting distance scanner low power mode: {e}")
        
        if self.sentinel_module and self.sentinel_module.is_open:
            try:
                command = b'LOW_POWER_ON\n' if enabled else b'LOW_POWER_OFF\n'
                self.sentinel_module.write(command)
            except Exception as e:
                self.logger.error(f"Error setting sentinel module low power mode: {e}")
        
        mode_str = "enabled" if enabled else "disabled"
        self.logger.info(f"External module low power mode {mode_str}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get external module status.
        
        Returns:
            Dictionary with module status information
        """
        return {
            'distance_scanner': {
                'enabled': self.distance_enabled,
                'connected': self.distance_scanner is not None and (
                    self.distance_scanner.is_open if self.distance_scanner else False
                ),
                'port': self.distance_port
            },
            'sentinel_module': {
                'enabled': self.sentinel_enabled,
                'connected': self.sentinel_module is not None and (
                    self.sentinel_module.is_open if self.sentinel_module else False
                ),
                'port': self.sentinel_port
            },
            'low_power_mode': self.low_power_mode
        }
    
    def shutdown(self):
        """Shutdown external module connections"""
        self.logger.info("Shutting down external modules...")
        
        # Close distance scanner connection
        if self.distance_scanner:
            try:
                self.distance_scanner.close()
            except Exception as e:
                self.logger.error(f"Error closing distance scanner: {e}")
        
        # Close sentinel module connection
        if self.sentinel_module:
            try:
                self.sentinel_module.close()
            except Exception as e:
                self.logger.error(f"Error closing sentinel module: {e}")
        
        self.logger.info("External modules shutdown complete")