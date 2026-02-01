import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from config import Config

class StorageManager:
    """Manages local file storage for events and screenshots"""
    
    def __init__(self):
        Config.ensure_directories()
        self.db_path = Config.DB_PATH
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for event logging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        # Screenshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filepath TEXT NOT NULL,
                filesize INTEGER,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_event(self, event_type, details):
        """Log a keyboard or mouse event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        details_json = json.dumps(details)
        
        cursor.execute(
            'INSERT INTO events (timestamp, event_type, details) VALUES (?, ?, ?)',
            (timestamp, event_type, details_json)
        )
        
        conn.commit()
        conn.close()
    
    def log_screenshot(self, filepath, filesize):
        """Log a screenshot capture"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            'INSERT INTO screenshots (timestamp, filepath, filesize) VALUES (?, ?, ?)',
            (timestamp, filepath, filesize)
        )
        
        conn.commit()
        conn.close()
    
    def get_unsynced_events(self, limit=100):
        """Get events that haven't been synced yet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, timestamp, event_type, details FROM events WHERE synced = 0 LIMIT ?',
            (limit,)
        )
        
        events = cursor.fetchall()
        conn.close()
        
        return [
            {'id': row[0], 'timestamp': row[1], 'event_type': row[2], 'details': json.loads(row[3])}
            for row in events
        ]
    
    def get_unsynced_screenshots(self, limit=50):
        """Get screenshots that haven't been synced yet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, timestamp, filepath, filesize FROM screenshots WHERE synced = 0 LIMIT ?',
            (limit,)
        )
        
        screenshots = cursor.fetchall()
        conn.close()
        
        return [
            {'id': row[0], 'timestamp': row[1], 'filepath': row[2], 'filesize': row[3]}
            for row in screenshots
        ]
    
    def mark_events_synced(self, event_ids):
        """Mark events as synced"""
        if not event_ids:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(event_ids))
        cursor.execute(
            f'UPDATE events SET synced = 1 WHERE id IN ({placeholders})',
            event_ids
        )
        
        conn.commit()
        conn.close()
    
    def mark_screenshots_synced(self, screenshot_ids):
        """Mark screenshots as synced"""
        if not screenshot_ids:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(screenshot_ids))
        cursor.execute(
            f'UPDATE screenshots SET synced = 1 WHERE id IN ({placeholders})',
            screenshot_ids
        )
        
        conn.commit()
        conn.close()
    
    def cleanup_old_data(self):
        """Remove local data older than MAX_LOCAL_DAYS"""
        cutoff_date = (datetime.now() - timedelta(days=Config.MAX_LOCAL_DAYS)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get old screenshot files to delete
        cursor.execute(
            'SELECT filepath FROM screenshots WHERE timestamp < ? AND synced = 1',
            (cutoff_date,)
        )
        old_files = cursor.fetchall()
        
        # Delete old screenshot files
        for (filepath,) in old_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
        
        # Delete old records from database
        cursor.execute('DELETE FROM events WHERE timestamp < ? AND synced = 1', (cutoff_date,))
        cursor.execute('DELETE FROM screenshots WHERE timestamp < ? AND synced = 1', (cutoff_date,))
        
        conn.commit()
        conn.close()
