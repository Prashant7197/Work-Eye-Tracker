"""
UI Package - Contains all user interface components
"""
# Import main UI components
from .main_window import MainWindow
from .auth_widget import AuthWidget
from .dashboard_widget import DashboardWidget
from .status_bar import CustomStatusBar
from .theme import apply_dark_theme

__all__ = [
    'MainWindow',
    'AuthWidget', 
    'DashboardWidget',
    'CustomStatusBar',
    'apply_dark_theme'
]
