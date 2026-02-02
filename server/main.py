import os
import sys
import signal
import schedule
import time
import threading
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ServerConfig
from storage_handler import StorageHandler
from file_receiver import app

class MonitoringServer:
    """Central monitoring server"""
    
    def __init__(self):
        self.storage_handler = StorageHandler()
        self.running = False
        self.cleanup_thread = None
    
    def schedule_cleanup(self):
        """Schedule periodic cleanup of old data"""
        schedule.every().day.at("02:00").do(self.storage_handler.cleanup_old_data)
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start_cleanup_scheduler(self):
        """Start cleanup scheduler in background thread"""
        self.running = True
        self.cleanup_thread = threading.Thread(target=self.schedule_cleanup, daemon=True)
        self.cleanup_thread.start()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
    
    def run(self):
        """Start the HTTP server"""
        # Ensure storage directories exist
        ServerConfig.ensure_directories()
        
        # Start cleanup scheduler
        self.start_cleanup_scheduler()
        
        print("=" * 60)
        print("  Monitoring Server Starting")
        print("=" * 60)
        print(f"Host: {ServerConfig.HOST}")
        print(f"Port: {ServerConfig.PORT}")
        print(f"Storage: {ServerConfig.STORAGE_ROOT}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print("\nEndpoints:")
        print(f"  - POST http://<server-ip>:{ServerConfig.PORT}/upload")
        print(f"  - GET  http://<server-ip>:{ServerConfig.PORT}/health")
        print(f"  - GET  http://<server-ip>:{ServerConfig.PORT}/stats")
        print(f"  - GET  http://<server-ip>:{ServerConfig.PORT}/")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 60)
        print()
        
        # Run Flask app
        try:
            app.run(
                host=ServerConfig.HOST,
                port=ServerConfig.PORT,
                debug=False,
                threaded=True
            )
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.stop()

def signal_handler(signum, frame):
    """Handle termination signals"""
    print("\nReceived signal to terminate. Shutting down...")
    sys.exit(0)

def main():
    """Entry point"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run server
    server = MonitoringServer()
    server.run()

if __name__ == '__main__':
    main()
