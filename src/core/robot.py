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
    """Main robot controller class"""
    
    def __init__(self, config):
        """Initialize the robot with configuration"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.running = False
        
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
                
                # Small delay to prevent CPU spinning
                time.sleep(0.01)
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            self._emergency_stop()
            raise
    
    def _execute_state_behavior(self, state: str):
        """Execute behavior for current state"""
        if state == 'idle':
            self._idle_behavior()
        elif state == 'manual_control':
            self._manual_control_behavior()
        elif state == 'autonomous':
            self._autonomous_behavior()
        elif state == 'emergency_stop':
            self._emergency_stop_behavior()
        elif state == 'low_power':
            self._low_power_behavior()
    
    def _idle_behavior(self):
        """Idle state - waiting for commands"""
        self.hardware.motors.stop()
        
    def _manual_control_behavior(self):
        """Manual control state"""
        # Commands come through communication system
        pass
    
    def _autonomous_behavior(self):
        """Autonomous navigation state"""
        self.navigation.update()
    
    def _emergency_stop_behavior(self):
        """Emergency stop - halt all movement"""
        self.hardware.motors.emergency_stop()
        self.hardware.disable_all_actuators()
    
    def _low_power_behavior(self):
        """Low power state - minimal activity"""
        self.hardware.set_low_power_mode(True)
    
    def _handle_command(self, command: Dict[str, Any]):
        """Handle commands from communication system"""
        cmd_type = command.get('type')
        
        if cmd_type == 'move':
            self._handle_move_command(command)
        elif cmd_type == 'state_change':
            self.state_machine.request_state_change(command['state'])
        elif cmd_type == 'emergency_stop':
            self._emergency_stop()
        else:
            self.logger.warning(f"Unknown command type: {cmd_type}")
    
    def _handle_move_command(self, command: Dict[str, Any]):
        """Handle movement commands"""
        if self.state_machine.current_state == 'manual_control':
            speed = command.get('speed', 0)
            direction = command.get('direction', 0)
            self.hardware.motors.set_velocity(speed, direction)
    
    def _emergency_stop(self):
        """Emergency stop procedure"""
        self.logger.critical("EMERGENCY STOP ACTIVATED")
        self.state_machine.set_state('emergency_stop')
        self.hardware.motors.emergency_stop()
    
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
