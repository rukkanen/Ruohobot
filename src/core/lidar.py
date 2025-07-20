"""
LiDAR Manager for LD-19

Handles LiDAR data acquisition, processing, and SLAM integration.
"""

import logging
import time
import threading
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Callable
from dataclasses import dataclass
from collections import deque


import serial
import struct
import sys
LIDAR_AVAILABLE = False  # No pyldlidar; we use serial directly


@dataclass
class LidarPoint:
    """Single LiDAR measurement point"""
    angle: float      # Angle in degrees (0-360)
    distance: float   # Distance in meters
    intensity: int    # Signal intensity
    valid: bool       # Whether measurement is valid


@dataclass
class LidarScan:
    """Complete LiDAR scan (360 degrees)"""
    timestamp: float
    points: List[LidarPoint]
    scan_frequency: float
    total_points: int
    
    def parse_ld19_data(self, raw_data: bytes):
        """Parse LD-19 LiDAR data"""
        # Implement parsing logic for LD-19 format
        pass

    def _initialize_lidar(self):
        """Initialize LD-19 LiDAR connection"""
        if LIDAR_AVAILABLE:
            self.lidar = LdLidar(self.port, self.baudrate)
            self.lidar.set_scan_frequency(self.scan_frequency)
            self.lidar.start()
            self.logger.info("LD-19 LiDAR initialized")
        else:
            self.logger.warning("LiDAR not available")

