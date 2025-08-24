import sys
import subprocess
import platform
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_platform():
    """Check platform compatibility"""
    system = platform.system()
    print(f"✅ Platform: {system} {platform.release()}")
    
    if system not in ["Windows", "Darwin", "Linux"]:
        print("⚠️  Platform may not be fully supported")
        return False
    
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install from requirements.txt
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install dependencies")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "data",
        "logs", 
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created: {directory}/")

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    modules = [
        ("PyQt5.QtWidgets", "PyQt5"),
        ("cv2", "OpenCV"),
        ("psutil", "psutil"),
        ("cryptography.fernet", "cryptography")
    ]
    
    failed_imports = []
    
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name}")
            failed_imports.append(name)
    
    return len(failed_imports) == 0

def test_camera():
    """Test camera availability"""
    print("\n📷 Testing camera...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            print("✅ Camera detected")
            cap.release()
            return True
        else:
            print("⚠️  No camera detected - simulation mode will be used")
            return True
            
    except Exception as e:
        print(f"⚠️  Camera test failed: {e}")
        print("   Simulation mode will be used")
        return True

def main():
    """Main setup function"""
    print("🏥 Wellness at Work - Eye Tracker Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_platform():
        print("⚠️  Continuing with potentially unsupported platform...")
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed - could not install dependencies")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n❌ Setup incomplete - some modules failed to import")
        print("Try installing missing dependencies manually:")
        print("pip install PyQt5 opencv-python psutil cryptography")
        sys.exit(1)
    
    # Test camera
    test_camera()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nTo run the application:")
    print("  python main.py")
    print("\nDemo login credentials:")
    print("  Username: admin / Password: password")
    print("  Username: demo  / Password: demo")

if __name__ == "__main__":
    main()
