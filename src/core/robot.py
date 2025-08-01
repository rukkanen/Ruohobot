"""
Core Robot Class

Main robot controller that orchestrates all subsystems.
"""

import time
import logging
from typing import Dict, Any

from .state_machine import StateMachine
from .hardware_manager import HardwareManager
from .navigation import NavigationSystem
from .communication import CommunicationManager
from .safety import SafetySystem


class Robot:
    def self_test(self):
        """Run a self-test of motors, encoders, and IMU. Log results and continue regardless of failures."""
        debug = getattr(self.config, 'debug_mode', False) or getattr(self.config, 'debug', {}).get('web_debug', False)
        results = {}
        try:
            # 1. Reset encoders
            if hasattr(self.hardware.sensors, 'left_encoder') and self.hardware.sensors.left_encoder:
                self.hardware.sensors.left_encoder.reset()
            if hasattr(self.hardware.sensors, 'right_encoder') and self.hardware.sensors.right_encoder:
                self.hardware.sensors.right_encoder.reset()
            # 2. Get initial IMU reading
            initial_accel = None
            if hasattr(self.hardware.sensors, 'imu') and self.hardware.sensors.imu:
                try:
                    initial_accel = self.hardware.sensors.imu.get_accel()
                except Exception as e:
                    self.logger.warning(f"IMU read failed: {e}")
            # 3. Move wheels forward a bit
            # Only log if debug
            self.hardware.motors.set_velocity(0.6, 0.0)  # Move forward at higher speed
            time.sleep(1.0)
            self.hardware.motors.stop()
            time.sleep(0.2)
            # 4. Check encoder counts
            left_count = self.hardware.sensors.left_encoder.get_count() if self.hardware.sensors.left_encoder else None
            right_count = self.hardware.sensors.right_encoder.get_count() if self.hardware.sensors.right_encoder else None
            results['left_encoder'] = left_count is not None and left_count > 0
            results['right_encoder'] = right_count is not None and right_count > 0
            # Only log if debug
            # 5. Check IMU for movement
            moved = False
            if initial_accel and self.hardware.sensors.imu:
                try:
                    new_accel = self.hardware.sensors.imu.get_accel()
                    # Check if any axis changed by >0.2 m/s^2 (simple threshold)
                    moved = any(abs(new_accel[axis] - initial_accel[axis]) > 0.2 for axis in new_accel)
                except Exception as e:
                    self.logger.warning(f"IMU read failed after move: {e}")
            results['imu_movement'] = moved
            # Only log if debug
        except Exception as e:
            self.logger.error(f"Self-test error: {e}")
        # Log summary
        for k, v in results.items():
            if v:
                pass  # Only log failures
            else:
                self.logger.warning(f"Self-test failed: {k}")
    """Main robot controller class"""
    
    def __init__(self, config):
        """Initialize the robot with configuration"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.running = False
        
        # Track state changes to avoid redundant operations
        self._last_state = None
        self._motors_stopped = False
        self._emergency_stop_executed = False
        
        # Initialize subsystems
        self.logger.info("Initializing robot subsystems...")
        
        self.hardware = HardwareManager(config.hardware)
        self.safety = SafetySystem(config.safety, self.hardware)
        self.navigation = NavigationSystem(config.navigation, self.hardware)
        self.communication = CommunicationManager(config.communication)
        self.state_machine = StateMachine(config.behavior)
        
        # Connect subsystems
        self._connect_subsystems()
        
        self.logger.info("Robot initialization complete")
    
    def _connect_subsystems(self):
        """Connect subsystems for inter-communication"""
        self.logger.info("Connecting subsystems...")
        # Safety system has emergency stop authority
        self.safety.set_emergency_callback(self._emergency_stop)
        
        # Navigation can request state changes
        self.navigation.set_state_callback(self.state_machine.request_state_change)
        
        # Communication can send commands
        self.communication.set_command_callback(self._handle_command)
    
    def run(self):
        """Main robot control loop"""
        self.running = True
        self.logger.info("Starting robot main loop")
        
        try:
            while self.running:
                # Safety check first
                if not self.safety.is_safe():
                    self.state_machine.set_state('emergency_stop')
                
                # Update state machine
                current_state = self.state_machine.update()
                
                # Execute current state behavior
                self._execute_state_behavior(current_state)
                
                # Update communication
                self.communication.update()
                
                # Update telemetry data
                self._update_telemetry()
                
                # Small delay to prevent CPU spinning
                time.sleep(0.01)
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            self._emergency_stop()
            raise
    
    def _execute_state_behavior(self, state: str):
        """Execute behavior for current state"""
        # Check if state changed
        state_changed = state != self._last_state
        if state_changed:
            self.logger.info(f"State changed from {self._last_state} to {state}")
            self._last_state = state
            # Reset flags on state change
            if state != 'idle':
                self._motors_stopped = False
            if state != 'emergency_stop':
                self._emergency_stop_executed = False
        
        if state == 'idle':
            self._idle_behavior(state_changed)
        elif state == 'manual_control':
            self._manual_control_behavior()
        elif state == 'autonomous':
            self._autonomous_behavior()
        elif state == 'emergency_stop':
            self._emergency_stop_behavior(state_changed)
        elif state == 'low_power':
            self._low_power_behavior()
        elif state == 'exploration':
            self._exploration_behavior()
    
    def _idle_behavior(self, state_changed: bool = False):
        """Idle state - waiting for commands"""
        # Only stop motors once when entering idle state
        if state_changed or not self._motors_stopped:
            self.hardware.motors.stop()
            self._motors_stopped = True
        
    def _manual_control_behavior(self):
        """Manual control state"""
        # Commands come through communication system
        pass
    
    def _autonomous_behavior(self):
        """Autonomous navigation state"""
        self.navigation.update()
    
    def _emergency_stop_behavior(self, state_changed: bool = False):
        """Emergency stop - halt all movement"""
        # Only execute emergency stop once when entering emergency state
        if state_changed or not self._emergency_stop_executed:
            self.hardware.motors.emergency_stop()
            self.hardware.disable_all_actuators()
            self._emergency_stop_executed = True
    
    def _low_power_behavior(self):
        """Low power state - minimal activity"""
        self.hardware.set_low_power_mode(True)
    
    def _exploration_behavior(self):
        """Exploration state - autonomous navigation and mapping"""
        self.logger.info("Exploration behavior active")
        self.navigation.update()
        # Use the SLAM and LiDAR from CommunicationManager so the web map updates
        if hasattr(self.communication, 'slam') and hasattr(self.communication, 'lidar'):
            if self.communication.slam and self.communication.lidar:
                scan = self.communication.lidar.get_current_scan()
                # The SLAM system expects a scan to be processed, not update_map
                if scan is not None and hasattr(self.communication.slam, '_process_lidar_scan'):
                    self.communication.slam._process_lidar_scan(scan)
                else:
                    self.logger.warning("No scan available or SLAM missing _process_lidar_scan method!")
            else:
                self.logger.warning("CommunicationManager SLAM or LiDAR not initialized!")
        else:
            self.logger.warning("CommunicationManager missing slam or lidar attributes!")
    
    def _run_exploration_algorithm(self):
        """Run exploration algorithm"""
        self.logger.info("Running exploration algorithm")
        if hasattr(self.communication, 'slam') and self.communication.slam:
            unexplored_areas = self.communication.slam.get_unexplored_areas()
            # Only call navigate_to if it exists
            if hasattr(self.navigation, 'navigate_to'):
                self.navigation.navigate_to(unexplored_areas)
            else:
                self.logger.warning("NavigationSystem missing navigate_to method!")
        else:
            self.logger.warning("CommunicationManager SLAM not available for exploration algorithm!")
    
    def _handle_command(self, command: Dict[str, Any]):
        """Handle commands from communication system"""
        # {'type': 'move', 'data': {'speed': 400, 'direction': 0}}
        self.logger.info(f"robot._handle_command: Received command: {command}")
        cmd_type = command.get('type')
        self.logger.info(f"Command type: {cmd_type}")
        self._last_command = cmd_type  # Track last command for telemetry                

        if cmd_type == 'move':
            self.logger.info(f"Handling move command: {command}")
            self._handle_move_command(command)
        elif cmd_type == 'state_change':
            # Handle both formats: {"type": "state_change", "state": "value"} and {"type": "state_change", "data": "value"}
            state = command.get('state', command.get('data'))
            if state:
                self.state_machine.request_state_change(state)
            else:
                self.logger.warning("State change command missing state parameter")
        elif cmd_type == 'emergency_stop':
            self._emergency_stop()
        else:
            self.logger.warning(f"Unknown command type: {cmd_type}")
    
    def _handle_move_command(self, command: Dict[str, Any]):
        """Handle movement commands"""
        self.logger.info(f"_handle_move_command: Current state is {self.state_machine.current_state}")
        
        if self.state_machine.current_state.value == 'manual_control':
            # Extract data from command - handle both formats for compatibility
            data = command.get('data', command)  # Use 'data' field if present, otherwise use command directly
            speed = data.get('speed', 0)
            direction = data.get('direction', 0)
            self.logger.info(f"_handle_move_command: Extracted speed={speed}, direction={direction}")
            self.logger.info(f"_handle_move_command: Calling motors.set_velocity({speed}, {direction})")
            self.hardware.motors.set_velocity(speed, direction)
            self.logger.info(f"_handle_move_command: Motor command sent successfully")
        else:
            self.logger.warning(f"_handle_move_command: Cannot move in state '{self.state_machine.current_state}', need 'manual_control'")
    
    def _emergency_stop(self):
        """Emergency stop procedure"""
        self.logger.critical("EMERGENCY STOP ACTIVATED")
        self.state_machine.set_state('emergency_stop')
        self.hardware.motors.emergency_stop()
    
    def _update_telemetry(self):
        """Update telemetry data with current robot status"""
        try:
            # Get current state as string
            current_state = str(self.state_machine.current_state)
            
            # Basic robot status
            safety_status = {
                'is_safe': self.safety.is_safe(),
                'emergency_stop_active': current_state == 'emergency_stop'
            }
            
            # Update communication telemetry
            telemetry_data = {
                'robot_state': current_state,
                'safety_status': safety_status,
                'last_command': getattr(self, '_last_command', 'none'),
                'motors_stopped': self._motors_stopped,
                'system_status': 'running' if self.running else 'stopped'
            }
            
            self.communication.update_telemetry(telemetry_data)
            
        except Exception as e:
            self.logger.warning(f"Failed to update telemetry: {e}")
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down robot...")
        self.running = False
        
        # Stop all movement
        self.hardware.motors.stop()
        
        # Shutdown subsystems
        self.hardware.shutdown()
        self.communication.shutdown()
        
        self.logger.info("Robot shutdown complete")
