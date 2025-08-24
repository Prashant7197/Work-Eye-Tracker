"""
System Monitor - Monitors system performance metrics
"""
import logging
import psutil
import time
import threading
import socket
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class SystemMonitor(QObject):
    """System performance monitoring using psutil"""
    
    # Signals
    metrics_updated = pyqtSignal(dict)
    monitoring_started = pyqtSignal()
    monitoring_stopped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Monitoring state
        self.is_running = False
        self.should_stop = False
        
        # Monitoring thread
        self.monitoring_thread = None
        
        # Current metrics
        self.current_metrics = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_used_mb': 0.0,
            'memory_total_mb': 0.0,
            'disk_usage_percent': 0.0,
            'network_available': False,
            'battery_percent': None,
            'power_connected': None,
            'process_count': 0,
            'boot_time': None
        }
        
        # Initialize system info
        self._get_system_info()
        
        logger.info("System monitor initialized")
    
    def start(self):
        """Start system monitoring"""
        if self.is_running:
            return
        
        logger.info("Starting system monitor")
        
        try:
            self.should_stop = False
            self.is_running = True
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            self.monitoring_started.emit()
            logger.info("System monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start system monitoring: {e}")
            self.is_running = False
            raise
    
    def stop(self):
        """Stop system monitoring"""
        if not self.is_running:
            return
        
        logger.info("Stopping system monitor")
        
        try:
            self.should_stop = True
            self.is_running = False
            
            # Wait for thread to finish
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=2.0)
            
            self.monitoring_stopped.emit()
            logger.info("System monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping system monitor: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop (runs in separate thread)"""
        logger.info("Starting monitoring loop")
        
        try:
            while not self.should_stop:
                # Update all metrics
                self._update_cpu_metrics()
                self._update_memory_metrics()
                self._update_disk_metrics()
                self._update_network_status()
                self._update_battery_metrics()
                self._update_process_count()
                
                # Emit updated metrics
                self.metrics_updated.emit(self.current_metrics.copy())
                
                # Wait before next update
                time.sleep(2.0)  # Update every 2 seconds
                
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
        
        logger.info("Monitoring loop ended")
    
    def _update_cpu_metrics(self):
        """Update CPU usage metrics"""
        try:
            # Get CPU percentage (non-blocking)
            cpu_percent = psutil.cpu_percent(interval=None)
            self.current_metrics['cpu_percent'] = cpu_percent
            
        except Exception as e:
            logger.error(f"Error updating CPU metrics: {e}")
    
    def _update_memory_metrics(self):
        """Update memory usage metrics"""
        try:
            # Get memory info
            memory = psutil.virtual_memory()
            
            self.current_metrics['memory_percent'] = memory.percent
            self.current_metrics['memory_used_mb'] = memory.used / (1024 * 1024)
            self.current_metrics['memory_total_mb'] = memory.total / (1024 * 1024)
            
        except Exception as e:
            logger.error(f"Error updating memory metrics: {e}")
    
    def _update_disk_metrics(self):
        """Update disk usage metrics"""
        try:
            # Get disk usage for root/C: drive
            if hasattr(psutil, 'disk_usage'):
                disk = psutil.disk_usage('/')
                self.current_metrics['disk_usage_percent'] = (disk.used / disk.total) * 100
            
        except Exception as e:
            logger.error(f"Error updating disk metrics: {e}")
    
    def _update_network_status(self):
        """Update network connectivity status"""
        try:
            # Check if we can connect to a public DNS server
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            self.current_metrics['network_available'] = True
            
        except socket.error:
            self.current_metrics['network_available'] = False
        except Exception as e:
            logger.error(f"Error checking network status: {e}")
            self.current_metrics['network_available'] = False
    
    def _update_battery_metrics(self):
        """Update battery status (if available)"""
        try:
            if hasattr(psutil, 'sensors_battery'):
                battery = psutil.sensors_battery()
                if battery:
                    self.current_metrics['battery_percent'] = battery.percent
                    self.current_metrics['power_connected'] = battery.power_plugged
                else:
                    # Desktop/no battery
                    self.current_metrics['battery_percent'] = None
                    self.current_metrics['power_connected'] = True
            
        except Exception as e:
            logger.error(f"Error updating battery metrics: {e}")
    
    def _update_process_count(self):
        """Update running process count"""
        try:
            self.current_metrics['process_count'] = len(psutil.pids())
            
        except Exception as e:
            logger.error(f"Error updating process count: {e}")
    
    def _get_system_info(self):
        """Get static system information"""
        try:
            # Get boot time
            self.current_metrics['boot_time'] = datetime.fromtimestamp(psutil.boot_time())
            
            # Initial CPU reading (to enable non-blocking subsequent calls)
            psutil.cpu_percent(interval=1)
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
    
    def get_current_data(self):
        """Get current monitoring data"""
        return self.current_metrics.copy()
    
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        return self.current_metrics['cpu_percent']
    
    def get_memory_usage(self):
        """Get current memory usage info"""
        return {
            'percent': self.current_metrics['memory_percent'],
            'used_mb': self.current_metrics['memory_used_mb'],
            'total_mb': self.current_metrics['memory_total_mb']
        }
    
    def get_network_status(self):
        """Get network connectivity status"""
        return self.current_metrics['network_available']
    
    def get_battery_info(self):
        """Get battery information"""
        return {
            'percent': self.current_metrics['battery_percent'],
            'power_connected': self.current_metrics['power_connected']
        }
    
    def get_system_uptime(self):
        """Get system uptime"""
        if self.current_metrics['boot_time']:
            uptime = datetime.now() - self.current_metrics['boot_time']
            return str(uptime).split('.')[0]  # Remove microseconds
        return "Unknown"
    
    def get_power_impact_estimate(self):
        """Estimate power impact based on CPU and other metrics"""
        try:
            cpu_impact = self.current_metrics['cpu_percent']
            
            # Simple estimation: high CPU = higher power impact
            if cpu_impact > 80:
                return "High"
            elif cpu_impact > 50:
                return "Medium"
            elif cpu_impact > 20:
                return "Low"
            else:
                return "Very Low"
                
        except Exception as e:
            logger.error(f"Error estimating power impact: {e}")
            return "Unknown"
