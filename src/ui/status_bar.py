"""
Custom Status Bar for the main window
"""
import logging
from PyQt5.QtWidgets import QStatusBar, QLabel, QProgressBar, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

logger = logging.getLogger(__name__)

class CustomStatusBar(QStatusBar):
    """Custom status bar with connection and sync indicators"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize widgets
        self.init_widgets()
        self.setup_layout()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(5000)  # Update every 5 seconds
        
        logger.info("Status bar initialized")
    
    def init_widgets(self):
        """Initialize status bar widgets"""
        # Connection status
        self.connection_label = QLabel("● Offline")
        self.connection_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        # Sync status
        self.sync_label = QLabel("Sync: Never")
        self.sync_label.setStyleSheet("color: #cccccc;")
        
        # Data count
        self.data_count_label = QLabel("Records: 0")
        self.data_count_label.setStyleSheet("color: #cccccc;")
        
        # GDPR indicator
        self.gdpr_label = QLabel("🔒 GDPR Compliant")
        self.gdpr_label.setStyleSheet("color: #4caf50; font-weight: bold;")
    
    def setup_layout(self):
        """Setup status bar layout"""
        # Add permanent widgets (right side)
        self.addPermanentWidget(self.gdpr_label)
        self.addPermanentWidget(self.data_count_label)
        self.addPermanentWidget(self.sync_label)
        self.addPermanentWidget(self.connection_label)
        
        # Set initial message
        self.showMessage("Ready")
    
    def update_connection_status(self, is_connected):
        """Update connection status indicator"""
        if is_connected:
            self.connection_label.setText("● Online")
            self.connection_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        else:
            self.connection_label.setText("● Offline")
            self.connection_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
    
    def update_sync_status(self, last_sync_time):
        """Update sync status"""
        if last_sync_time:
            self.sync_label.setText(f"Sync: {last_sync_time}")
            self.sync_label.setStyleSheet("color: #4caf50;")
        else:
            self.sync_label.setText("Sync: Never")
            self.sync_label.setStyleSheet("color: #cccccc;")
    
    def update_data_count(self, count):
        """Update data record count"""
        self.data_count_label.setText(f"Records: {count}")
    
    def update_status(self):
        """Periodic status update"""
        # This would typically check actual system status
        # For now, just ensure GDPR indicator is visible
        pass
    
    def show_message_temp(self, message, timeout=2000):
        """Show temporary message"""
        self.showMessage(message, timeout)
