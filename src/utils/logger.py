"""
Logging Configuration for the Wellness at Work Application
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

def setup_logger(name=None, level=logging.INFO):
    """
    Setup application logger with file and console handlers
    
    Args:
        name (str): Logger name (defaults to root logger)
        level (int): Logging level
    
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler (rotating)
    log_file = log_dir / f"wellness_tracker_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Set levels for specific modules
    logging.getLogger('PyQt5').setLevel(logging.WARNING)
    logging.getLogger('opencv').setLevel(logging.WARNING)
    
    logger.info("Logger initialized successfully")
    return logger

def get_logger(name):
    """Get logger instance for a specific module"""
    return logging.getLogger(name)

def set_debug_mode(enabled=True):
    """Enable or disable debug mode"""
    level = logging.DEBUG if enabled else logging.INFO
    
    # Update all existing loggers
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
        # Update handler levels
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level)

def log_system_info():
    """Log system information for debugging"""
    logger = logging.getLogger(__name__)
    
    import platform
    import sys
    
    logger.info("=" * 50)
    logger.info("SYSTEM INFORMATION")
    logger.info("=" * 50)
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Architecture: {platform.architecture()}")
    logger.info(f"Processor: {platform.processor()}")
    
    try:
        import PyQt5.QtCore
        logger.info(f"PyQt5 Version: {PyQt5.QtCore.QT_VERSION_STR}")
    except ImportError:
        logger.warning("PyQt5 not available")
    
    try:
        import cv2
        logger.info(f"OpenCV Version: {cv2.__version__}")
    except ImportError:
        logger.warning("OpenCV not available")
    
    try:
        import psutil
        logger.info(f"psutil Version: {psutil.__version__}")
    except ImportError:
        logger.warning("psutil not available")
    
    logger.info("=" * 50)
