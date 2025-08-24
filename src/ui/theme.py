from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def apply_dark_theme(app):
    # Create dark palette
    dark_palette = QPalette()
    
    # Window colors
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    
    # Base colors (for input fields)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    
    # Tool tip colors
    dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    
    # Text colors
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    
    # Button colors
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    
    # Bright text
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    
    # Link colors
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    
    # Highlight colors
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    
    # Apply palette
    app.setPalette(dark_palette)
    
    # Additional stylesheet for specific widgets
    app.setStyleSheet("""
        QMainWindow {
            background-color: #353535;
        }
        
        QWidget {
            background-color: #353535;
            color: white;
        }
        
        QLineEdit {
            background-color: #2b2b2b;
            border: 1px solid #404040;
            border-radius: 5px;
            padding: 8px;
            color: white;
            font-size: 12px;
        }
        
        QLineEdit:focus {
            border: 2px solid #2a82da;
        }
        
        QPushButton {
            background-color: #2a82da;
            border: none;
            border-radius: 5px;
            color: white;
            font-size: 12px;
            font-weight: bold;
            padding: 10px 20px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #3a92ea;
        }
        
        QPushButton:pressed {
            background-color: #1a72ca;
        }
        
        QPushButton:disabled {
            background-color: #404040;
            color: #808080;
        }
        
        QLabel {
            color: white;
        }
        
        QFrame {
            background-color: #353535;
        }
        
        QGroupBox {
            background-color: #2b2b2b;
            border: 1px solid #404040;
            border-radius: 5px;
            margin: 5px;
            padding-top: 15px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            color: #cccccc;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QProgressBar {
            background-color: #2b2b2b;
            border: 1px solid #404040;
            border-radius: 5px;
            text-align: center;
            color: white;
        }
        
        QProgressBar::chunk {
            background-color: #2a82da;
            border-radius: 3px;
        }
        
        QStatusBar {
            background-color: #2b2b2b;
            border-top: 1px solid #404040;
            color: #cccccc;
        }
        
        QMenuBar {
            background-color: #2b2b2b;
            color: white;
            border-bottom: 1px solid #404040;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        
        QMenuBar::item:selected {
            background-color: #2a82da;
        }
        
        QMenu {
            background-color: #2b2b2b;
            border: 1px solid #404040;
            color: white;
        }
        
        QMenu::item {
            padding: 5px 20px;
        }
        
        QMenu::item:selected {
            background-color: #2a82da;
        }
        
        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #353535;
        }
        
        QTabBar::tab {
            background-color: #2b2b2b;
            border: 1px solid #404040;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #2a82da;
            color: white;
        }
        
        QScrollBar:vertical {
            background-color: #2b2b2b;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #404040;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #505050;
        }
        
        QTableWidget {
            background-color: #2b2b2b;
            border: 1px solid #404040;
            gridline-color: #404040;
            selection-background-color: #2a82da;
        }
        
        QHeaderView::section {
            background-color: #404040;
            color: white;
            padding: 5px;
            border: none;
            font-weight: bold;
        }
    """)

def get_accent_color():
    """Get the accent color used in the theme"""
    return "#2a82da"

def get_background_color():
    """Get the main background color"""
    return "#353535"

def get_secondary_background():
    """Get the secondary background color"""
    return "#2b2b2b"

def get_text_color():
    """Get the main text color"""
    return "#ffffff"

def get_secondary_text_color():
    """Get the secondary text color"""
    return "#cccccc"
