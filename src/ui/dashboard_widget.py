import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QGroupBox, QProgressBar,
                            QGridLayout, QSplitter, QTextEdit, QSpacerItem,
                            QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap

from core.eye_tracker import EyeTracker
from core.system_monitor import SystemMonitor
from core.data_manager import DataManager

logger = logging.getLogger(__name__)

class DashboardWidget(QWidget):
    # Signals
    logout_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.eye_tracker = EyeTracker()
        self.system_monitor = SystemMonitor()
        self.data_manager = DataManager()
        
        # Monitoring state
        self.is_monitoring = False
        
        # Timers
        self.update_timer = QTimer()
        self.save_timer = QTimer()
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        
        logger.info("Dashboard widget initialized")
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create top control bar
        self.create_control_bar(layout)
        
        # Create main content area
        self.create_main_content(layout)
        
        # Create bottom status area
        self.create_status_area(layout)
    
    def create_control_bar(self, layout):
        """Create control bar with start/stop and logout buttons"""
        control_frame = QFrame()
        control_frame.setFixedHeight(60)
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 5px;
            }
        """)
        
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 10, 15, 10)
        
        # Start/Stop monitoring button
        self.monitor_button = QPushButton("Start Monitoring")
        self.monitor_button.setFixedSize(150, 40)
        self.monitor_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5cbf60;
            }
        """)
        control_layout.addWidget(self.monitor_button)
        
        # Spacer
        control_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #ff6b6b; font-size: 20px;")
        control_layout.addWidget(self.status_indicator)
        
        self.status_text = QLabel("Monitoring Stopped")
        self.status_text.setStyleSheet("color: #cccccc; font-weight: bold;")
        control_layout.addWidget(self.status_text)
        
        # Spacer
        control_layout.addStretch()
        
        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.setFixedSize(100, 40)
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #f55346;
            }
        """)
        logout_button.clicked.connect(self.logout_requested.emit)
        control_layout.addWidget(logout_button)
        
        layout.addWidget(control_frame)
    
    def create_main_content(self, layout):
        """Create main content area with monitoring widgets"""
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Eye tracking
        left_panel = self.create_eye_tracking_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - System monitoring
        right_panel = self.create_system_monitoring_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([600, 600])
        
        layout.addWidget(splitter)
    
    def create_eye_tracking_panel(self):
        """Create eye tracking monitoring panel"""
        group_box = QGroupBox("Eye Tracking Monitor")
        layout = QVBoxLayout(group_box)
        layout.setSpacing(15)
        
        # Blink counter display
        blink_frame = QFrame()
        blink_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        blink_layout = QVBoxLayout(blink_frame)
        
        # Current session blinks
        self.blink_count_label = QLabel("0")
        self.blink_count_label.setAlignment(Qt.AlignCenter)
        self.blink_count_label.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #2a82da;
        """)
        blink_layout.addWidget(self.blink_count_label)
        
        blink_text = QLabel("Blinks This Session")
        blink_text.setAlignment(Qt.AlignCenter)
        blink_text.setStyleSheet("color: #cccccc; font-size: 14px;")
        blink_layout.addWidget(blink_text)
        
        layout.addWidget(blink_frame)
        
        # Statistics
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        stats_layout = QGridLayout(stats_frame)
        
        # Blinks per minute
        stats_layout.addWidget(QLabel("Blinks/Min:"), 0, 0)
        self.bpm_label = QLabel("0")
        self.bpm_label.setStyleSheet("color: #2a82da; font-weight: bold;")
        stats_layout.addWidget(self.bpm_label, 0, 1)
        
        # Session duration
        stats_layout.addWidget(QLabel("Session Time:"), 1, 0)
        self.session_time_label = QLabel("00:00:00")
        self.session_time_label.setStyleSheet("color: #2a82da; font-weight: bold;")
        stats_layout.addWidget(self.session_time_label, 1, 1)
        
        # Eye strain indicator
        stats_layout.addWidget(QLabel("Eye Strain:"), 2, 0)
        self.eye_strain_label = QLabel("Normal")
        self.eye_strain_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        stats_layout.addWidget(self.eye_strain_label, 2, 1)
        
        layout.addWidget(stats_frame)
        
        # Camera status
        camera_frame = QFrame()
        camera_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        camera_layout = QHBoxLayout(camera_frame)
        
        camera_layout.addWidget(QLabel("Camera Status:"))
        self.camera_status_label = QLabel("Disconnected")
        self.camera_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        camera_layout.addWidget(self.camera_status_label)
        camera_layout.addStretch()
        
        layout.addWidget(camera_frame)
        
        return group_box
    
    def create_system_monitoring_panel(self):
        """Create system monitoring panel"""
        group_box = QGroupBox("System Performance Monitor")
        layout = QVBoxLayout(group_box)
        layout.setSpacing(15)
        
        # CPU Usage
        cpu_frame = self.create_metric_frame("CPU Usage", "cpu")
        layout.addWidget(cpu_frame)
        
        # Memory Usage
        memory_frame = self.create_metric_frame("Memory Usage", "memory")
        layout.addWidget(memory_frame)
        
        # Power/Energy Impact
        power_frame = self.create_metric_frame("Power Impact", "power")
        layout.addWidget(power_frame)
        
        # Network Status
        network_frame = QFrame()
        network_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        network_layout = QHBoxLayout(network_frame)
        
        network_layout.addWidget(QLabel("Network Status:"))
        self.network_status_label = QLabel("Checking...")
        self.network_status_label.setStyleSheet("color: #ffeb3b; font-weight: bold;")
        network_layout.addWidget(self.network_status_label)
        network_layout.addStretch()
        
        layout.addWidget(network_frame)
        
        return group_box
    
    def create_metric_frame(self, title, metric_type):
        """Create a frame for displaying a system metric"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #cccccc; font-weight: bold; font-size: 12px;")
        layout.addWidget(title_label)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setFixedHeight(20)
        
        # Store reference for updates
        if metric_type == "cpu":
            self.cpu_progress = progress_bar
        elif metric_type == "memory":
            self.memory_progress = progress_bar
        elif metric_type == "power":
            self.power_progress = progress_bar
        
        layout.addWidget(progress_bar)
        
        # Value label
        value_label = QLabel("0%")
        value_label.setStyleSheet("color: #2a82da; font-weight: bold;")
        
        if metric_type == "cpu":
            self.cpu_value_label = value_label
        elif metric_type == "memory":
            self.memory_value_label = value_label
        elif metric_type == "power":
            self.power_value_label = value_label
        
        layout.addWidget(value_label)
        
        return frame
    
    def create_status_area(self, layout):
        """Create bottom status area"""
        status_frame = QFrame()
        status_frame.setFixedHeight(100)
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 5px;
            }
        """)
        
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        # Data sync status
        sync_layout = QHBoxLayout()
        
        sync_layout.addWidget(QLabel("Data Sync:"))
        self.sync_status_label = QLabel("Offline Mode")
        self.sync_status_label.setStyleSheet("color: #ffeb3b; font-weight: bold;")
        sync_layout.addWidget(self.sync_status_label)
        
        sync_layout.addStretch()
        
        # Last sync time
        sync_layout.addWidget(QLabel("Last Sync:"))
        self.last_sync_label = QLabel("Never")
        self.last_sync_label.setStyleSheet("color: #cccccc;")
        sync_layout.addWidget(self.last_sync_label)
        
        status_layout.addLayout(sync_layout)
        
        # GDPR compliance notice
        gdpr_label = QLabel("🔒 All data is processed according to GDPR compliance standards. Data is encrypted and can be deleted upon request.")
        gdpr_label.setStyleSheet("color: #808080; font-size: 10px; font-style: italic;")
        gdpr_label.setWordWrap(True)
        status_layout.addWidget(gdpr_label)
        
        layout.addWidget(status_frame)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Monitor button
        self.monitor_button.clicked.connect(self.toggle_monitoring)
        
        # Update timer - updates UI every second
        self.update_timer.timeout.connect(self.update_display)
        
        # Save timer - saves data every 30 seconds
        self.save_timer.timeout.connect(self.save_data)
    
    def start_monitoring(self):
        """Start monitoring systems"""
        if self.is_monitoring:
            return
        
        logger.info("Starting monitoring")
        
        try:
            # Start eye tracker
            self.eye_tracker.start()
            
            # Start system monitor
            self.system_monitor.start()
            
            # Start timers
            self.update_timer.start(1000)  # Update every second
            self.save_timer.start(30000)   # Save every 30 seconds
            
            # Update UI
            self.is_monitoring = True
            self.monitor_button.setText("Stop Monitoring")
            self.monitor_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    font-size: 13px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #f55346;
                }
            """)
            
            self.status_indicator.setStyleSheet("color: #4caf50; font-size: 20px;")
            self.status_text.setText("Monitoring Active")
            
            # Update camera status
            if self.eye_tracker.is_camera_available():
                self.camera_status_label.setText("Connected")
                self.camera_status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            else:
                self.camera_status_label.setText("Simulated")
                self.camera_status_label.setStyleSheet("color: #ffeb3b; font-weight: bold;")
            
            logger.info("Monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            self.show_error(f"Failed to start monitoring: {str(e)}")
    
    def stop_monitoring(self):
        """Stop monitoring systems"""
        if not self.is_monitoring:
            return
        
        logger.info("Stopping monitoring")
        
        try:
            # Stop timers
            self.update_timer.stop()
            self.save_timer.stop()
            
            # Stop components
            self.eye_tracker.stop()
            self.system_monitor.stop()
            
            # Save final data
            self.save_data()
            
            # Update UI
            self.is_monitoring = False
            self.monitor_button.setText("Start Monitoring")
            self.monitor_button.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    font-size: 13px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #5cbf60;
                }
            """)
            
            self.status_indicator.setStyleSheet("color: #ff6b6b; font-size: 20px;")
            self.status_text.setText("Monitoring Stopped")
            self.camera_status_label.setText("Disconnected")
            self.camera_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            
            logger.info("Monitoring stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
    
    def toggle_monitoring(self):
        """Toggle monitoring state"""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def update_display(self):
        """Update all display elements"""
        try:
            # Update eye tracking data
            if self.eye_tracker.is_running:
                blink_data = self.eye_tracker.get_current_data()
                
                self.blink_count_label.setText(str(blink_data['total_blinks']))
                self.bpm_label.setText(f"{blink_data['blinks_per_minute']:.1f}")
                self.session_time_label.setText(blink_data['session_duration'])
                
                # Update eye strain indicator
                bpm = blink_data['blinks_per_minute']
                if bpm < 10:
                    self.eye_strain_label.setText("High Strain")
                    self.eye_strain_label.setStyleSheet("color: #f44336; font-weight: bold;")
                elif bpm < 15:
                    self.eye_strain_label.setText("Moderate")
                    self.eye_strain_label.setStyleSheet("color: #ffeb3b; font-weight: bold;")
                else:
                    self.eye_strain_label.setText("Normal")
                    self.eye_strain_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            
            # Update system monitoring data
            if self.system_monitor.is_running:
                system_data = self.system_monitor.get_current_data()
                
                # CPU usage
                cpu_percent = system_data['cpu_percent']
                self.cpu_progress.setValue(int(cpu_percent))
                self.cpu_value_label.setText(f"{cpu_percent:.1f}%")
                
                # Memory usage
                memory_percent = system_data['memory_percent']
                self.memory_progress.setValue(int(memory_percent))
                self.memory_value_label.setText(f"{memory_percent:.1f}%")
                
                # Power impact (simulated based on CPU usage)
                power_impact = min(100, cpu_percent * 1.2)
                self.power_progress.setValue(int(power_impact))
                self.power_value_label.setText(f"{power_impact:.1f}%")
                
                # Network status
                if system_data['network_available']:
                    self.network_status_label.setText("Online")
                    self.network_status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
                    self.sync_status_label.setText("Syncing")
                    self.sync_status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
                else:
                    self.network_status_label.setText("Offline")
                    self.network_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
                    self.sync_status_label.setText("Offline Mode")
                    self.sync_status_label.setStyleSheet("color: #ffeb3b; font-weight: bold;")
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    def save_data(self):
        """Save current monitoring data"""
        try:
            if self.is_monitoring:
                # Get data from trackers
                eye_data = self.eye_tracker.get_current_data()
                system_data = self.system_monitor.get_current_data()
                
                # Save to data manager
                self.data_manager.save_session_data(eye_data, system_data)
                
                # Update last sync time
                from datetime import datetime
                self.last_sync_label.setText(datetime.now().strftime("%H:%M:%S"))
                
                logger.debug("Session data saved")
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def show_error(self, message):
        """Show error message to user"""
        # For now, just log the error
        # In a full implementation, you might show a popup or status message
        logger.error(message)
