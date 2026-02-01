import os
import json
import threading
import time
from datetime import datetime
from pathlib import Path
try:
    import firebase_admin
    from firebase_admin import credentials, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

from config import Config
from storage_manager import StorageManager

class FirebaseSync:
    """Syncs local data to Firebase Storage"""
    
    def __init__(self, storage_manager, credentials_path=None):
        self.storage_manager = storage_manager
        self.running = False
        self.thread = None
        self.bucket = None
        self.initialized = False
        
        if FIREBASE_AVAILABLE and credentials_path and os.path.exists(credentials_path):
            self._initialize_firebase(credentials_path)
    
    def _initialize_firebase(self, credentials_path):
        """Initialize Firebase Admin SDK"""
        try:
            # Initialize Firebase app
            cred = credentials.Certificate(credentials_path)
            
            # Check if already initialized
            try:
                firebase_admin.get_app()
            except ValueError:
                firebase_admin.initialize_app(cred, {
                    'storageBucket': Config.FIREBASE_BUCKET_NAME
                })
            
            self.bucket = storage.bucket()
            self.initialized = True
            
        except Exception as e:
            # Fail silently - will just keep data local
            self.initialized = False
    
    def upload_file(self, local_path, remote_path):
        """Upload a file to Firebase Storage"""
        if not self.initialized or not self.bucket:
            return False
        
        try:
            blob = self.bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
            return True
        except Exception as e:
            return False
    
    def upload_events(self):
        """Upload unsynced events to Firebase"""
        if not self.initialized:
            return
        
        events = self.storage_manager.get_unsynced_events()
        if not events:
            return
        
        # Group events into a JSON file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"events_{timestamp}.json"
        local_path = os.path.join(Config.EVENTS_FOLDER, filename)
        
        # Write events to temporary JSON file
        with open(local_path, 'w') as f:
            json.dump(events, f, indent=2)
        
        # Upload to Firebase
        remote_path = f"events/{filename}"
        if self.upload_file(local_path, remote_path):
            # Mark as synced
            event_ids = [event['id'] for event in events]
            self.storage_manager.mark_events_synced(event_ids)
            
            # Clean up local temp file
            try:
                os.remove(local_path)
            except:
                pass
    
    def upload_screenshots(self):
        """Upload unsynced screenshots to Firebase"""
        if not self.initialized:
            return
        
        screenshots = self.storage_manager.get_unsynced_screenshots()
        
        synced_ids = []
        for screenshot in screenshots:
            filepath = screenshot['filepath']
            if not os.path.exists(filepath):
                continue
            
            # Generate remote path
            filename = os.path.basename(filepath)
            remote_path = f"screenshots/{filename}"
            
            # Upload
            if self.upload_file(filepath, remote_path):
                synced_ids.append(screenshot['id'])
        
        # Mark as synced
        if synced_ids:
            self.storage_manager.mark_screenshots_synced(synced_ids)
    
    def _sync_loop(self):
        """Main loop for syncing data"""
        while self.running:
            try:
                self.upload_events()
                self.upload_screenshots()
                
                # Cleanup old data
                self.storage_manager.cleanup_old_data()
                
            except Exception as e:
                # Fail silently
                pass
            
            time.sleep(Config.SYNC_INTERVAL)
    
    def start(self):
        """Start the sync service"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the sync service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
