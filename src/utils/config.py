"""
Configuration Management for the Wellness at Work Application
"""
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Config:
    """Application configuration manager"""
    
    def __init__(self):
        self.config_file = Path("config/app_config.json")
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Default configuration
        self.default_config = {
            "app": {
                "name": "Wellness at Work - Eye Tracker",
                "version": "1.0.0",
                "debug_mode": False,
                "auto_start_monitoring": False
            },
            "eye_tracking": {
                "simulation_mode": False,
                "blink_threshold_frames": 5,
                "camera_index": 0,
                "camera_width": 640,
                "camera_height": 480,
                "camera_fps": 30
            },
            "system_monitoring": {
                "update_interval_seconds": 2,
                "metrics_history_minutes": 60,
                "enable_battery_monitoring": True,
                "enable_network_monitoring": True
            },
            "data": {
                "auto_sync_enabled": True,
                "sync_interval_minutes": 5,
                "retention_days": 30,
                "database_path": "data/wellness_tracker.db"
            },
            "ui": {
                "theme": "dark",
                "window_width": 1200,
                "window_height": 800,
                "remember_window_position": True,
                "show_notifications": True
            },
            "privacy": {
                "gdpr_compliance": True,
                "data_encryption": True,
                "anonymize_data": False,
                "consent_required": True
            },
            "api": {
                "base_url": "https://api.wellness-tracker.com",
                "timeout_seconds": 30,
                "retry_attempts": 3,
                "use_ssl": True
            }
        }
        
        # Load configuration
        self.config = self.load_config()
        
        logger.info("Configuration manager initialized")
    
    def load_config(self):
        """Load configuration from file or create with defaults"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults (in case new keys were added)
                config = self._merge_configs(self.default_config, loaded_config)
                
                logger.info("Configuration loaded from file")
                return config
            else:
                # Create config file with defaults
                self.save_config(self.default_config)
                logger.info("Created new configuration file with defaults")
                return self.default_config.copy()
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            return self.default_config.copy()
    
    def save_config(self, config=None):
        """Save configuration to file"""
        try:
            config_to_save = config or self.config
            
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=4)
            
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get(self, key_path, default=None):
        """
        Get configuration value using dot notation
        
        Args:
            key_path (str): Key path like 'app.name' or 'eye_tracking.camera_index'
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                value = value[key]
            
            return value
            
        except (KeyError, TypeError):
            logger.warning(f"Configuration key '{key_path}' not found, using default: {default}")
            return default
    
    def set(self, key_path, value, save=True):
        """
        Set configuration value using dot notation
        
        Args:
            key_path (str): Key path like 'app.debug_mode'
            value: Value to set
            save (bool): Whether to save to file immediately
        """
        try:
            keys = key_path.split('.')
            config_ref = self.config
            
            # Navigate to parent key
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]
            
            # Set the value
            config_ref[keys[-1]] = value
            
            if save:
                self.save_config()
            
            logger.debug(f"Configuration updated: {key_path} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to set configuration '{key_path}': {e}")
    
    def _merge_configs(self, default, loaded):
        """Recursively merge loaded config with defaults"""
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        self.save_config()
        logger.info("Configuration reset to defaults")
    
    def get_app_info(self):
        """Get application information"""
        return {
            'name': self.get('app.name'),
            'version': self.get('app.version'),
            'debug_mode': self.get('app.debug_mode', False)
        }
    
    def is_debug_mode(self):
        """Check if debug mode is enabled"""
        return self.get('app.debug_mode', False)
    
    def get_database_path(self):
        """Get database file path"""
        return Path(self.get('data.database_path', 'data/wellness_tracker.db'))
    
    def is_gdpr_compliant(self):
        """Check if GDPR compliance is enabled"""
        return self.get('privacy.gdpr_compliance', True)
    
    def get_sync_interval(self):
        """Get sync interval in minutes"""
        return self.get('data.sync_interval_minutes', 5)
    
    def is_auto_sync_enabled(self):
        """Check if auto sync is enabled"""
        return self.get('data.auto_sync_enabled', True)

# Global configuration instance
config = Config()

def get_config():
    """Get global configuration instance"""
    return config
