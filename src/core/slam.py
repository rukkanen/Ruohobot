"""
SLAM (Simultaneous Localization and Mapping) System

Implements real-time mapping and localization using LiDAR data.
"""

import logging
import time
import numpy as np
import cv2
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import deque

from .lidar import LidarScan


@dataclass
class Pose:
    """Robot pose (position and orientation)"""
    x: float          # X position in meters
    y: float          # Y position in meters
    theta: float      # Orientation in radians
    timestamp: float  # When this pose was recorded
    confidence: float = 1.0  # Pose confidence (0-1)


class SLAMSystem:
    """SLAM system using LiDAR data"""
    
    def __init__(self, config: Dict[str, Any], lidar_manager):
        """Initialize SLAM system"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.lidar = lidar_manager
        
        # SLAM configuration
        self.map_width = config.get('map_width', 1000)  # cells
        self.map_height = config.get('map_height', 1000)  # cells
        self.map_resolution = config.get('map_resolution', 0.05)  # meters per cell
        self.max_range = config.get('max_range', 10.0)  # max LiDAR range to use
        
        # Initialize occupancy grid
        self.occupancy_grid = np.full((self.map_height, self.map_width), 0.5, dtype=np.float32)
        
        # Map origin (robot starts at center)
        self.origin_x = -(self.map_width * self.map_resolution) / 2
        self.origin_y = -(self.map_height * self.map_resolution) / 2
        
        # Robot pose tracking
        self.current_pose = Pose(0.0, 0.0, 0.0, time.time())
        self.pose_history = deque(maxlen=1000)
        
        # SLAM state
        self.is_mapping = False
        self.total_scans_processed = 0
        self.last_map_update = time.time()
        
        # Register for LiDAR callbacks
        self.lidar.set_scan_callback(self._process_lidar_scan)
        
        self.logger.info("SLAM system initialized")
    
    def start_mapping(self):
        """Start SLAM mapping"""
        if self.is_mapping:
            return

        self.logger.info("Starting SLAM mapping...")
        self.is_mapping = True

        # Start LiDAR if not already running
        if not self.lidar.is_scanning:
            self.lidar.start_scanning()

    def stop_mapping(self):
        """Stop SLAM mapping"""
        if not self.is_mapping:
            return

        self.logger.info("Stopping SLAM mapping...")
        self.is_mapping = False
    
    def _process_lidar_scan(self, scan: LidarScan):
        """Process new LiDAR scan for SLAM"""
        if not self.is_mapping:
            self.logger.info("SLAM: Not mapping, scan ignored.")
            return
        try:
            self.logger.info(f"SLAM: Processing scan with {len(scan.points) if scan and hasattr(scan, 'points') else 'N/A'} points.")
            # Update occupancy grid with scan data
            self._update_occupancy_grid(scan)
            self.total_scans_processed += 1
            self.last_map_update = time.time()
            self.logger.info(f"SLAM: Scan processed. Total scans: {self.total_scans_processed}")
        except Exception as e:
            self.logger.warning(f"Error processing LiDAR scan for SLAM: {e}")
    
    def _update_occupancy_grid(self, scan: LidarScan):
        """Update occupancy grid with LiDAR scan"""
        robot_x = self.current_pose.x
        robot_y = self.current_pose.y
        robot_theta = self.current_pose.theta
        
        for point in scan.points:
            if not point.valid or point.distance > self.max_range:
                continue
            
            # Convert LiDAR point to world coordinates
            point_angle = np.radians(point.angle) + robot_theta
            point_x = robot_x + point.distance * np.cos(point_angle)
            point_y = robot_y + point.distance * np.sin(point_angle)
            
            # Update occupancy grid along ray from robot to point
            self._update_ray(robot_x, robot_y, point_x, point_y)
    
    def _update_ray(self, start_x: float, start_y: float, end_x: float, end_y: float):
        """Update occupancy along a ray using Bresenham's algorithm"""
        # Convert to grid coordinates
        start_gx = int((start_x - self.origin_x) / self.map_resolution)
        start_gy = int((start_y - self.origin_y) / self.map_resolution)
        end_gx = int((end_x - self.origin_x) / self.map_resolution)
        end_gy = int((end_y - self.origin_y) / self.map_resolution)
        
        # Get line points using Bresenham's algorithm
        points = self._bresenham_line(start_gx, start_gy, end_gx, end_gy)
        
        for i, (gx, gy) in enumerate(points):
            if 0 <= gx < self.map_width and 0 <= gy < self.map_height:
                if i == len(points) - 1:
                    # Last point is occupied (obstacle)
                    self.occupancy_grid[gy, gx] = min(1.0, self.occupancy_grid[gy, gx] + 0.1)
                else:
                    # Points along ray are free
                    self.occupancy_grid[gy, gx] = max(0.0, self.occupancy_grid[gy, gx] - 0.05)
    
    def _bresenham_line(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        """Bresenham's line algorithm"""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        while True:
            points.append((x, y))
            if x == x1 and y == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return points
    
    def update_odometry(self, linear_vel: float, angular_vel: float):
        """Update pose with odometry data"""
        current_time = time.time()
        if hasattr(self, '_last_odom_time'):
            dt = current_time - self._last_odom_time
            
            if dt > 0:
                # Simple dead reckoning
                self.current_pose.theta += angular_vel * dt
                self.current_pose.x += linear_vel * np.cos(self.current_pose.theta) * dt
                self.current_pose.y += linear_vel * np.sin(self.current_pose.theta) * dt
                self.current_pose.timestamp = current_time
                
                # Store pose in history
                self.pose_history.append(Pose(
                    self.current_pose.x,
                    self.current_pose.y,
                    self.current_pose.theta,
                    current_time
                ))
        
        self._last_odom_time = current_time
    
    def get_map_image(self, add_robot_pose: bool = True) -> np.ndarray:
        """Generate SLAM map image"""
        map_image = (self.occupancy_grid * 255).astype(np.uint8)
        map_image = cv2.cvtColor(map_image, cv2.COLOR_GRAY2BGR)

        if add_robot_pose:
            robot_x = int((self.current_pose.x - self.origin_x) / self.map_resolution)
            robot_y = int((self.current_pose.y - self.origin_y) / self.map_resolution)
            cv2.circle(map_image, (robot_x, robot_y), 5, (0, 0, 255), -1)

        return map_image