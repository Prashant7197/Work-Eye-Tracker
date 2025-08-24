"""
Authentication Manager - Handles user authentication
"""
import logging
import hashlib
import json
import os
from PyQt5.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class AuthManager(QObject):
    """Manages user authentication and session state"""
    
    # Signals
    authentication_changed = pyqtSignal(bool, str)  # is_authenticated, username
    
    def __init__(self):
        super().__init__()
        
        # Current session
        self.current_user = None
        self.is_authenticated = False
        
        # Demo users (in production, this would be handled by a proper backend)
        self.demo_users = {
            "admin": self._hash_password("password"),
            "user": self._hash_password("user123"),
            "demo": self._hash_password("demo")
        }
        
        logger.info("Auth manager initialized")
    
    def authenticate(self, username, password):
        """
        Authenticate user with username and password
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            bool: True if authentication successful
        """
        try:
            # Hash the provided password
            password_hash = self._hash_password(password)
            
            # Check against demo users
            if username in self.demo_users:
                if self.demo_users[username] == password_hash:
                    self.current_user = username
                    self.is_authenticated = True
                    
                    logger.info(f"User {username} authenticated successfully")
                    self.authentication_changed.emit(True, username)
                    
                    return True
            
            logger.warning(f"Authentication failed for user: {username}")
            return False
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def logout(self):
        """Logout current user"""
        if self.is_authenticated:
            logger.info(f"User {self.current_user} logged out")
            
            self.current_user = None
            self.is_authenticated = False
            
            self.authentication_changed.emit(False, "")
    
    def get_current_user(self):
        """Get current authenticated user"""
        return self.current_user if self.is_authenticated else None
    
    def is_user_authenticated(self):
        """Check if user is currently authenticated"""
        return self.is_authenticated
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_session(self):
        """Validate current session (for future implementation)"""
        # In a full implementation, this would validate session tokens
        # with a backend service
        return self.is_authenticated
    
    def get_user_permissions(self):
        """Get current user permissions (for future implementation)"""
        if not self.is_authenticated:
            return []
        
        # Basic permissions for demo
        if self.current_user == "admin":
            return ["read", "write", "delete", "admin"]
        else:
            return ["read", "write"]
