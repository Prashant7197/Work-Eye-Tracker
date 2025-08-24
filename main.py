import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

# Add src directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Wellness at Work - Eye Tracker")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Wellness Solutions")
    
    # Set global dark theme
    app.setStyle('Fusion')
    
    # Apply dark theme palette
    from ui.theme import apply_dark_theme
    apply_dark_theme(app)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show main window
    try:
        main_window = MainWindow()
        main_window.show()
        
        logger.info("Application started successfully")
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
