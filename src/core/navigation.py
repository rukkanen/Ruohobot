"""
Navigation System

Handles autonomous navigation, path planning, and obstacle avoidance.
"""

import logging
import time
import math
from typing import Dict, Any, Callable, Optional, Tuple, List
from enum import Enum


class NavigationMode(Enum):
    """Navigation operation modes"""
    STOP = "stop"
    FORWARD = "forward"
    BACKWARD = "backward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    OBSTACLE_AVOIDANCE = "obstacle_avoidance"


class NavigationSystem:
    """
    Autonomous navigation and path planning system.
    """
    
    def __init__(self, config: Dict[str, Any], hardware_manager):
        """
        Initialize the navigation system.
        
        Args:
            config: Navigation configuration
            hardware_manager: Hardware manager instance
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.hardware = hardware_manager
        
        # Navigation parameters
        self.max_speed = config.get('max_speed', 0.5)
        self.turn_speed = config.get('turn_speed', 0.3)
        self.obstacle_distance = config.get('obstacle_distance', 0.5)
        
        # Current navigation state
        self.current_mode = NavigationMode.STOP
        self.target_heading = 0.0
        self.current_speed = 0.0
        self.current_direction = 0.0
        
        # State callback for requesting robot state changes
        self.state_callback: Optional[Callable] = None
        
        # Path planning
        self.waypoints: List[Tuple[float, float]] = []
        self.current_waypoint_index = 0
        
        # Obstacle avoidance
        self.avoidance_start_time = 0
        self.avoidance_duration = 2.0  # seconds
        
        self.logger.info("Navigation system initialized")
    
    def update(self):
        """Update navigation system - main navigation loop"""
        try:
            # Get current sensor readings
            distances = self._get_distance_readings()
            
            # Check for obstacles
            if self._obstacle_detected(distances):
                self._handle_obstacle_avoidance(distances)
            else:
                # Normal navigation
                self._execute_navigation()
            
            # Update motor commands
            self._update_motors()
            
        except Exception as e:
            self.logger.error(f"Error in navigation update: {e}")
            self._stop_motors()
    
    def _get_distance_readings(self) -> Dict[str, float]:
        """
        Get distance readings from sensors.
        
        Returns:
            Dictionary with distance readings for each direction
        """
        try:
            return self.hardware.get_distance_readings()
        except Exception as e:
            self.logger.error(f"Error getting distance readings: {e}")
            # Return safe default values
            return {
                'front': 1.0,
                'left': 1.0,
                'right': 1.0,
                'back': 1.0
            }
    
    def _obstacle_detected(self, distances: Dict[str, float]) -> bool:
        """
        Check if obstacles are detected in navigation path.
        
        Args:
            distances: Distance readings
            
        Returns:
            True if obstacle detected
        """
        front_distance = distances.get('front', 1.0)
        return front_distance < self.obstacle_distance
    
    def _handle_obstacle_avoidance(self, distances: Dict[str, float]):
        """
        Handle obstacle avoidance behavior.
        
        Args:
            distances: Current distance readings
        """
        if self.current_mode != NavigationMode.OBSTACLE_AVOIDANCE:
            self.logger.info("Starting obstacle avoidance")
            self.current_mode = NavigationMode.OBSTACLE_AVOIDANCE
            self.avoidance_start_time = time.time()
        
        # Simple obstacle avoidance: stop, turn, continue
        elapsed_time = time.time() - self.avoidance_start_time
        
        if elapsed_time < 1.0:
            # Stop first
            self.current_mode = NavigationMode.STOP
            self.current_speed = 0.0
        elif elapsed_time < 2.0:
            # Choose turn direction based on side clearance
            left_distance = distances.get('left', 0.5)
            right_distance = distances.get('right', 0.5)
            
            if left_distance > right_distance:
                self.current_mode = NavigationMode.TURN_LEFT
            else:
                self.current_mode = NavigationMode.TURN_RIGHT
            
            self.current_speed = self.turn_speed
        else:
            # Resume forward movement
            self.current_mode = NavigationMode.FORWARD
            self.current_speed = self.max_speed * 0.5  # Reduced speed after avoidance
    
    def _execute_navigation(self):
        """Execute normal navigation behavior"""
        if len(self.waypoints) > 0:
            self._navigate_to_waypoint()
        else:
            # Default patrol behavior
            self._patrol_behavior()
    
    def _navigate_to_waypoint(self):
        """Navigate to current waypoint"""
        if self.current_waypoint_index >= len(self.waypoints):
            self.logger.info("All waypoints reached")
            self.current_mode = NavigationMode.STOP
            return
        
        # Simple waypoint navigation (placeholder)
        target_x, target_y = self.waypoints[self.current_waypoint_index]
        
        # For now, just move forward (actual implementation would use GPS/odometry)
        self.current_mode = NavigationMode.FORWARD
        self.current_speed = self.max_speed
        
        # Simulate reaching waypoint after some time
        # In real implementation, this would check actual position
    
    def _patrol_behavior(self):
        """Simple patrol behavior - move forward by default"""
        self.current_mode = NavigationMode.FORWARD
        self.current_speed = self.max_speed * 0.7  # 70% of max speed for patrol
    
    def _update_motors(self):
        """Update motor commands based on current navigation mode"""
        try:
            if self.current_mode == NavigationMode.STOP:
                self.hardware.motors.stop()
            
            elif self.current_mode == NavigationMode.FORWARD:
                self.hardware.motors.set_velocity(self.current_speed, 0.0)
            
            elif self.current_mode == NavigationMode.BACKWARD:
                self.hardware.motors.set_velocity(-self.current_speed, 0.0)
            
            elif self.current_mode == NavigationMode.TURN_LEFT:
                self.hardware.motors.set_velocity(0.0, self.current_speed)
            
            elif self.current_mode == NavigationMode.TURN_RIGHT:
                self.hardware.motors.set_velocity(0.0, -self.current_speed)
                
        except Exception as e:
            self.logger.error(f"Error updating motors: {e}")
    
    def _stop_motors(self):
        """Emergency stop motors"""
        try:
            self.hardware.motors.stop()
            self.current_mode = NavigationMode.STOP
            self.current_speed = 0.0
        except Exception as e:
            self.logger.error(f"Error stopping motors: {e}")
    
    def set_state_callback(self, callback: Callable):
        """
        Set callback for requesting robot state changes.
        
        Args:
            callback: Function to call for state changes
        """
        self.state_callback = callback
    
    def set_waypoints(self, waypoints: List[Tuple[float, float]]):
        """
        Set navigation waypoints.
        
        Args:
            waypoints: List of (x, y) coordinate tuples
        """
        self.waypoints = waypoints
        self.current_waypoint_index = 0
        self.logger.info(f"Navigation waypoints set: {len(waypoints)} points")
    
    def get_navigation_status(self) -> Dict[str, Any]:
        """
        Get current navigation status.
        
        Returns:
            Dictionary with navigation information
        """
        return {
            'mode': self.current_mode.value,
            'speed': self.current_speed,
            'direction': self.current_direction,
            'waypoints': len(self.waypoints),
            'current_waypoint': self.current_waypoint_index
        }