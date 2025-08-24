import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame, QSpacerItem, 
                            QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.auth_manager import AuthManager

logger = logging.getLogger(__name__)

class AuthWidget(QWidget):
    # Signals
    login_successful = pyqtSignal(str)  # username
    
    def __init__(self):
        super().__init__()
        
        # Auth manager
        self.auth_manager = AuthManager()
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        
        logger.info("Auth widget initialized")
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Add vertical spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Create login form container
        self.create_login_form(layout)
        
        # Add vertical spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def create_login_form(self, layout):
        """Create the login form"""
        # Main container
        container = QFrame()
        container.setFixedSize(400, 350)
        container.setObjectName("loginContainer")
        container.setStyleSheet("""
            QFrame#loginContainer {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 10px;
            }
        """)
        
        form_layout = QVBoxLayout(container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Welcome Back")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        form_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Sign in to continue monitoring your wellness")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            color: #cccccc;
            font-size: 12px;
            margin-bottom: 20px;
        """)
        subtitle_label.setWordWrap(True)
        form_layout.addWidget(subtitle_label)
        
        # Username field
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: #cccccc; font-weight: bold;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(40)
        form_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: #cccccc; font-weight: bold;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setFixedHeight(40)
        form_layout.addWidget(self.password_input)
        
        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setFixedHeight(45)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a92ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
        """)
        form_layout.addWidget(self.login_button)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #ff6b6b; font-size: 11px;")
        self.status_label.hide()
        form_layout.addWidget(self.status_label)
        
        # Demo credentials info
        demo_info = QLabel("Demo Credentials: admin / password")
        demo_info.setAlignment(Qt.AlignCenter)
        demo_info.setStyleSheet("""
            color: #808080;
            font-size: 10px;
            font-style: italic;
            margin-top: 10px;
        """)
        form_layout.addWidget(demo_info)
        
        # Center the container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(container)
        container_layout.addStretch()
        
        layout.addLayout(container_layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.login_button.clicked.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Enable/disable login button based on input
        self.username_input.textChanged.connect(self.update_login_button)
        self.password_input.textChanged.connect(self.update_login_button)
    
    def update_login_button(self):
        """Update login button state based on input"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        self.login_button.setEnabled(len(username) > 0 and len(password) > 0)
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_status("Please enter both username and password", error=True)
            return
        
        # Disable button during login
        self.login_button.setEnabled(False)
        self.login_button.setText("Signing In...")
        
        try:
            # Attempt authentication
            if self.auth_manager.authenticate(username, password):
                self.show_status("Login successful!", error=False)
                
                # Clear inputs
                self.username_input.clear()
                self.password_input.clear()
                
                # Emit success signal
                QTimer.singleShot(500, lambda: self.login_successful.emit(username))
                
                logger.info(f"User {username} authenticated successfully")
            else:
                self.show_status("Invalid username or password", error=True)
                logger.warning(f"Failed authentication attempt for user: {username}")
                
        except Exception as e:
            self.show_status(f"Login error: {str(e)}", error=True)
            logger.error(f"Authentication error: {e}")
        
        finally:
            # Re-enable button
            self.login_button.setText("Sign In")
            self.update_login_button()
    
    def show_status(self, message, error=True):
        """Show status message"""
        self.status_label.setText(message)
        
        if error:
            self.status_label.setStyleSheet("color: #ff6b6b; font-size: 11px;")
        else:
            self.status_label.setStyleSheet("color: #4caf50; font-size: 11px;")
        
        self.status_label.show()
        
        # Hide status after 3 seconds
        QTimer.singleShot(3000, self.status_label.hide)
    
    def reset_form(self):
        """Reset the login form"""
        self.username_input.clear()
        self.password_input.clear()
        self.status_label.hide()
        self.login_button.setEnabled(False)
