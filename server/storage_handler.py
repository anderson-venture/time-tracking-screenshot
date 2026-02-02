import os
import zipfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from config import ServerConfig

class StorageHandler:
    """Handles storage and organization of received files"""
    
    def __init__(self):
        ServerConfig.ensure_directories()
        self.storage_root = ServerConfig.STORAGE_ROOT
    
    def _get_computer_folder(self, computer_id):
        """Get the folder path for a specific computer"""
        # Sanitize computer_id to prevent path traversal
        safe_id = "".join(c for c in computer_id if c.isalnum() or c in ('-', '_'))
        return os.path.join(self.storage_root, safe_id)
    
    def _get_date_folder(self, computer_folder):
        """Get the folder path for today's date"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(computer_folder, date_str)
    
    def save_upload(self, zip_path, computer_id):
        """
        Extract and organize uploaded ZIP file
        
        Args:
            zip_path: Path to uploaded ZIP file
            computer_id: Identifier for the computer
            
        Returns:
            bool: True if successful
        """
        try:
            # Create directory structure
            computer_folder = self._get_computer_folder(computer_id)
            date_folder = self._get_date_folder(computer_folder)
            os.makedirs(date_folder, exist_ok=True)
            
            # Extract ZIP contents
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of files in ZIP
                for member in zip_ref.namelist():
                    # Sanitize paths to prevent directory traversal
                    member_path = os.path.normpath(member)
                    if member_path.startswith('..') or member_path.startswith('/'):
                        continue
                    
                    # Extract to date folder
                    target_path = os.path.join(date_folder, member_path)
                    
                    # Create subdirectories if needed
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    # Extract file
                    with zip_ref.open(member) as source:
                        with open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
            
            return True
            
        except Exception as e:
            print(f"Error saving upload: {e}")
            return False
    
    def cleanup_old_data(self):
        """Remove data older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=ServerConfig.RETENTION_DAYS)
            
            # Iterate through all computer folders
            for computer_folder in Path(self.storage_root).iterdir():
                if not computer_folder.is_dir():
                    continue
                
                # Check each date folder
                for date_folder in computer_folder.iterdir():
                    if not date_folder.is_dir():
                        continue
                    
                    # Parse date from folder name
                    try:
                        folder_date = datetime.strptime(date_folder.name, '%Y-%m-%d')
                        if folder_date < cutoff_date:
                            # Delete old folder
                            shutil.rmtree(date_folder)
                            print(f"Cleaned up old data: {date_folder}")
                    except ValueError:
                        # Skip folders that don't match date format
                        continue
                
                # Remove empty computer folders
                if not any(computer_folder.iterdir()):
                    computer_folder.rmdir()
                    
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def get_statistics(self):
        """Get statistics about stored data"""
        stats = {
            'total_computers': 0,
            'total_size_mb': 0,
            'computers': {}
        }
        
        try:
            for computer_folder in Path(self.storage_root).iterdir():
                if not computer_folder.is_dir():
                    continue
                
                computer_id = computer_folder.name
                stats['total_computers'] += 1
                
                # Calculate size for this computer
                total_size = 0
                file_count = 0
                
                for item in computer_folder.rglob('*'):
                    if item.is_file():
                        total_size += item.stat().st_size
                        file_count += 1
                
                stats['computers'][computer_id] = {
                    'size_mb': round(total_size / (1024 * 1024), 2),
                    'file_count': file_count
                }
                
                stats['total_size_mb'] += stats['computers'][computer_id]['size_mb']
            
            stats['total_size_mb'] = round(stats['total_size_mb'], 2)
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
        
        return stats
