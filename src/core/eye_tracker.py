"""
Eye Tracker - Monitors eye blinks using computer vision
"""
import logging
import cv2
import time
import threading
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

logger = logging.getLogger(__name__)

class EyeTracker(QObject):
    """Eye tracking system using OpenCV and face detection"""
    
    # Signals
    blink_detected = pyqtSignal()
    tracking_started = pyqtSignal()
    tracking_stopped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Tracking state
        self.is_running = False
        self.camera_available = False
        
        # Blink data
        self.total_blinks = 0
        self.session_start_time = None
        self.last_blink_time = None
        self.blink_history = []
        
        # Camera and detection
        self.camera = None
        self.face_cascade = None
        self.eye_cascade = None
        
        # Threading
        self.tracking_thread = None
        self.should_stop = False
        
        # Simulation mode (when camera not available)
        self.simulation_mode = False
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self._simulate_blink)
        
        logger.info("Eye tracker initialized")
    
    def start(self):
        """Start eye tracking"""
        if self.is_running:
            return
        
        logger.info("Starting eye tracker")
        
        try:
            # Try to initialize camera and cascades
            if self._initialize_camera() and self._load_cascades():
                self.camera_available = True
                self.simulation_mode = False
                logger.info("Camera available, using real tracking")
            else:
                self.camera_available = False
                self.simulation_mode = True
                logger.info("Camera not available, using simulation mode")
            
            # Reset tracking data
            self.total_blinks = 0
            self.session_start_time = datetime.now()
            self.blink_history = []
            self.should_stop = False
            
            # Start tracking
            self.is_running = True
            
            if self.simulation_mode:
                # Start simulation timer (random blinks every 3-8 seconds)
                import random
                self.simulation_timer.start(random.randint(3000, 8000))
            else:
                # Start real tracking thread
                self.tracking_thread = threading.Thread(target=self._tracking_loop)
                self.tracking_thread.daemon = True
                self.tracking_thread.start()
            
            self.tracking_started.emit()
            logger.info("Eye tracking started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start eye tracking: {e}")
            self.is_running = False
            raise
    
    def stop(self):
        """Stop eye tracking"""
        if not self.is_running:
            return
        
        logger.info("Stopping eye tracker")
        
        try:
            self.should_stop = True
            self.is_running = False
            
            if self.simulation_mode:
                self.simulation_timer.stop()
            
            # Stop camera
            if self.camera:
                self.camera.release()
                self.camera = None
            
            # Wait for thread to finish
            if self.tracking_thread and self.tracking_thread.is_alive():
                self.tracking_thread.join(timeout=2.0)
            
            self.tracking_stopped.emit()
            logger.info("Eye tracking stopped")
            
        except Exception as e:
            logger.error(f"Error stopping eye tracker: {e}")
    
    def _initialize_camera(self):
        """Initialize camera for eye tracking"""
        try:
            # Try to open default camera
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                logger.warning("Could not open camera")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def _load_cascades(self):
        """Load OpenCV cascade classifiers"""
        try:
            # Load pre-trained cascade classifiers
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            
            if self.face_cascade.empty() or self.eye_cascade.empty():
                logger.error("Failed to load cascade classifiers")
                return False
            
            logger.info("Cascade classifiers loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load cascades: {e}")
            return False
    
    def _tracking_loop(self):
        """Main tracking loop (runs in separate thread)"""
        logger.info("Starting tracking loop")
        
        # Eye state tracking
        eye_closed_frames = 0
        blink_threshold = 5  # Number of consecutive frames with closed eyes to count as blink
        
        try:
            while not self.should_stop and self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                
                if not ret:
                    break
                
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                eyes_detected = False
                
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    
                    # Detect eyes in face region
                    eyes = self.eye_cascade.detectMultiScale(roi_gray)
                    
                    if len(eyes) >= 2:  # Both eyes detected
                        eyes_detected = True
                        break
                
                # Track eye state
                if not eyes_detected:
                    eye_closed_frames += 1
                else:
                    if eye_closed_frames >= blink_threshold:
                        # Blink detected
                        self._record_blink()
                    eye_closed_frames = 0
                
                # Small delay to reduce CPU usage
                time.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            logger.error(f"Error in tracking loop: {e}")
        
        logger.info("Tracking loop ended")
    
    def _simulate_blink(self):
        """Simulate a blink (for demo purposes when camera not available)"""
        self._record_blink()
        
        # Schedule next simulation blink
        import random
        self.simulation_timer.start(random.randint(3000, 8000))
    
    def _record_blink(self):
        """Record a detected blink"""
        current_time = datetime.now()
        
        self.total_blinks += 1
        self.last_blink_time = current_time
        self.blink_history.append(current_time)
        
        # Keep only recent blinks (last 5 minutes for rate calculation)
        cutoff_time = current_time - timedelta(minutes=5)
        self.blink_history = [t for t in self.blink_history if t > cutoff_time]
        
        self.blink_detected.emit()
        logger.debug(f"Blink detected. Total: {self.total_blinks}")
    
    def get_current_data(self):
        """Get current tracking data"""
        current_time = datetime.now()
        
        # Calculate session duration
        if self.session_start_time:
            session_duration = current_time - self.session_start_time
            duration_str = str(session_duration).split('.')[0]  # Remove microseconds
        else:
            duration_str = "00:00:00"
        
        # Calculate blinks per minute
        if self.session_start_time:
            session_minutes = max(1, (current_time - self.session_start_time).total_seconds() / 60)
            blinks_per_minute = self.total_blinks / session_minutes
        else:
            blinks_per_minute = 0
        
        return {
            'total_blinks': self.total_blinks,
            'blinks_per_minute': blinks_per_minute,
            'session_duration': duration_str,
            'last_blink': self.last_blink_time,
            'is_tracking': self.is_running,
            'camera_available': self.camera_available,
            'simulation_mode': self.simulation_mode
        }
    
    def is_camera_available(self):
        """Check if camera is available"""
        return self.camera_available
    
    def get_blink_history(self):
        """Get recent blink history"""
        return self.blink_history.copy()
    
    def reset_session(self):
        """Reset current session data"""
        self.total_blinks = 0
        self.session_start_time = datetime.now()
        self.blink_history = []
        logger.info("Session data reset")
