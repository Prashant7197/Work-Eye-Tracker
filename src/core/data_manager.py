"""
Data Manager - Handles local data storage and cloud synchronization
"""
import logging
import sqlite3
import json
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

logger = logging.getLogger(__name__)

class DataManager(QObject):
    """Manages local data storage and cloud synchronization"""
    
    # Signals
    data_saved = pyqtSignal(dict)
    sync_completed = pyqtSignal(bool)  # success
    sync_status_changed = pyqtSignal(str)  # status message
    
    def __init__(self):
        super().__init__()
        
        # Database path
        self.db_path = Path("data/wellness_tracker.db")
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Sync state
        self.is_syncing = False
        self.last_sync_time = None
        self.pending_sync_count = 0
        
        # Auto-sync timer
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.sync_data)
        
        # Thread lock for database operations
        self.db_lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        # Start auto-sync (every 5 minutes)
        self.sync_timer.start(300000)
        
        logger.info("Data manager initialized")
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create eye tracking sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS eye_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        session_start TIMESTAMP NOT NULL,
                        session_end TIMESTAMP,
                        total_blinks INTEGER DEFAULT 0,
                        blinks_per_minute REAL DEFAULT 0.0,
                        eye_strain_level TEXT DEFAULT 'normal',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        synced INTEGER DEFAULT 0
                    )
                ''')
                
                # Create system metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        cpu_percent REAL NOT NULL,
                        memory_percent REAL NOT NULL,
                        memory_used_mb REAL NOT NULL,
                        disk_usage_percent REAL,
                        network_available INTEGER DEFAULT 0,
                        battery_percent REAL,
                        power_connected INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        synced INTEGER DEFAULT 0
                    )
                ''')
                
                # Create blink events table (detailed tracking)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS blink_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        session_id INTEGER,
                        timestamp TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        synced INTEGER DEFAULT 0,
                        FOREIGN KEY (session_id) REFERENCES eye_sessions (id)
                    )
                ''')
                
                # Create sync log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sync_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sync_time TIMESTAMP NOT NULL,
                        records_synced INTEGER NOT NULL,
                        success INTEGER NOT NULL,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_session_data(self, eye_data, system_data):
        """Save current session data to local database"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get current user (from auth manager or default)
                    user_id = self._get_current_user_id()
                    current_time = datetime.now()
                    
                    # Save system metrics
                    cursor.execute('''
                        INSERT INTO system_metrics 
                        (user_id, timestamp, cpu_percent, memory_percent, memory_used_mb,
                         disk_usage_percent, network_available, battery_percent, power_connected)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id,
                        current_time,
                        system_data.get('cpu_percent', 0),
                        system_data.get('memory_percent', 0),
                        system_data.get('memory_used_mb', 0),
                        system_data.get('disk_usage_percent', 0),
                        1 if system_data.get('network_available', False) else 0,
                        system_data.get('battery_percent'),
                        1 if system_data.get('power_connected', False) else 0
                    ))
                    
                    # Update pending sync count
                    self.pending_sync_count += 1
                    
                    conn.commit()
                    
                    logger.debug("Session data saved to local database")
                    self.data_saved.emit({
                        'eye_data': eye_data,
                        'system_data': system_data,
                        'timestamp': current_time
                    })
                    
        except Exception as e:
            logger.error(f"Failed to save session data: {e}")
    
    def save_blink_event(self, user_id, session_id=None):
        """Save individual blink event"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO blink_events (user_id, session_id, timestamp)
                        VALUES (?, ?, ?)
                    ''', (user_id, session_id, datetime.now()))
                    
                    conn.commit()
                    logger.debug("Blink event saved")
                    
        except Exception as e:
            logger.error(f"Failed to save blink event: {e}")
    
    def start_eye_session(self, user_id):
        """Start a new eye tracking session"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO eye_sessions (user_id, session_start)
                        VALUES (?, ?)
                    ''', (user_id, datetime.now()))
                    
                    session_id = cursor.lastrowid
                    conn.commit()
                    
                    logger.info(f"Started eye tracking session {session_id} for user {user_id}")
                    return session_id
                    
        except Exception as e:
            logger.error(f"Failed to start eye session: {e}")
            return None
    
    def end_eye_session(self, session_id, total_blinks, blinks_per_minute):
        """End eye tracking session with summary data"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Determine eye strain level
                    if blinks_per_minute < 10:
                        strain_level = 'high'
                    elif blinks_per_minute < 15:
                        strain_level = 'moderate'
                    else:
                        strain_level = 'normal'
                    
                    cursor.execute('''
                        UPDATE eye_sessions 
                        SET session_end = ?, total_blinks = ?, blinks_per_minute = ?, eye_strain_level = ?
                        WHERE id = ?
                    ''', (datetime.now(), total_blinks, blinks_per_minute, strain_level, session_id))
                    
                    conn.commit()
                    logger.info(f"Ended eye tracking session {session_id}")
                    
        except Exception as e:
            logger.error(f"Failed to end eye session: {e}")
    
    def get_session_stats(self, user_id, days=7):
        """Get session statistics for the last N days"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cutoff_date = datetime.now() - timedelta(days=days)
                    
                    # Get eye tracking stats
                    cursor.execute('''
                        SELECT 
                            COUNT(*) as session_count,
                            AVG(total_blinks) as avg_blinks,
                            AVG(blinks_per_minute) as avg_bpm,
                            SUM(CASE WHEN eye_strain_level = 'high' THEN 1 ELSE 0 END) as high_strain_sessions
                        FROM eye_sessions 
                        WHERE user_id = ? AND session_start >= ?
                    ''', (user_id, cutoff_date))
                    
                    eye_stats = cursor.fetchone()
                    
                    # Get system performance averages
                    cursor.execute('''
                        SELECT 
                            AVG(cpu_percent) as avg_cpu,
                            AVG(memory_percent) as avg_memory
                        FROM system_metrics 
                        WHERE user_id = ? AND timestamp >= ?
                    ''', (user_id, cutoff_date))
                    
                    system_stats = cursor.fetchone()
                    
                    return {
                        'eye_stats': {
                            'session_count': eye_stats[0] or 0,
                            'avg_blinks': eye_stats[1] or 0,
                            'avg_bpm': eye_stats[2] or 0,
                            'high_strain_sessions': eye_stats[3] or 0
                        },
                        'system_stats': {
                            'avg_cpu': system_stats[0] or 0,
                            'avg_memory': system_stats[1] or 0
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return None
    
    def sync_data(self):
        """Synchronize local data with cloud (placeholder implementation)"""
        if self.is_syncing:
            return
        
        logger.info("Starting data synchronization")
        self.is_syncing = True
        self.sync_status_changed.emit("Syncing...")
        
        try:
            # Get unsynced records
            unsynced_count = self._get_unsynced_count()
            
            if unsynced_count == 0:
                logger.info("No data to sync")
                self.sync_status_changed.emit("Up to date")
                self.sync_completed.emit(True)
                return
            
            # Simulate cloud sync (in production, this would make API calls)
            success = self._simulate_cloud_sync()
            
            if success:
                self._mark_records_as_synced()
                self.last_sync_time = datetime.now()
                self.pending_sync_count = 0
                
                self._log_sync_result(unsynced_count, True, None)
                self.sync_status_changed.emit("Sync complete")
                self.sync_completed.emit(True)
                
                logger.info(f"Successfully synced {unsynced_count} records")
            else:
                self._log_sync_result(unsynced_count, False, "Simulated failure")
                self.sync_status_changed.emit("Sync failed")
                self.sync_completed.emit(False)
                
                logger.warning("Data sync failed")
                
        except Exception as e:
            logger.error(f"Error during data sync: {e}")
            self._log_sync_result(0, False, str(e))
            self.sync_status_changed.emit("Sync error")
            self.sync_completed.emit(False)
        
        finally:
            self.is_syncing = False
    
    def _get_unsynced_count(self):
        """Get count of unsynced records"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('SELECT COUNT(*) FROM system_metrics WHERE synced = 0')
                    metrics_count = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT COUNT(*) FROM eye_sessions WHERE synced = 0')
                    sessions_count = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT COUNT(*) FROM blink_events WHERE synced = 0')
                    blinks_count = cursor.fetchone()[0]
                    
                    return metrics_count + sessions_count + blinks_count
                    
        except Exception as e:
            logger.error(f"Failed to get unsynced count: {e}")
            return 0
    
    def _simulate_cloud_sync(self):
        """Simulate cloud synchronization (placeholder)"""
        import time
        import random
        
        # Simulate network delay
        time.sleep(1)
        
        # Simulate occasional failures (10% chance)
        return random.random() > 0.1
    
    def _mark_records_as_synced(self):
        """Mark all unsynced records as synced"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('UPDATE system_metrics SET synced = 1 WHERE synced = 0')
                    cursor.execute('UPDATE eye_sessions SET synced = 1 WHERE synced = 0')
                    cursor.execute('UPDATE blink_events SET synced = 1 WHERE synced = 0')
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Failed to mark records as synced: {e}")
    
    def _log_sync_result(self, records_synced, success, error_message):
        """Log sync operation result"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO sync_log (sync_time, records_synced, success, error_message)
                        VALUES (?, ?, ?, ?)
                    ''', (datetime.now(), records_synced, 1 if success else 0, error_message))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Failed to log sync result: {e}")
    
    def _get_current_user_id(self):
        """Get current user ID (placeholder - would integrate with auth manager)"""
        # In production, this would get the user ID from the authentication manager
        return "demo_user"
    
    def save_pending_data(self):
        """Save any pending data before shutdown"""
        try:
            # Force sync any remaining data
            if self.pending_sync_count > 0:
                logger.info(f"Saving {self.pending_sync_count} pending records")
                # In production, might save to a backup file or queue for next startup
                
        except Exception as e:
            logger.error(f"Error saving pending data: {e}")
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            with self.db_lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get table counts
                    cursor.execute('SELECT COUNT(*) FROM eye_sessions')
                    sessions_count = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT COUNT(*) FROM system_metrics')
                    metrics_count = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT COUNT(*) FROM blink_events')
                    blinks_count = cursor.fetchone()[0]
                    
                    # Get unsynced counts
                    cursor.execute('SELECT COUNT(*) FROM system_metrics WHERE synced = 0')
                    unsynced_metrics = cursor.fetchone()[0]
                    
                    return {
                        'total_sessions': sessions_count,
                        'total_metrics': metrics_count,
                        'total_blinks': blinks_count,
                        'unsynced_count': unsynced_metrics,
                        'last_sync': self.last_sync_time,
                        'database_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return None
