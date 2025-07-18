"""
Hardware Package

Contains hardware-specific modules for motors, sensors, and external devices.
"""

from .motors import MotorController
from .sensors import SensorManager  
from .external_modules import ExternalModuleManager

__all__ = ['MotorController', 'SensorManager', 'ExternalModuleManager']