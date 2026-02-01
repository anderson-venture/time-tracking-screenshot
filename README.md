# Employee Monitoring Application

A Windows desktop application for employee monitoring with proper legal disclosure and consent.

## Features

1. **Event Tracking**: Captures keyboard and mouse events with timestamps
2. **Screenshot Capture**: Takes compressed screenshots every 30 seconds
3. **Local Storage**: Saves data in a hidden system folder
4. **Cloud Sync**: Automatically syncs to Firebase Storage
5. **Background Operation**: Runs silently without user interface
6. **Auto-Start**: Automatically starts with Windows

## Technology Stack

- **Python 3.10+**
- **pynput**: Keyboard and mouse event tracking
- **Pillow (PIL)**: Screenshot capture and compression
- **firebase-admin**: Firebase Storage integration
- **pywin32**: Windows-specific operations
- **PyInstaller**: Packaging to standalone executable

## Project Structure

```
time-tracking-screenshot/
├── src/
│   ├── main.py              # Entry point
│   ├── event_tracker.py     # Keyboard/mouse tracking
│   ├── screenshot_manager.py # Screenshot capture
│   ├── storage_manager.py   # Local file operations
│   ├── firebase_sync.py     # Cloud sync
│   ├── config.py            # Configuration
│   └── auto_start.py        # Windows auto-start
├── requirements.txt         # Python dependencies
├── build.py                 # Build script
└── README.md               # This file
```

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
2. Enable Firebase Storage
3. Create a storage bucket
4. Generate service account credentials:
   - Go to Project Settings → Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file securely
5. Update `src/config.py` with your Firebase bucket name

### 3. Development Testing

```bash
cd src
python main.py
```

### 4. Build Executable

```bash
python build.py
```

This creates:
- `dist/SystemHealthMonitor.exe` - Main executable
- `dist/install.bat` - Installation script
- `dist/uninstall.bat` - Uninstallation script
- `dist/README.txt` - User documentation

## Deployment

1. Run `dist/install.bat` as Administrator
2. Place Firebase credentials in the configured location
3. The application will start automatically with Windows

## Configuration

Edit `src/config.py` to customize:

- Screenshot interval (default: 30 seconds)
- Sync frequency (default: 10 minutes)
- Local storage path
- JPEG compression quality
- Data retention period

## Uninstallation

Run `dist/uninstall.bat` as Administrator to:
- Remove from Windows startup
- Stop the monitoring process
- Delete the executable

**Note**: Local data and cloud data must be manually removed if needed.

## Support & Maintenance

- Check logs in the hidden system folder for debugging
- Monitor Firebase Storage usage to stay within free tier limits
- Regularly review and clean old data
- Keep Python dependencies updated

## Development Notes

### Running in Development

```bash
# Test individual components
cd src
python event_tracker.py
python screenshot_manager.py
python firebase_sync.py
```

### Auto-Start Management

```bash
# Install auto-start
python src/auto_start.py install

# Check if installed
python src/auto_start.py check

# Uninstall
python src/auto_start.py uninstall
```

## Troubleshooting

**Issue**: Screenshots not capturing
- Check if Pillow is properly installed
- Verify screen permissions on Windows

**Issue**: Firebase sync failing
- Verify credentials file path
- Check Firebase Storage rules
- Ensure internet connectivity

**Issue**: Not starting with Windows
- Run installation as Administrator
- Check Windows Registry for the entry
- Verify executable path is correct

**Issue**: High disk usage
- Reduce screenshot interval
- Lower JPEG quality
- Decrease data retention period
