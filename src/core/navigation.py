"""
Navigation System for Ruohobot

Handles autonomous navigation, path planning, and obstacle avoidance.
"""

import logging
import time
import math
from typing import Dict, Any, Tuple, List, Optional, Callable


class NavigationSystem:
    """Autonomous navigation system"""
    
    def __init__(self, config: Dict[str, Any], hardware_manager):
        """Initialize navigation system"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.hardware = hardware_manager
        
        # Navigation parameters
        self.max_speed = config.get('max_speed', 0.5)
        self.turn_speed = config.get('turn_speed', 0.3)
        self.obstacle_distance = config.get('obstacle_distance', 0.5)
        
        # Current navigation state
        self.is_navigating = False
        self.current_target = None
        self.navigation_mode = "idle"  # idle, waypoint, explore, return_home
        
        # Position tracking (simple odometry)
        self.position = {'x': 0.0, 'y': 0.0, 'heading': 0.0}
        self.last_update_time = time.time()
        
        # Waypoint navigation
        self.waypoints: List[Tuple[float, float]] = []
        self.current_waypoint_index = 0
        
        # Obstacle avoidance
        self.obstacle_detected = False
        self.avoidance_start_time = 0
        
        # Callbacks
        self.state_callback: Optional[Callable] = None
        
        self.logger.info("Navigation system initialized")
    
    def set_state_callback(self, callback: Callable):
        """Set callback for state change requests"""
        self.state_callback = callback
    
    def update(self):
        """Main navigation update loop"""
        if not self.is_navigating:
            return
        
        try:
            # Update position estimation
            self._update_position()
            
            # Check for obstacles
            self._check_obstacles()
            
            # Execute current navigation behavior
            if self.navigation_mode == "waypoint":
                self._navigate_to_waypoint()
            elif self.navigation_mode == "explore":
                self._explore_behavior()
            elif self.navigation_mode == "return_home":
                self._return_home_behavior()
            elif self.navigation_mode == "avoid_obstacle":
                self._obstacle_avoidance_behavior()
                
        except Exception as e:
            self.logger.error(f"Navigation update error: {e}")
            self.stop_navigation()
    
    def start_navigation(self, mode: str = "explore"):
        """Start autonomous navigation"""
        self.is_navigating = True
        self.navigation_mode = mode
        self.last_update_time = time.time()
        self.logger.info(f"Navigation started in {mode} mode")
    
    def stop_navigation(self):
        """Stop autonomous navigation"""
        self.is_navigating = False
        self.navigation_mode = "idle"
        self.hardware.motors.stop()
        self.logger.info("Navigation stopped")
    
    def set_waypoints(self, waypoints: List[Tuple[float, float]]):
        """Set waypoints for navigation"""
        self.waypoints = waypoints
        self.current_waypoint_index = 0
        self.logger.info(f"Set {len(waypoints)} waypoints")
    
    def go_to_point(self, x: float, y: float):
        """Navigate to a specific point"""
        self.current_target = (x, y)
        self.navigation_mode = "waypoint"
        self.start_navigation()
        self.logger.info(f"Navigating to point ({x}, {y})")
    
    def _update_position(self):
        """Update position estimation using simple odometry"""
        current_time = time.time()
        dt = current_time - self.last_update_time
        
        if dt > 0:
            # Get current motor speeds (this is approximate)
            status = self.hardware.motors.get_status()
            speeds = status.get('current_speeds', {1: 0, 2: 0})
            
            # Simple differential drive kinematics
            left_speed = speeds.get(1, 0)
            right_speed = speeds.get(2, 0)
            
            # Convert motor speeds to linear and angular velocities
            # These constants need calibration for your specific robot
            speed_scale = 0.001  # Convert motor units to m/s
            wheel_base = 0.3     # Distance between wheels (meters)
            
            linear_velocity = (left_speed + right_speed) * 0.5 * speed_scale
            angular_velocity = (right_speed - left_speed) * speed_scale / wheel_base
            
            # Update position
            self.position['heading'] += angular_velocity * dt
            self.position['x'] += linear_velocity * math.cos(self.position['heading']) * dt
            self.position['y'] += linear_velocity * math.sin(self.position['heading']) * dt
            
        self.last_update_time = current_time
    
    def _check_obstacles(self):
        """Check for obstacles using sensor data"""
        try:
            sensor_data = self.hardware.get_sensor_data()
            
            # Check distance sensors (you'll need to adapt this to your sensors)
            front_distance = sensor_data.get('front_distance', float('inf'))
            
            if front_distance < self.obstacle_distance:
                if not self.obstacle_detected:
                    self.obstacle_detected = True
                    self.avoidance_start_time = time.time()
                    self.navigation_mode = "avoid_obstacle"
                    self.logger.info(f"Obstacle detected at {front_distance:.2f}m")
            else:
                if self.obstacle_detected:
                    self.obstacle_detected = False
                    self.navigation_mode = "explore"  # Resume previous behavior
                    self.logger.info("Obstacle cleared")
                    
        except Exception as e:
            self.logger.debug(f"Sensor check error: {e}")
    
    def _navigate_to_waypoint(self):
        """Navigate to current waypoint"""
        if not self.waypoints or self.current_waypoint_index >= len(self.waypoints):
            self.stop_navigation()
            return
        
        target_x, target_y = self.waypoints[self.current_waypoint_index]
        
        # Calculate distance and bearing to target
        dx = target_x - self.position['x']
        dy = target_y - self.position['y']
        distance = math.sqrt(dx*dx + dy*dy)
        target_bearing = math.atan2(dy, dx)
        
        # Check if we've reached the waypoint
        if distance < 0.2:  # 20cm tolerance
            self.logger.info(f"Reached waypoint {self.current_waypoint_index}: ({target_x}, {target_y})")
            self.current_waypoint_index += 1
            return
        
        # Calculate steering to target
        bearing_error = target_bearing - self.position['heading']
        
        # Normalize bearing error to [-pi, pi]
        while bearing_error > math.pi:
            bearing_error -= 2 * math.pi
        while bearing_error < -math.pi:
            bearing_error += 2 * math.pi
        
        # Simple proportional controller
        angular_command = bearing_error * 0.5  # Proportional gain
        linear_command = self.max_speed * (1.0 - abs(bearing_error) / math.pi)
        
        # Limit commands
        angular_command = max(-self.turn_speed, min(self.turn_speed, angular_command))
        linear_command = max(0, min(self.max_speed, linear_command))
        
        # Send commands to motors
        self.hardware.motors.set_velocity(linear_command, angular_command)
    
    def _explore_behavior(self):
        """Exploration mode using SLAM"""
        if self.slam_system.is_mapping:
            self.slam_system.start_mapping()
        obstacles = self._check_obstacles()
        if obstacles:
            self._avoid_obstacles()
        else:
            self._navigate_to_waypoint()
    
    def _return_home_behavior(self):
        """Return to starting position"""
        # Navigate back to (0, 0)
        target_x, target_y = 0.0, 0.0
        
        dx = target_x - self.position['x']
        dy = target_y - self.position['y']
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 0.5:  # Close to home
            self.stop_navigation()
            if self.state_callback:
                self.state_callback("idle")
            return
        
        # Point towards home
        target_bearing = math.atan2(dy, dx)
        bearing_error = target_bearing - self.position['heading']
        
        # Normalize bearing error
        while bearing_error > math.pi:
            bearing_error -= 2 * math.pi
        while bearing_error < -math.pi:
            bearing_error += 2 * math.pi
        
        # Navigate towards home
        angular_command = bearing_error * 0.5
        linear_command = self.max_speed * 0.8
        
        self.hardware.motors.set_velocity(linear_command, angular_command)
    
    def _obstacle_avoidance_behavior(self):
        """Simple obstacle avoidance"""
        avoidance_time = time.time() - self.avoidance_start_time
        
        if avoidance_time < 1.0:
            # Back up
            self.hardware.motors.set_velocity(-self.max_speed * 0.5, 0.0)
        elif avoidance_time < 2.5:
            # Turn right
            self.hardware.motors.set_velocity(0.0, self.turn_speed)
        else:
            # Resume forward motion
            self.navigation_mode = "explore"
            self.obstacle_detected = False
    
    def get_position(self) -> Dict[str, float]:
        """Get current estimated position"""
        return self.position.copy()
    
    def reset_position(self):
        """Reset position to origin"""
        self.position = {'x': 0.0, 'y': 0.0, 'heading': 0.0}
        self.logger.info("Position reset to origin")
    
    def get_status(self) -> Dict[str, Any]:
        """Get navigation system status"""
        return {
            'is_navigating': self.is_navigating,
            'navigation_mode': self.navigation_mode,
            'position': self.position.copy(),
            'current_target': self.current_target,
            'waypoints_remaining': len(self.waypoints) - self.current_waypoint_index if self.waypoints else 0,
            'obstacle_detected': self.obstacle_detected
        }
