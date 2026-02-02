# Employee Monitoring Application

A Windows desktop application for employee monitoring Uses a local network architecture for data collection.

## Features

1. **Event Tracking**: Captures keyboard and mouse events with timestamps
2. **Screenshot Capture**: Takes compressed screenshots every 30 seconds
3. **Local Storage**: Saves data in a hidden system folder
4. **Network Sync**: Automatically syncs to central server on local network
5. **Background Operation**: Runs silently without user interface
6. **Auto-Start**: Automatically starts with Windows
7. **Central Server**: Web-based dashboard for viewing collected data

## Architecture

- **Client Application**: Runs on monitored computers, captures and sends data
- **Central Server**: Receives and organizes data from all clients
- **Local Network**: All communication stays within your network (no cloud/internet required)

## Technology Stack

### Client
- **Python 3.10+**
- **pynput**: Keyboard and mouse event tracking
- **Pillow (PIL)**: Screenshot capture and compression
- **requests**: HTTP client for network sync
- **pywin32**: Windows-specific operations
- **PyInstaller**: Packaging to standalone executable

### Server
- **Python 3.10+**
- **Flask**: HTTP server for receiving uploads
- **schedule**: Automated cleanup tasks

## Project Structure

```
time-tracking-screenshot/
 client/                   # Client application
    main.py              # Entry point
    event_tracker.py     # Keyboard/mouse tracking
    screenshot_manager.py # Screenshot capture
    storage_manager.py   # Local file operations
    network_sync.py      # Network sync to server
    config.py            # Configuration
    auto_start.py        # Windows auto-start
    requirements.txt     # Client dependencies
    build.py             # Build script
 server/                   # Central server
    main.py              # Server entry point
    file_receiver.py     # File upload handler
    storage_handler.py   # File organization
    config.py            # Server configuration
    requirements.txt     # Server dependencies
 requirements.txt         # All dependencies
 NETWORK_SETUP.md         # Detailed setup guide
 README.md               # This file
```

## Quick Start

### For Detailed Setup Instructions

See [NETWORK_SETUP.md](NETWORK_SETUP.md)** for complete step-by-step guide

### Summary

1. **Set up Central Server** (one computer on your network)
   ```bash
   cd server
   pip install -r requirements.txt
   # Edit config.py (set API token, storage path)
   python main.py
   ```

2. **Configure Firewall** on server computer to allow port 5000

3. **Deploy Client** to monitored computers
   ```bash
   cd client
   pip install -r requirements.txt
   # Edit config.py (set server IP, API token)
   python build.py  # Creates executable
   ```

4. **Install client executable** on each monitored computer

## Installation & Setup

### Server Setup

1. **Choose a server computer** on your local network
2. **Assign static IP** (e.g., 192.168.1.100)
3. **Install dependencies**:
   ```bash
   cd server
   pip install -r requirements.txt
   ```
4. **Configure** `server/config.py`:
   - Set API_TOKEN (strong random string)
   - Set STORAGE_ROOT path
   - Configure PORT (default: 5000)
5. **Open firewall** for port 5000
6. **Start server**: `python main.py`

### Client Setup

1. **Install dependencies**:
   ```bash
   cd client
   pip install -r requirements.txt
   ```
2. **Configure** `client/config.py`:
   - Set SERVER_ADDRESS (server IP)
   - Set API_TOKEN (must match server)
   - Adjust intervals if needed
3. **Build executable**: `python build.py`
4. **Deploy** `dist/SystemHealthMonitor.exe` to monitored computers
5. **Enable auto-start** (see documentation)

## Configuration

### Client Configuration (`client/config.py`)

```python
SERVER_ADDRESS = '192.168.1.100'  # Server IP
SERVER_PORT = 5000
API_TOKEN = 'your-secret-token'   # Must match server
SCREENSHOT_INTERVAL = 30          # seconds
SYNC_INTERVAL = 600               # seconds (10 min)
SCREENSHOT_QUALITY = 65           # JPEG quality
MAX_LOCAL_DAYS = 7                # Local retention
```

### Server Configuration (`server/config.py`)

```python
HOST = '0.0.0.0'                  # Listen on all interfaces
PORT = 5000
API_TOKEN = 'your-secret-token'   # Must match clients
STORAGE_ROOT = r'E:\MonitoringData'
RETENTION_DAYS = 30               # Server retention
ALLOWED_IPS = []                  # Optional whitelist
```

## Accessing the Dashboard

Open browser and navigate to: `http://<server-ip>:5000/`

Add header: `X-API-Token: your-secret-token`

Or use curl:
```bash
curl -H "X-API-Token: your-secret-token" http://192.168.1.100:5000/stats
```

## Data Organization

Server stores data organized by computer and date:

```
MonitoringData/
 COMPUTER-1/
    2026-02-02/
       events_20260202_100000.json
       screenshots/
           screenshot_*.jpg
    2026-02-03/
 COMPUTER-2/
     ...
```

## Support & Maintenance

### Daily Tasks
- Verify server is running
- Check disk space
- Monitor network connectivity

### Automatic Cleanup
- Old data cleaned up after 30 days (configurable)
- Manual cleanup: `curl -X POST -H "X-API-Token: token" http://server:5000/cleanup`

### Backups
- Regularly backup `MonitoringData` folder
- Keep configuration files secure

## Development Notes

### Testing Server

```bash
cd server
python main.py
# Server starts on http://localhost:5000
```

Test endpoints:
```bash
# Health check
curl http://localhost:5000/health

# Stats (with auth)
curl -H "X-API-Token: your-token" http://localhost:5000/stats
```

### Testing Client

```bash
cd client
python main.py
# Client runs and syncs to server
```

### Auto-Start Management

```python
from client.auto_start import AutoStartManager

manager = AutoStartManager()
manager.install()   # Add to startup
manager.check()     # Verify installation
manager.uninstall() # Remove from startup
```

## Troubleshooting

**Issue**: Client can't connect to server
- Verify server IP address in `client/config.py`
- Check firewall on server computer
- Ping server: `ping 192.168.1.100`
- Ensure server is running
- Verify both computers are on same network

**Issue**: Authentication errors (401)
- Check API_TOKEN matches in both configs
- Ensure no extra spaces in token string
- Case-sensitive comparison

**Issue**: No data appearing on server
- Check client is running
- Wait for sync interval (default 10 minutes)
- Check server logs for connection attempts
- Verify network connectivity

**Issue**: Screenshots not capturing
- Check if Pillow is properly installed
- Verify screen permissions on Windows
- Check disk space

**Issue**: Not starting with Windows
- Run installation as Administrator
- Check Windows Registry for the entry
- Verify executable path is correct

**Issue**: High disk usage
- Reduce screenshot interval
- Lower JPEG quality
- Decrease data retention period
- Check server cleanup is running

**Issue**: Server won't start
- Check port 5000 is not already in use
- Verify firewall allows the port
- Check Python version (3.10+ required)
- Review error messages in console

