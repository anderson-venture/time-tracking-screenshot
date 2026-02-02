import os
from pathlib import Path

class ServerConfig:
    """Configuration settings for the central server"""
    
    # Server settings
    HOST = '0.0.0.0'  # Listen on all interfaces
    PORT = 5000
    
    # Authentication
    # IMPORTANT: Change this to a strong random string
    # Must match the API_TOKEN in client configuration
    API_TOKEN = 'CHANGE-THIS-TO-A-STRONG-RANDOM-TOKEN'
    
    # Storage settings
    # Change this to your preferred storage location
    STORAGE_ROOT = os.path.join(os.path.expanduser('~'), 'MonitoringData')
    
    # File upload settings
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB
    ALLOWED_EXTENSIONS = {'.zip'}
    
    # Data retention
    RETENTION_DAYS = 30  # Keep data for 30 days
    
    # Optional: IP whitelist (empty list = allow all)
    # Example: ['192.168.1.0/24', '10.0.0.0/24']
    ALLOWED_IPS = []
    
    @staticmethod
    def ensure_directories():
        """Create necessary directories"""
        os.makedirs(ServerConfig.STORAGE_ROOT, exist_ok=True)
