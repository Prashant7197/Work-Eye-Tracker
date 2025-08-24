# Wellness at Work - Eye Tracker Desktop Application

A cross-platform desktop application built with PyQt5 that monitors eye blinks and system performance to promote workplace wellness.

## Features

### 🔍 Eye Tracking
- Real-time blink detection using computer vision
- Eye strain monitoring based on blink frequency
- Session tracking and statistics
- Camera integration with fallback simulation mode

### 📊 System Performance Monitoring
- CPU usage tracking
- Memory usage monitoring
- Power/Energy impact assessment
- Network connectivity status

### 🔐 User Authentication
- Secure login system
- Session management
- User-specific data tracking

### 💾 Data Management
- Local SQLite database storage
- Offline data handling
- Automatic cloud synchronization (when online)
- Data export and backup capabilities

### 🛡️ GDPR Compliance
- Data encryption at rest
- User consent management
- Right to data deletion
- Data portability features
- Privacy-first design

## Installation

### Prerequisites
- Python 3.7 or higher
- Webcam (optional - simulation mode available)
- Windows 10/11 or macOS 10.14+

### Setup

1. **Clone or download the application**
   ```bash
   # If using git
   git clone <repository-url>
   cd wellness-task
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### First Time Setup

1. **Launch the application**
   - Run `python main.py`
   - The application will start with a dark theme

2. **Login**
   - Use demo credentials:
     - Username: `admin` / Password: `password`
     - Username: `user` / Password: `user123` 
     - Username: `demo` / Password: `demo`

3. **Start Monitoring**
   - Click "Start Monitoring" in the dashboard
   - Grant camera permissions if prompted
   - If camera is unavailable, simulation mode will activate

### Dashboard Overview

#### Eye Tracking Panel
- **Blink Counter**: Real-time blink count for current session
- **Blinks/Minute**: Average blink rate
- **Session Time**: Duration of current monitoring session
- **Eye Strain**: Assessment based on blink frequency
  - Normal: 15+ blinks/minute
  - Moderate: 10-15 blinks/minute  
  - High Strain: <10 blinks/minute

#### System Performance Panel
- **CPU Usage**: Current processor utilization
- **Memory Usage**: RAM consumption percentage
- **Power Impact**: Estimated energy consumption
- **Network Status**: Connectivity indicator

#### Data Sync Status
- **Sync Status**: Shows online/offline mode
- **Last Sync**: Timestamp of last cloud synchronization
- **GDPR Indicator**: Compliance status

### Features in Detail

#### Eye Tracking
The application uses OpenCV for real-time face and eye detection:
- Detects faces using Haar cascades
- Monitors eye regions for blink detection
- Counts consecutive frames with closed eyes
- Records blink events with timestamps

#### System Monitoring  
Utilizes psutil for cross-platform system metrics:
- CPU percentage (updated every 2 seconds)
- Memory usage in MB and percentage
- Network connectivity testing
- Battery status (on laptops)

#### Data Storage
- **Local Database**: SQLite for offline operation
- **Automatic Sync**: Attempts cloud sync every 5 minutes
- **Offline Mode**: Continues operation without internet
- **Data Retention**: Configurable retention period

## GDPR Compliance

This application is designed with privacy and GDPR compliance in mind:

### Data Collection
- **Minimal Data**: Only collects necessary wellness metrics
- **User Consent**: Explicit consent required for data processing
- **Local First**: Data stored locally by default

### Data Protection
- **Encryption**: All sensitive data encrypted using Fernet (AES 128)
- **Anonymization**: Optional data anonymization features
- **Access Control**: User-specific data isolation

### User Rights
The application supports all GDPR user rights:

#### Right to Access
- Users can view all collected data
- Export functionality for data portability
- Transparent data processing information

#### Right to Rectification
- Users can correct inaccurate data
- Update personal information through settings

#### Right to Erasure (Right to be Forgotten)
```python
# Example: Delete user data
from src.utils.gdpr import get_gdpr_manager
gdpr = get_gdpr_manager()
gdpr.delete_user_data("username")
```

#### Right to Data Portability
```python
# Example: Export user data
data = gdpr.export_user_data("username")
```

#### Right to Object
- Users can opt-out of specific data processing
- Granular consent management
- Easy consent withdrawal

### Consent Management
The application implements comprehensive consent tracking:

```python
# Recording consent
gdpr.record_consent("username", "data_collection", granted=True)

