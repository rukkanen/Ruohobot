"""
State Machine

Manages robot operational states and state transitions.
"""

import logging
from enum import Enum
from typing import Dict, Any, Callable, Optional


class RobotState(Enum):
    """Robot operational states"""
    IDLE = "idle"
    MANUAL_CONTROL = "manual_control"
    AUTONOMOUS = "autonomous"
    EMERGENCY_STOP = "emergency_stop"
    LOW_POWER = "low_power"


class StateMachine:
    """
    Robot state machine for managing operational states and transitions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the state machine.
        
        Args:
            config: Behavior configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize state
        default_state = config.get('default_state', 'idle')
        self.current_state = RobotState(default_state)
        self.previous_state = None
        
        # State transition callbacks
        self._state_callbacks: Dict[str, Callable] = {}
        
        # Valid state transitions
        self._valid_transitions = {
            RobotState.IDLE: [RobotState.MANUAL_CONTROL, RobotState.AUTONOMOUS, RobotState.EMERGENCY_STOP],
            RobotState.MANUAL_CONTROL: [RobotState.IDLE, RobotState.EMERGENCY_STOP, RobotState.LOW_POWER],
            RobotState.AUTONOMOUS: [RobotState.IDLE, RobotState.EMERGENCY_STOP, RobotState.LOW_POWER],
            RobotState.EMERGENCY_STOP: [RobotState.IDLE],
            RobotState.LOW_POWER: [RobotState.IDLE, RobotState.EMERGENCY_STOP]
        }
        
        self.logger.info(f"State machine initialized in {self.current_state.value} state")
    
    def update(self) -> str:
        """
        Update the state machine.
        
        Returns:
            Current state as string
        """
        # Check for automatic state transitions based on conditions
        self._check_automatic_transitions()
        
        return self.current_state.value
    
    def request_state_change(self, new_state: str) -> bool:
        """
        Request a state change.
        
        Args:
            new_state: Target state name
            
        Returns:
            True if transition was successful
        """
        try:
            target_state = RobotState(new_state)
            return self._transition_to(target_state)
        except ValueError:
            self.logger.error(f"Invalid state requested: {new_state}")
            return False
    
    def set_state(self, new_state: str):
        """
        Force set state (used for emergency situations).
        
        Args:
            new_state: Target state name
        """
        try:
            target_state = RobotState(new_state)
            self.previous_state = self.current_state
            self.current_state = target_state
            self.logger.warning(f"State forced to {new_state}")
            self._notify_state_change()
        except ValueError:
            self.logger.error(f"Invalid state: {new_state}")
    
    def _transition_to(self, new_state: RobotState) -> bool:
        """
        Attempt to transition to a new state.
        
        Args:
            new_state: Target state
            
        Returns:
            True if transition was successful
        """
        if new_state == self.current_state:
            return True
            
        if new_state in self._valid_transitions.get(self.current_state, []):
            self.logger.info(f"Transitioning from {self.current_state.value} to {new_state.value}")
            self.previous_state = self.current_state
            self.current_state = new_state
            self._notify_state_change()
            return True
        else:
            self.logger.warning(f"Invalid transition from {self.current_state.value} to {new_state.value}")
            return False
    
    def _check_automatic_transitions(self):
        """Check for automatic state transitions based on conditions"""
        # Example: Low battery triggers low power mode
        # This would be expanded with actual sensor readings
        pass
    
    def _notify_state_change(self):
        """Notify registered callbacks of state change"""
        callback = self._state_callbacks.get(self.current_state.value)
        if callback:
            try:
                callback(self.current_state.value, self.previous_state.value if self.previous_state else None)
            except Exception as e:
                self.logger.error(f"Error in state change callback: {e}")
    
    def register_state_callback(self, state: str, callback: Callable):
        """
        Register a callback for state changes.
        
        Args:
            state: State name to monitor
            callback: Function to call on state entry
        """
        self._state_callbacks[state] = callback