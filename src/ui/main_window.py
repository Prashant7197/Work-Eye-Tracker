import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QStackedWidget, QLabel, QFrame, QSplitter)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

from .auth_widget import AuthWidget
from .dashboard_widget import DashboardWidget
from .status_bar import CustomStatusBar
from core.auth_manager import AuthManager
from core.data_manager import DataManager

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    # Signals
    user_authenticated = pyqtSignal(str)  # username
    user_logged_out = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.auth_manager = AuthManager()
        self.data_manager = DataManager()
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        
        # Start with authentication screen
        self.show_auth_screen()
        
        logger.info("Main window initialized")
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Wellness at Work - Eye Tracker")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.create_header(main_layout)
        
        # Stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create screens
        self.auth_widget = AuthWidget()
        self.dashboard_widget = DashboardWidget()
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.auth_widget)
        self.stacked_widget.addWidget(self.dashboard_widget)
        
        # Status bar
        self.status_bar = CustomStatusBar()
        self.setStatusBar(self.status_bar)
    
    def create_header(self, layout):
        """Create application header"""
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet("""
            QFrame#headerFrame {
                background-color: #2b2b2b;
                border-bottom: 2px solid #404040;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # App title
        title_label = QLabel("Wellness at Work")
        title_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        
        subtitle_label = QLabel("Eye Tracker & Performance Monitor")
        subtitle_label.setStyleSheet("""
            color: #cccccc;
            font-size: 12px;
            margin-left: 10px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        
        # User info (hidden initially)
        self.user_info_label = QLabel("")
        self.user_info_label.setStyleSheet("""
            color: #cccccc;
            font-size: 12px;
        """)
        self.user_info_label.hide()
        header_layout.addWidget(self.user_info_label)
        
        layout.addWidget(header_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Auth widget connections
        self.auth_widget.login_successful.connect(self.on_login_successful)
        
        # Dashboard widget connections
        self.dashboard_widget.logout_requested.connect(self.on_logout_requested)
        
        # Auth manager connections
        self.auth_manager.authentication_changed.connect(self.on_auth_changed)
    
    def show_auth_screen(self):
        """Show authentication screen"""
        self.stacked_widget.setCurrentWidget(self.auth_widget)
        self.user_info_label.hide()
        self.status_bar.update_connection_status(False)
        logger.info("Showing authentication screen")
    
    def show_dashboard(self):
        """Show main dashboard"""
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)
        self.dashboard_widget.start_monitoring()
        logger.info("Showing dashboard")
    
    def on_login_successful(self, username):
        """Handle successful login"""
        logger.info(f"User {username} logged in successfully")
        
        # Update UI
        self.user_info_label.setText(f"Logged in as: {username}")
        self.user_info_label.show()
        
        # Show dashboard
        self.show_dashboard()
        
        # Update status
        self.status_bar.update_connection_status(True)
        
        # Emit signal
        self.user_authenticated.emit(username)
    
    def on_logout_requested(self):
        """Handle logout request"""
        logger.info("Logout requested")
        
        # Stop monitoring
        self.dashboard_widget.stop_monitoring()
        
        # Clear authentication
        self.auth_manager.logout()
        
        # Show auth screen
        self.show_auth_screen()
        
        # Emit signal
        self.user_logged_out.emit()
    
    def on_auth_changed(self, is_authenticated, username):
        """Handle authentication state change"""
        if is_authenticated:
            self.on_login_successful(username)
        else:
            self.show_auth_screen()
    
    def closeEvent(self, event):
        """Handle application close"""
        logger.info("Application closing")
        
        # Stop monitoring
        if hasattr(self, 'dashboard_widget'):
            self.dashboard_widget.stop_monitoring()
        
        # Save any pending data
        if hasattr(self, 'data_manager'):
            self.data_manager.save_pending_data()
        
        event.accept()
