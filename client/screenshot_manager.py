import os
import threading
import time
from datetime import datetime
from PIL import ImageGrab
from config import Config
from storage_manager import StorageManager

class ScreenshotManager:
    """Captures and compresses screenshots at regular intervals"""
    
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager
        self.running = False
        self.thread = None
    
    def capture_screenshot(self):
        """Capture and save a compressed screenshot"""
        try:
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.jpg"
            filepath = os.path.join(Config.SCREENSHOTS_FOLDER, filename)
            
            # Save with compression
            screenshot.save(filepath, 'JPEG', quality=Config.SCREENSHOT_QUALITY, optimize=True)
            
            # Get file size
            filesize = os.path.getsize(filepath)
            
            # Log to database
            self.storage_manager.log_screenshot(filepath, filesize)
            
        except Exception as e:
            # Fail silently - don't interrupt the monitoring
            pass
    
    def _screenshot_loop(self):
        """Main loop for taking screenshots"""
        while self.running:
            self.capture_screenshot()
            time.sleep(Config.SCREENSHOT_INTERVAL)
    
    def start(self):
        """Start capturing screenshots"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._screenshot_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop capturing screenshots"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