class LidarManager:
    """LD-19 LiDAR data acquisition and processing (real and simulated)"""

    def __init__(self, config: Dict[str, Any], simulate: bool = False):
        self.logger = logging.getLogger("core.lidar")
        self.config = config


        # LiDAR configuration: prefer hardware.sensors.lidar if present
        port = None
        baudrate = None
        enabled = None
        scan_frequency = config.get('scan_frequency', 10)
        # Try to get from full robot config structure
        if 'hardware' in config and 'sensors' in config['hardware'] and 'lidar' in config['hardware']['sensors']:
            sensor_cfg = config['hardware']['sensors']['lidar']
            port = sensor_cfg.get('port', None)
            baudrate = sensor_cfg.get('baudrate', None)
            enabled = sensor_cfg.get('enabled', None)
        # Fallback to direct config
        if port is None:
            port = config.get('port', '/dev/ttyUSB0')
        if baudrate is None:
            baudrate = config.get('baudrate', 230400)
        if enabled is None:
            enabled = config.get('enabled', True)
        self.port = port
        self.baudrate = baudrate
        self.scan_frequency = scan_frequency
        self.enabled = enabled

        # Data storage
        self.current_scan: Optional[LidarScan] = None
        self.scan_history = deque(maxlen=100)
        self.is_scanning = False
        self.scan_thread: Optional[threading.Thread] = None

        # Callbacks
        self.scan_callback: Optional[Callable[[LidarScan], None]] = None

        # Statistics
        self.total_scans = 0
        self.scan_errors = 0
        self.last_scan_time = 0

        # Serial port for real LD19
        self.serial = None
        self.simulate = simulate or not self.enabled
        if not self.simulate:
            try:
                self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
                self.logger.info(f"LD-19 serial port opened: {self.port} @ {self.baudrate}")
            except Exception as e:
                self.logger.warning(f"Failed to open LD-19 serial port: {e}. Falling back to simulation.")
                self.simulate = True
        if self.simulate:
            self.logger.info("LidarManager initialized (simulated mode)")
    
    # _initialize_lidar removed (no longer needed)
    
    def start_scanning(self):
        """Start LiDAR scanning in background thread"""
        self.logger.info("LidarManager: start_scanning called")
        if self.is_scanning:
            return False
        self.is_scanning = True
        self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.scan_thread.start()
        return True
    
    def stop_scanning(self):
        """Stop LiDAR scanning"""
        self.logger.info("LidarManager: stop_scanning called")
        self.is_scanning = False
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=2.0)
        if self.serial:
            try:
                self.serial.close()
                self.logger.info("LD-19 serial port closed.")
            except Exception:
                pass
    
    def _scan_loop(self):
        """Main scanning loop running in background thread"""
        self.logger.info("LiDAR scan loop started")
        while self.is_scanning:
            try:
                if self.simulate:
                    num_points = 360
                    scan_data = np.full((num_points,), 4000, dtype=np.float32)  # 4m default
                    for i in range(170, 191):
                        scan_data[i % num_points] = 1000  # 1m
                    scan_data[90] = 2000  # 2m
                    scan_data[270] = 1500  # 1.5m
                    self.logger.debug(f"[SIM] Generated scan_data (first 10): {scan_data[:10]}")
                    processed_scan = self._process_simulated_scan(scan_data)
                else:
                    self.logger.debug("[REAL] Attempting to read LD19 scan from serial...")
                    processed_scan = self._read_ld19_scan()
                if processed_scan:
                    self.logger.debug(f"Scan processed: timestamp={processed_scan.timestamp}, total_points={processed_scan.total_points}")
                    if processed_scan.points:
                        sample_points = processed_scan.points[:5]
                        self.logger.debug(f"First 5 points: {[{'angle': p.angle, 'dist': p.distance, 'valid': p.valid} for p in sample_points]}")
                    self.current_scan = processed_scan
                    self.scan_history.append(processed_scan)
                    self.total_scans += 1
                    self.last_scan_time = time.time()
                    if self.scan_callback:
                        try:
                            self.logger.debug("Calling scan_callback with new scan.")
                            self.scan_callback(processed_scan)
                        except Exception as e:
                            self.logger.warning(f"Scan callback error: {e}")
                else:
                    self.logger.warning("No scan processed in this loop iteration.")
                time.sleep(1.0 / self.scan_frequency)
            except Exception as e:
                self.logger.warning(f"Scan loop error: {e}")
                self.scan_errors += 1
                time.sleep(0.1)
        self.logger.info("LiDAR scan loop stopped")

    def _process_simulated_scan(self, scan_data) -> Optional[LidarScan]:
        """Process simulated scan data into LidarScan"""
        points = []
        for angle in range(len(scan_data)):
            distance = scan_data[angle] / 1000.0
            valid = 0.05 < distance < 12.0
            points.append(LidarPoint(
                angle=angle,
                distance=distance,
                intensity=0,
                valid=valid
            ))
        self.logger.debug(f"[SIM] Processed {len(points)} points in simulated scan.")
        return LidarScan(
            timestamp=time.time(),
            points=points,
            scan_frequency=self.scan_frequency,
            total_points=len(points)
        )

    def _read_ld19_scan(self) -> Optional[LidarScan]:
        """Read and parse a full 360-degree scan from LD19 via serial (protocol-correct)."""
        if not self.serial or not self.serial.is_open:
            self.logger.warning("Serial port not open for LD19.")
            return None

        def crc8(data: bytes) -> int:
            # Official CRC8 table from SDK
            table = [
                0x00, 0x4d, 0x9a, 0xd7, 0x79, 0x34, 0xe3, 0xae, 0xf2, 0xbf, 0x68, 0x25,
                0x8b, 0xc6, 0x11, 0x5c, 0xa9, 0xe4, 0x33, 0x7e, 0xd0, 0x9d, 0x4a, 0x07,
                0x5b, 0x16, 0xc1, 0x8c, 0x22, 0x6f, 0xb8, 0xf5, 0x1f, 0x52, 0x85, 0xc8,
                0x66, 0x2b, 0xfc, 0xb1, 0xed, 0xa0, 0x77, 0x3a, 0x94, 0xd9, 0x0e, 0x43,
                0xb6, 0xfb, 0x2c, 0x61, 0xcf, 0x82, 0x55, 0x18, 0x44, 0x09, 0xde, 0x93,
                0x3d, 0x70, 0xa7, 0xea, 0x3e, 0x73, 0xa4, 0xe9, 0x47, 0x0a, 0xdd, 0x90,
                0xcc, 0x81, 0x56, 0x1b, 0xb5, 0xf8, 0x2f, 0x62, 0x97, 0xda, 0x0d, 0x40,
                0xee, 0xa3, 0x74, 0x39, 0x65, 0x28, 0xff, 0xb2, 0x1c, 0x51, 0x86, 0xcb,
                0x21, 0x6c, 0xbb, 0xf6, 0x58, 0x15, 0xc2, 0x8f, 0xd3, 0x9e, 0x49, 0x04,
                0xaa, 0xe7, 0x30, 0x7d, 0x88, 0xc5, 0x12, 0x5f, 0xf1, 0xbc, 0x6b, 0x26,
                0x7a, 0x37, 0xe0, 0xad, 0x03, 0x4e, 0x99, 0xd4, 0x7c, 0x31, 0xe6, 0xab,
                0x05, 0x48, 0x9f, 0xd2, 0x8e, 0xc3, 0x14, 0x59, 0xf7, 0xba, 0x6d, 0x20,
                0xd5, 0x98, 0x4f, 0x02, 0xac, 0xe1, 0x36, 0x7b, 0x27, 0x6a, 0xbd, 0xf0,
                0x5e, 0x13, 0xc4, 0x89, 0x63, 0x2e, 0xf9, 0xb4, 0x1a, 0x57, 0x80, 0xcd,
                0x91, 0xdc, 0x0b, 0x46, 0xe8, 0xa5, 0x72, 0x3f, 0xca, 0x87, 0x50, 0x1d,
                0xb3, 0xfe, 0x29, 0x64, 0x38, 0x75, 0xa2, 0xef, 0x41, 0x0c, 0xdb, 0x96,
                0x42, 0x0f, 0xd8, 0x95, 0x3b, 0x76, 0xa1, 0xec, 0xb0, 0xfd, 0x2a, 0x67,
                0xc9, 0x84, 0x53, 0x1e, 0xeb, 0xa6, 0x71, 0x3c, 0x92, 0xdf, 0x08, 0x45,
                0x19, 0x54, 0x83, 0xce, 0x60, 0x2d, 0xfa, 0xb7, 0x5d, 0x10, 0xc7, 0x8a,
                0x24, 0x69, 0xbe, 0xf3, 0xaf, 0xe2, 0x35, 0x78, 0xd6, 0x9b, 0x4c, 0x01,
                0xf4, 0xb9, 0x6e, 0x23, 0x8d, 0xc0, 0x17, 0x5a, 0x06, 0x4b, 0x9c, 0xd1,
                0x7f, 0x32, 0xe5, 0xa8
            ]
            crc = 0
            for b in data:
                crc = table[(crc ^ b) & 0xFF]
            return crc

        scan_points: List[LidarPoint] = []
        last_end_angle = None
        scan_complete = False
        start_time = time.time()
        timeout = 1.0  # seconds
        raw_packet_log_count = 0
        packets_collected = 0
        while not scan_complete and (time.time() - start_time) < timeout:
            try:
                # Find packet header
                header = self.serial.read(2)
                if len(header) < 2:
                    continue
                if header[0] != 0x54 or header[1] != 0x2C:
                    continue
                packet = header + self.serial.read(45)
                if len(packet) != 47:
                    continue
                if raw_packet_log_count < 3:
                    self.logger.debug(f"[RAW PACKET {raw_packet_log_count+1}] {packet.hex(' ')}")
                # CRC8 check
                if crc8(packet[:46]) != packet[46]:
                    self.logger.debug("[CRC] CRC8 mismatch, skipping packet.")
                    continue
                # Parse packet fields
                speed = int.from_bytes(packet[2:4], 'little')
                start_angle = int.from_bytes(packet[4:6], 'little') / 100.0  # degrees
                points = []
                for i in range(12):
                    offset = 6 + i * 3
                    distance = int.from_bytes(packet[offset:offset+2], 'little') / 1000.0  # meters
                    intensity = packet[offset+2]
                    points.append((distance, intensity))
                end_angle = int.from_bytes(packet[42:44], 'little') / 100.0  # degrees
                timestamp = int.from_bytes(packet[44:46], 'little')
                # Interpolate angles for 12 points
                angle_diff = (end_angle - start_angle)
                if angle_diff < 0:
                    angle_diff += 360.0
                angle_step = angle_diff / (12 - 1)
                angles = [(start_angle + i * angle_step) % 360.0 for i in range(12)]
                # If this is the first packet, just start collecting
                if last_end_angle is not None:
                    # Detect wraparound (end of scan)
                    if (start_angle < last_end_angle) and (last_end_angle - start_angle > 180):
                        scan_complete = True
                last_end_angle = end_angle
                # Add points to scan
                for (distance, intensity), angle in zip(points, angles):
                    valid = 0.05 < distance < 12.0
                    scan_points.append(LidarPoint(
                        angle=angle,
                        distance=distance,
                        intensity=intensity,
                        valid=valid
                    ))
                packets_collected += 1
                if raw_packet_log_count < 3:
                    self.logger.debug(f"[PARSE] Packet {packets_collected}: start_angle={start_angle:.2f}, end_angle={end_angle:.2f}, first 3 points: {scan_points[-12:-9]}")
                    raw_packet_log_count += 1
            except Exception as e:
                self.logger.warning(f"LD19 serial read error: {e}")
                break
        # Optionally, sort points by angle and deduplicate
        scan_points = sorted(scan_points, key=lambda p: p.angle)
        # Remove duplicate angles (keep first occurrence)
        seen_angles = set()
        unique_points = []
        for p in scan_points:
            a = int(round(p.angle))
            if a not in seen_angles:
                unique_points.append(p)
                seen_angles.add(a)
        valid_points = sum(1 for p in unique_points if p.valid)
        self.logger.info(f"[SCAN SUMMARY] packets={packets_collected}, valid_points={valid_points}, total_points={len(unique_points)}")
        self.logger.debug(f"[REAL] Finished scan: {len(unique_points)} points collected. First 5: {[{'angle': p.angle, 'dist': p.distance, 'valid': p.valid} for p in unique_points[:5]]}")
        return LidarScan(
            timestamp=time.time(),
            points=unique_points,
            scan_frequency=self.scan_frequency,
            total_points=len(unique_points)
        )
    
    # _process_scan_data removed (replaced by _process_simulated_scan and _read_ld19_scan)
    
    def get_current_scan(self) -> Optional[LidarScan]:
        """Get the most recent LiDAR scan"""
        return self.current_scan
    
    def get_scan_as_cartesian(self, scan: Optional[LidarScan] = None) -> np.ndarray:
        """Convert LiDAR scan to Cartesian coordinates (x, y) in meters"""
        if scan is None:
            scan = self.current_scan
        if not scan:
            self.logger.debug("get_scan_as_cartesian: No scan available.")
            return np.array([]).reshape(0, 2)
        points = []
        for point in scan.points:
            if point.valid:
                x = point.distance * np.cos(np.radians(point.angle))
                y = point.distance * np.sin(np.radians(point.angle))
                points.append([x, y])
        self.logger.debug(f"get_scan_as_cartesian: {len(points)} valid points. Sample: {points[:5]}")
        return np.array(points)
    
    def get_obstacles_in_direction(self, direction: float, cone_angle: float = 30.0) -> List[float]:
        """Get obstacle distances in a specific direction cone"""
        if not self.current_scan:
            return []
        
        obstacles = []
        half_cone = cone_angle / 2.0
        
        for point in self.current_scan.points:
            if not point.valid:
                continue
            
            # Normalize angle difference
            angle_diff = abs(point.angle - direction)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            
            if angle_diff <= half_cone:
                obstacles.append(point.distance)
        
        return sorted(obstacles)  # Closest first
    
    def set_scan_callback(self, callback: Callable[[LidarScan], None]):
        """Set callback function for new scans"""
        self.scan_callback = callback
    
    def get_status(self) -> Dict[str, Any]:
        """Get LiDAR status information"""
        return {
            'connected': (self.serial is not None and self.serial.is_open) if not self.simulate else True,
            'scanning': self.is_scanning,
            'total_scans': self.total_scans,
            'scan_errors': self.scan_errors,
            'last_scan_age': time.time() - self.last_scan_time if self.last_scan_time > 0 else -1,
            'scan_frequency': self.scan_frequency,
            'current_points': len(self.current_scan.points) if self.current_scan else 0,
            'simulated': self.simulate
        }
    
    def shutdown(self):
        """Shutdown LiDAR system"""
        self.logger.info("Shutting down LiDAR system...")
        self.stop_scanning()
        self.serial = None