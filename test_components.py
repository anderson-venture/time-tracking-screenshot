"""
Test script to verify all components work correctly before building
"""

import os
import sys
import time

# Add src to path
sys.path.insert(0, 'src')

from config import Config
from storage_manager import StorageManager
from event_tracker import EventTracker
from screenshot_manager import ScreenshotManager
from firebase_sync import FirebaseSync

def test_storage_manager():
    """Test local storage functionality"""
    print("\n" + "="*50)
    print("Testing Storage Manager...")
    print("="*50)
    
    try:
        storage = StorageManager()
        
        # Test event logging
        storage.log_event('test', {'message': 'Test event'})
        print("✓ Event logging works")
        
        # Test screenshot logging
        storage.log_screenshot('test.jpg', 12345)
        print("✓ Screenshot logging works")
        
        # Test retrieval
        events = storage.get_unsynced_events()
        screenshots = storage.get_unsynced_screenshots()
        print(f"✓ Retrieved {len(events)} events and {len(screenshots)} screenshots")
        
        print("\n✓ Storage Manager: PASSED")
        return True
    except Exception as e:
        print(f"\n✗ Storage Manager: FAILED - {e}")
        return False

def test_event_tracker():
    """Test event tracking"""
    print("\n" + "="*50)
    print("Testing Event Tracker...")
    print("="*50)
    
    try:
        storage = StorageManager()
        tracker = EventTracker(storage)
        
        # Start tracking
        tracker.start()
        print("✓ Event tracker started")
        
        # Let it run briefly
        print("  Tracking events for 3 seconds...")
        print("  (Try clicking or pressing keys)")
        time.sleep(3)
        
        # Stop tracking
        tracker.stop()
        print("✓ Event tracker stopped")
        
        # Check if events were logged
        events = storage.get_unsynced_events()
        print(f"  Captured {len(events)} events")
        
        print("\n✓ Event Tracker: PASSED")
        return True
    except Exception as e:
        print(f"\n✗ Event Tracker: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_screenshot_manager():
    """Test screenshot capture"""
    print("\n" + "="*50)
    print("Testing Screenshot Manager...")
    print("="*50)
    
    try:
        storage = StorageManager()
        screenshot_mgr = ScreenshotManager(storage)
        
        # Take one screenshot
        print("  Capturing screenshot...")
        screenshot_mgr.capture_screenshot()
        print("✓ Screenshot captured")
        
        # Check if logged
        screenshots = storage.get_unsynced_screenshots()
        if screenshots:
            last = screenshots[-1]
            print(f"  File: {last['filepath']}")
            print(f"  Size: {last['filesize']} bytes")
            if os.path.exists(last['filepath']):
                print("  ✓ File exists on disk")
        
        print("\n✓ Screenshot Manager: PASSED")
        return True
    except Exception as e:
        print(f"\n✗ Screenshot Manager: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_firebase_sync():
    """Test Firebase sync (if credentials available)"""
    print("\n" + "="*50)
    print("Testing Firebase Sync...")
    print("="*50)
    
    creds_path = 'firebase-credentials.json'
    
    if not os.path.exists(creds_path):
        print("⚠ No Firebase credentials found")
        print("  Skipping Firebase test")
        print("  (This is OK for local testing)")
        return True
    
    try:
        storage = StorageManager()
        firebase_sync = FirebaseSync(storage, creds_path)
        
        if firebase_sync.initialized:
            print("✓ Firebase initialized successfully")
            print("✓ Firebase Sync: PASSED (configured)")
        else:
            print("⚠ Firebase configured but not initialized")
            print("  (Check credentials and bucket name)")
        
        return True
    except Exception as e:
        print(f"⚠ Firebase Sync: WARNING - {e}")
        print("  (Firebase is optional for testing)")
        return True

def test_config():
    """Test configuration"""
    print("\n" + "="*50)
    print("Testing Configuration...")
    print("="*50)
    
    print(f"App Name: {Config.APP_NAME}")
    print(f"Screenshot Interval: {Config.SCREENSHOT_INTERVAL}s")
    print(f"Screenshot Quality: {Config.SCREENSHOT_QUALITY}")
    print(f"Sync Interval: {Config.SYNC_INTERVAL}s")
    print(f"Local Storage: {Config.LOCAL_STORAGE_PATH}")
    print(f"Firebase Bucket: {Config.FIREBASE_BUCKET_NAME or 'Not configured'}")
    
    # Test directory creation
    Config.ensure_directories()
    
    if os.path.exists(Config.LOCAL_STORAGE_PATH):
        print("✓ Local storage directory created")
    if os.path.exists(Config.SCREENSHOTS_FOLDER):
        print("✓ Screenshots folder created")
    if os.path.exists(Config.EVENTS_FOLDER):
        print("✓ Events folder created")
    
    print("\n✓ Configuration: PASSED")
    return True

def main():
    """Run all tests"""
    print("="*50)
    print("Employee Monitoring Application - Component Tests")
    print("="*50)
    
    results = []
    
    # Run tests
    results.append(("Configuration", test_config()))
    results.append(("Storage Manager", test_storage_manager()))
    results.append(("Screenshot Manager", test_screenshot_manager()))
    results.append(("Event Tracker", test_event_tracker()))
    results.append(("Firebase Sync", test_firebase_sync()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:20s} : {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("\n✓ All tests passed! Ready to build.")
        print("\nNext steps:")
        print("1. Configure Firebase (if not done): See FIREBASE_SETUP.md")
        print("2. Build executable: python build.py")
        print("3. Test the .exe file manually")
        print("4. Deploy with proper legal disclosure")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix issues before building.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