# Checking consent
has_consent = gdpr.check_consent("username", "analytics")

# Revoking consent
gdpr.revoke_consent("username", "data_collection")
```

### Data Retention
- **Default**: 30 days retention period
- **Configurable**: Adjustable in settings
- **Automatic Cleanup**: Old data automatically purged
- **Secure Deletion**: Cryptographic erasure of sensitive data

### Security Measures
1. **Encryption at Rest**: All databases encrypted
2. **No Cloud by Default**: Operates offline-first
3. **Minimal Network**: Only syncs when explicitly enabled
4. **Secure Logging**: No sensitive data in log files
5. **Key Management**: Secure encryption key storage

## Configuration

The application uses a JSON configuration file at `config/app_config.json`:

```json
{
  "privacy": {
    "gdpr_compliance": true,
    "data_encryption": true,
    "anonymize_data": false,
    "consent_required": true
  },
  "data": {
    "retention_days": 30,
    "auto_sync_enabled": true,
    "sync_interval_minutes": 5
  }
}
```

## Architecture

### Project Structure
```
wellness-task/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── ui/                # User interface components
│   │   ├── main_window.py # Main application window
│   │   ├── auth_widget.py # Authentication screen
│   │   ├── dashboard_widget.py # Main dashboard
│   │   ├── status_bar.py  # Status bar component
│   │   └── theme.py       # Dark theme styling
│   ├── core/              # Core business logic
│   │   ├── auth_manager.py # User authentication
│   │   ├── eye_tracker.py # Eye tracking system
│   │   ├── system_monitor.py # System monitoring
│   │   └── data_manager.py # Data storage & sync
│   └── utils/             # Utility modules
│       ├── logger.py      # Logging configuration
│       ├── config.py      # Configuration management
│       └── gdpr.py        # GDPR compliance tools
├── data/                  # Local data storage
│   ├── wellness_tracker.db # SQLite database
│   └── user_consent.json # Consent records
├── logs/                  # Application logs
└── config/                # Configuration files
    └── app_config.json    # Application settings
```

### Key Components

#### UI Layer (`src/ui/`)
- **MainWindow**: Primary application window with navigation
- **AuthWidget**: User login and authentication
- **DashboardWidget**: Main monitoring interface
- **Theme**: Dark theme implementation for modern UI

#### Core Logic (`src/core/`)
- **AuthManager**: Handles user authentication and sessions
- **EyeTracker**: Computer vision-based eye blink detection
- **SystemMonitor**: Cross-platform system performance monitoring
- **DataManager**: Local storage and cloud synchronization

#### Utilities (`src/utils/`)
- **Logger**: Structured logging with file rotation
- **Config**: JSON-based configuration management
- **GDPR**: Privacy compliance and data protection tools

## Dependencies

### Core Dependencies
- **PyQt5**: Cross-platform GUI framework
- **OpenCV**: Computer vision for eye tracking
- **psutil**: System and process utilities
- **cryptography**: Data encryption for GDPR compliance

### Optional Dependencies
- **jsonschema**: Configuration validation
- **python-dateutil**: Enhanced date/time handling

## Troubleshooting

### Camera Issues
- **No Camera**: Application automatically switches to simulation mode
- **Permission Denied**: Check system camera permissions
- **Poor Detection**: Ensure good lighting and face visibility

### Performance Issues
- **High CPU Usage**: Reduce camera resolution in settings
- **Memory Leaks**: Restart application if memory usage grows
- **Slow UI**: Check if debug logging is enabled

### Data Issues
- **Sync Failures**: Check network connectivity
- **Database Errors**: Check file permissions in data directory
- **Missing Data**: Verify data retention settings

## Development

### Adding Features
1. Follow the modular architecture
2. Update configuration schema if needed
3. Add appropriate logging
4. Ensure GDPR compliance for any new data collection

### Testing
```bash
# Install development dependencies
pip install pytest black flake8

# Run tests (when implemented)
pytest tests/

# Code formatting
black src/

# Linting
flake8 src/
```

## License

This application is developed for educational and wellness purposes. Please ensure compliance with local privacy laws and regulations when deploying.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs in the `logs/` directory
3. Verify configuration in `config/app_config.json`

---

**Note**: This application prioritizes user privacy and GDPR compliance. All data processing is transparent, consensual, and designed with privacy-by-design principles.
