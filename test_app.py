import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        print("✅ PyQt5 imports successful")
        
        # Test OpenCV
        import cv2
        print("✅ OpenCV import successful")
        
        # Test psutil
        import psutil
        print("✅ psutil import successful")
        
        # Test cryptography
        from cryptography.fernet import Fernet
        print("✅ cryptography import successful")
        
        # Test application modules
        from ui.theme import apply_dark_theme
        from core.auth_manager import AuthManager
        from core.eye_tracker import EyeTracker
        from core.system_monitor import SystemMonitor
        from core.data_manager import DataManager
        from utils.logger import setup_logger
        from utils.config import get_config
        from utils.gdpr import get_gdpr_manager
        
        print("✅ All application modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_initialization():
    """Test basic component initialization"""
    print("\nTesting component initialization...")
    
    try:
        # Test logger
        from utils.logger import setup_logger
        logger = setup_logger()
        print("✅ Logger initialization successful")
        
        # Test config
        from utils.config import get_config
        config = get_config()
        print("✅ Config initialization successful")
        
        # Test GDPR manager
        from utils.gdpr import get_gdpr_manager
        gdpr = get_gdpr_manager()
        print("✅ GDPR manager initialization successful")
        
        # Test auth manager
        from core.auth_manager import AuthManager
        auth = AuthManager()
        print("✅ Auth manager initialization successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_camera():
    """Test camera availability"""
    print("\nTesting camera availability...")
    
    try:
        import cv2
        
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera available")
            cap.release()
        else:
            print("⚠️  No camera found - simulation mode will be used")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Camera test error: {e}")
        print("   Application will use simulation mode")
        return True

def test_system_monitoring():
    """Test system monitoring capabilities"""
    print("\nTesting system monitoring...")
    
    try:
        import psutil
        
        # Test CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        print(f"✅ CPU monitoring: {cpu_percent}%")
        
        # Test memory
        memory = psutil.virtual_memory()
        print(f"✅ Memory monitoring: {memory.percent}%")
        
        # Test network
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            print("✅ Network connectivity: Available")
        except:
            print("⚠️  Network connectivity: Limited")
        
        return True
        
    except Exception as e:
        print(f"❌ System monitoring error: {e}")
        return False

def main():
    """Run all tests"""
    print("🏥 Wellness at Work - Eye Tracker Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    # Run tests
    if test_imports():
        tests_passed += 1
    
    if test_initialization():
        tests_passed += 1
    
    if test_camera():
        tests_passed += 1
    
    if test_system_monitoring():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! Application is ready to run.")
        print("\nTo start the application:")
        print("  python main.py")
        return True
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
