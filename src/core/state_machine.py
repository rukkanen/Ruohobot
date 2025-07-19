"""
State Machine for Ruohobot

Manages robot behavioral states and transitions between them.
"""

import logging
import time
from enum import Enum
from typing import Dict, Any, Callable, Optional


class RobotState(Enum):
    """Available robot states"""
    IDLE = "idle"
    MANUAL_CONTROL = "manual_control"
    AUTONOMOUS = "autonomous"
    EMERGENCY_STOP = "emergency_stop"
    LOW_POWER = "low_power"
    CHARGING = "charging"
    ERROR = "error"


class StateMachine:
    """Robot state machine"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize state machine"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Current state
        default_state = config.get('default_state', 'idle')
        self.current_state = RobotState(default_state)
        self.previous_state = self.current_state
        
        # State timing
        self.state_start_time = time.time()
        self.state_duration = 0.0
        
        # State transition callbacks
        self.state_callbacks: Dict[RobotState, Callable] = {}
        self.transition_callbacks: Dict[tuple, Callable] = {}
        
        # State change requests
        self.requested_state: Optional[RobotState] = None
        self.force_state_change = False
        
        self.logger.info(f"State machine initialized with default state: {self.current_state.value}")
    
    def set_state(self, state: str):
        """Force immediate state change"""
        try:
            new_state = RobotState(state)
            self.logger.info(f"Forcing state change: {self.current_state.value} -> {new_state.value}")
            self._change_state(new_state)
        except ValueError:
            self.logger.error(f"Invalid state: {state}")
    
    def request_state_change(self, state: str):
        """Request state change (will be processed on next update)"""
        try:
            new_state = RobotState(state)
            self.requested_state = new_state
            self.logger.debug(f"State change requested: {state}")
        except ValueError:
            self.logger.error(f"Invalid state requested: {state}")
    
    def update(self) -> str:
        """Update state machine and return current state"""
        current_time = time.time()
        self.state_duration = current_time - self.state_start_time
        
        # Process state change requests
        if self.requested_state is not None:
            if self._can_transition_to(self.requested_state):
                self._change_state(self.requested_state)
            else:
                self.logger.warning(f"Cannot transition from {self.current_state.value} to {self.requested_state.value}")
            self.requested_state = None
        
        # Call state callback if registered
        if self.current_state in self.state_callbacks:
            try:
                self.state_callbacks[self.current_state]()
            except Exception as e:
                self.logger.error(f"Error in state callback for {self.current_state.value}: {e}")
        
        return self.current_state.value
    
    def _change_state(self, new_state: RobotState):
        """Internal state change"""
        if new_state == self.current_state:
            return
        
        old_state = self.current_state
        self.previous_state = old_state
        self.current_state = new_state
        self.state_start_time = time.time()
        self.state_duration = 0.0
        
        self.logger.info(f"State changed: {old_state.value} -> {new_state.value}")
        
        # Call transition callback if registered
        transition = (old_state, new_state)
        if transition in self.transition_callbacks:
            try:
                self.transition_callbacks[transition]()
            except Exception as e:
                self.logger.error(f"Error in transition callback {old_state.value}->{new_state.value}: {e}")
    
    def _can_transition_to(self, new_state: RobotState) -> bool:
        """Check if transition to new state is allowed"""
        
        # Emergency stop can always be entered
        if new_state == RobotState.EMERGENCY_STOP:
            return True
        
        # Cannot leave emergency stop without explicit reset
        if self.current_state == RobotState.EMERGENCY_STOP and new_state != RobotState.IDLE:
            return False
        
        # Error state can only go to idle or emergency stop
        if self.current_state == RobotState.ERROR and new_state not in [RobotState.IDLE, RobotState.EMERGENCY_STOP]:
            return False
        
        # Low power state restrictions
        if self.current_state == RobotState.LOW_POWER and new_state not in [RobotState.CHARGING, RobotState.IDLE, RobotState.EMERGENCY_STOP]:
            return False
        
        # All other transitions are allowed
        return True
    
    def register_state_callback(self, state: RobotState, callback: Callable):
        """Register callback for when robot is in a specific state"""
        self.state_callbacks[state] = callback
        self.logger.debug(f"Registered state callback for {state.value}")
    
    def register_transition_callback(self, from_state: RobotState, to_state: RobotState, callback: Callable):
        """Register callback for specific state transitions"""
        self.transition_callbacks[(from_state, to_state)] = callback
        self.logger.debug(f"Registered transition callback: {from_state.value} -> {to_state.value}")
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get comprehensive state information"""
        return {
            'current_state': self.current_state.value,
            'previous_state': self.previous_state.value,
            'state_duration': self.state_duration,
            'time_in_state': time.time() - self.state_start_time,
            'requested_state': self.requested_state.value if self.requested_state else None
        }
    
    def is_state(self, state: str) -> bool:
        """Check if robot is in specific state"""
        try:
            return self.current_state == RobotState(state)
        except ValueError:
            return False
    
    def time_in_current_state(self) -> float:
        """Get time spent in current state (seconds)"""
        return time.time() - self.state_start_time
