"""
Core Package - Contains core business logic and managers
"""
# Import core components
from .auth_manager import AuthManager
from .eye_tracker import EyeTracker
from .system_monitor import SystemMonitor
from .data_manager import DataManager

__all__ = [
    'AuthManager',
    'EyeTracker',
    'SystemMonitor',
    'DataManager'
]
