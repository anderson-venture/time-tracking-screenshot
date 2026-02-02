import os
import json
import threading
import time
import zipfile
import socket
from datetime import datetime
from pathlib import Path
import tempfile
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Config
from storage_manager import StorageManager

class NetworkSync:
    """Syncs local data to central server over local network"""
    
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager
        self.running = False
        self.thread = None
        self.session = self._create_session()
        self.computer_id = self._get_computer_id()
    
    def _create_session(self):
        """Create requests session with retry logic"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def _get_computer_id(self):
        """Get unique computer identifier"""
        # Use hostname as identifier
        return socket.gethostname()
    
    def _create_zip_package(self, events, screenshots):
        """Create a ZIP file containing events and screenshots"""
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_path = os.path.join(temp_dir, f'{self.computer_id}_{timestamp}.zip')
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add events JSON if any
                if events:
                    events_json = json.dumps(events, indent=2)
                    zipf.writestr(f'events_{timestamp}.json', events_json)
                
                # Add screenshots
                for screenshot in screenshots:
                    filepath = screenshot['filepath']
                    if os.path.exists(filepath):
                        filename = os.path.basename(filepath)
                        zipf.write(filepath, f'screenshots/{filename}')
            
            return zip_path
        except Exception as e:
            # Clean up on error
            try:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                os.rmdir(temp_dir)
            except:
                pass
            return None
    
    def upload_data(self, events, screenshots):
        """Upload events and screenshots to central server"""
        if not events and not screenshots:
            return False
        
        # Create ZIP package
        zip_path = self._create_zip_package(events, screenshots)
        if not zip_path:
            return False
        
        try:
            # Prepare the upload
            url = f'http://{Config.SERVER_ADDRESS}:{Config.SERVER_PORT}/upload'
            
            with open(zip_path, 'rb') as f:
                files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
                data = {
                    'computer_id': self.computer_id,
                    'timestamp': datetime.now().isoformat()
                }
                headers = {
                    'X-API-Token': Config.API_TOKEN
                }
                
                # Send request with timeout
                response = self.session.post(
                    url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=30
                )
                
                success = response.status_code == 200
                return success
                
        except Exception as e:
            # Network error - will retry next cycle
            return False
        finally:
            # Clean up ZIP file
            try:
                os.remove(zip_path)
                os.rmdir(os.path.dirname(zip_path))
            except:
                pass
    
    def _sync_loop(self):
        """Main loop for syncing data"""
        while self.running:
            try:
                # Get unsynced data
                events = self.storage_manager.get_unsynced_events()
                screenshots = self.storage_manager.get_unsynced_screenshots()
                
                if events or screenshots:
                    # Try to upload
                    if self.upload_data(events, screenshots):
                        # Mark as synced on success
                        if events:
                            event_ids = [event['id'] for event in events]
                            self.storage_manager.mark_events_synced(event_ids)
                        
                        if screenshots:
                            screenshot_ids = [s['id'] for s in screenshots]
                            self.storage_manager.mark_screenshots_synced(screenshot_ids)
                
                # Cleanup old data
                self.storage_manager.cleanup_old_data()
                
            except Exception as e:
                # Fail silently - will retry next cycle
                pass
            
            # Wait for next sync cycle
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
