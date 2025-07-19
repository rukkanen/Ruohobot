"""
External Module Manager for Ruohobot

Manages communication with external modules like Arduino distance scanner and NodeMCU sentinel.
"""

import logging
import time
import json
from typing import Dict, Any, Optional
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class ExternalModuleManager:
    """Manages external Arduino and NodeMCU modules"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize external module manager"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Module configurations
        self.distance_scanner_config = config.get('distance_scanner', {})
        self.sentinel_config = config.get('sentinel', {})
        
        # Serial connections
        self.distance_scanner_port = None
        self.sentinel_port = None
        
        # Module data
        self.distance_data = {}
        self.sentinel_data = {}
        self.last_update = time.time()
        
        # Status
        self.low_power_mode = False
        
        if not SERIAL_AVAILABLE:
            self.logger.warning("Serial library not available - external modules disabled")
            return
        
        # Initialize modules
        self._init_distance_scanner()
        self._init_sentinel()
        
        self.logger.info("External module manager initialized")
    
    def _init_distance_scanner(self):
        """Initialize Arduino distance scanner"""
        if not self.distance_scanner_config.get('enabled', False):
            self.logger.info("Distance scanner disabled in config")
            return
        
        port_path = self.distance_scanner_config.get('port', '/dev/ttyUSB0')
        baudrate = self.distance_scanner_config.get('baudrate', 9600)
        
        try:
            if SERIAL_AVAILABLE:
                self.distance_scanner_port = serial.Serial(
                    port_path,
                    baudrate,
                    timeout=1.0
                )
                self.logger.info(f"Distance scanner connected on {port_path}")
            else:
                self.logger.warning("Distance scanner: serial not available")
                
        except Exception as e:
            self.logger.error(f"Failed to connect distance scanner: {e}")
            self.distance_scanner_port = None
    
    def _init_sentinel(self):
        """Initialize NodeMCU sentinel module"""
        if not self.sentinel_config.get('enabled', False):
            self.logger.info("Sentinel module disabled in config")
            return
        
        port_path = self.sentinel_config.get('port', '/dev/ttyUSB1')
        baudrate = self.sentinel_config.get('baudrate', 115200)
        
        try:
            if SERIAL_AVAILABLE:
                self.sentinel_port = serial.Serial(
                    port_path,
                    baudrate,
                    timeout=1.0
                )
                self.logger.info(f"Sentinel module connected on {port_path}")
            else:
                self.logger.warning("Sentinel module: serial not available")
                
        except Exception as e:
            self.logger.error(f"Failed to connect sentinel module: {e}")
            self.sentinel_port = None
    
    def get_all_data(self) -> Dict[str, Any]:
        """Get data from all external modules"""
        self._update_distance_scanner()
        self._update_sentinel()
        
        return {
            'distance_scanner': self.distance_data.copy(),
            'sentinel': self.sentinel_data.copy(),
            'last_update': self.last_update
        }
    
    def _update_distance_scanner(self):
        """Update data from distance scanner"""
        if not self.distance_scanner_port:
            # Simulate distance data for testing
            self.distance_data = {
                'front_distance': 2.5,  # meters
                'left_distance': 1.8,
                'right_distance': 3.2,
                'rear_distance': 1.5,
                'status': 'simulated',
                'timestamp': time.time()
            }
            return
        
        try:
            # Send request for distance data
            self.distance_scanner_port.write(b'GET_DISTANCES\n')
            
            # Read response
            response = self.distance_scanner_port.readline().decode().strip()
            
            if response:
                # Parse distance data (format: "DIST:1.23,2.34,3.45,4.56")
                if response.startswith('DIST:'):
                    distances = response[5:].split(',')
                    if len(distances) >= 4:
                        self.distance_data = {
                            'front_distance': float(distances[0]),
                            'left_distance': float(distances[1]),
                            'right_distance': float(distances[2]),
                            'rear_distance': float(distances[3]),
                            'status': 'connected',
                            'timestamp': time.time()
                        }
                
        except Exception as e:
            self.logger.debug(f"Distance scanner communication error: {e}")
            self.distance_data = {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _update_sentinel(self):
        """Update data from sentinel module"""
        if not self.sentinel_port:
            # Simulate sentinel data for testing
            self.sentinel_data = {
                'temperature': 23.5,     # Celsius
                'humidity': 65.2,        # %
                'light_level': 450,      # lux
                'motion_detected': False,
                'battery_voltage': 3.7,  # V
                'status': 'simulated',
                'timestamp': time.time()
            }
            return
        
        try:
            # Send request for sensor data
            self.sentinel_port.write(b'GET_SENSORS\n')
            
            # Read response
            response = self.sentinel_port.readline().decode().strip()
            
            if response:
                # Parse JSON data
                try:
                    data = json.loads(response)
                    self.sentinel_data = {
                        'temperature': data.get('temp', 0.0),
                        'humidity': data.get('humidity', 0.0),
                        'light_level': data.get('light', 0),
                        'motion_detected': data.get('motion', False),
                        'battery_voltage': data.get('battery', 0.0),
                        'status': 'connected',
                        'timestamp': time.time()
                    }
                except json.JSONDecodeError:
                    self.logger.debug(f"Invalid JSON from sentinel: {response}")
                
        except Exception as e:
            self.logger.debug(f"Sentinel communication error: {e}")
            self.sentinel_data = {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def get_distance_data(self) -> Dict[str, Any]:
        """Get latest distance scanner data"""
        self._update_distance_scanner()
        return self.distance_data.copy()
    
    def get_sentinel_data(self) -> Dict[str, Any]:
        """Get latest sentinel data"""
        self._update_sentinel()
        return self.sentinel_data.copy()
    
    def get_front_distance(self) -> float:
        """Get front distance reading"""
        self._update_distance_scanner()
        return self.distance_data.get('front_distance', float('inf'))
    
    def get_environmental_data(self) -> Dict[str, Any]:
        """Get environmental sensor data from sentinel"""
        self._update_sentinel()
        return {
            'temperature': self.sentinel_data.get('temperature', 0.0),
            'humidity': self.sentinel_data.get('humidity', 0.0),
            'light_level': self.sentinel_data.get('light_level', 0)
        }
    
    def set_low_power_mode(self, enabled: bool):
        """Enable/disable low power mode"""
        self.low_power_mode = enabled
        
        # Send low power commands to modules
        if enabled:
            self._send_command_to_all('LOW_POWER_ON')
            self.logger.info("External modules entered low power mode")
        else:
            self._send_command_to_all('LOW_POWER_OFF')
            self.logger.info("External modules exited low power mode")
    
    def _send_command_to_all(self, command: str):
        """Send command to all connected modules"""
        command_bytes = f"{command}\n".encode()
        
        if self.distance_scanner_port:
            try:
                self.distance_scanner_port.write(command_bytes)
            except Exception as e:
                self.logger.debug(f"Error sending command to distance scanner: {e}")
        
        if self.sentinel_port:
            try:
                self.sentinel_port.write(command_bytes)
            except Exception as e:
                self.logger.debug(f"Error sending command to sentinel: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get external module system status"""
        return {
            'distance_scanner_connected': self.distance_scanner_port is not None,
            'sentinel_connected': self.sentinel_port is not None,
            'low_power_mode': self.low_power_mode,
            'last_update': self.last_update,
            'distance_scanner_status': self.distance_data.get('status', 'unknown'),
            'sentinel_status': self.sentinel_data.get('status', 'unknown')
        }
    
    def shutdown(self):
        """Shutdown external module connections"""
        self.logger.info("Shutting down external modules...")
        
        if self.distance_scanner_port:
            try:
                self.distance_scanner_port.close()
            except Exception as e:
                self.logger.error(f"Error closing distance scanner: {e}")
        
        if self.sentinel_port:
            try:
                self.sentinel_port.close()
            except Exception as e:
                self.logger.error(f"Error closing sentinel: {e}")
        
        self.logger.info("External modules shutdown complete")
