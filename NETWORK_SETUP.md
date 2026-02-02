# Network Setup Guide

This guide explains how to set up the employee monitoring system using a local network architecture.

## Overview

The system consists of two components:
- **Client Application**: Runs on monitored computers, captures data and sends to central server
- **Central Server**: Runs on one computer, receives and stores data from all clients

## Prerequisites

- All computers must be on the same local network
- Python 3.10+ installed on all computers
- Network connectivity between clients and server
- Administrator access for installation

---

## Part 1: Set Up Central Server

The central server receives and stores all monitoring data.

### Step 1: Choose Server Computer

1. Select a computer that will act as the central server
2. This computer should:
   - Remain powered on during work hours
   - Have sufficient disk space (recommend 100+ GB)
   - Have a reliable network connection (wired recommended)

### Step 2: Assign Static IP Address

**For reliability, assign a static IP to the server computer:**

1. Open Network Settings
2. Go to Network Adapter Properties
3. Select IPv4 settings
4. Set a static IP address (e.g., `192.168.1.100`)
5. Note this IP address - you'll need it for client configuration

**Alternative:** Configure your router to assign a fixed IP to this computer via DHCP reservation

### Step 3: Install Server Dependencies

```bash
cd E:\time-tracking-screenshot\server
pip install -r requirements.txt
```

### Step 4: Configure Server

Edit `server/config.py`:

```python
# Server settings
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000

# Authentication - CHANGE THIS!
API_TOKEN = 'your-secret-token-here'  # Use a strong random string

# Storage location
STORAGE_ROOT = r'E:\MonitoringData'  # Change to your preferred location

# Optional: IP whitelist (leave empty to allow all local network)
ALLOWED_IPS = []  # Example: ['192.168.1.0/24']
```

### Step 5: Configure Firewall

Allow incoming connections on port 5000:

```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Monitoring Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

Or manually:
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Select "Inbound Rules"
4. Click "New Rule"
5. Select "Port"  Next
6. Enter port 5000  Next
7. Allow the connection  Next
8. Apply to all profiles  Next
9. Name it "Monitoring Server"  Finish

### Step 6: Start the Server

```bash
cd E:\time-tracking-screenshot\server
python main.py
```

You should see:
```
============================================================
  Monitoring Server Starting
============================================================
Host: 0.0.0.0
Port: 5000
Storage: E:\MonitoringData
Time: 2026-02-02 10:30:00
============================================================

Endpoints:
  - POST http://<server-ip>:5000/upload
  - GET  http://<server-ip>:5000/health
  - GET  http://<server-ip>:5000/stats
  - GET  http://<server-ip>:5000/

Press Ctrl+C to stop the server
============================================================
```

### Step 7: Test Server

From another computer on the network:

```bash
# Test health endpoint
curl http://192.168.1.100:5000/health
```

Should return:
```json
{
  "status": "ok",
  "service": "monitoring-server",
  "version": "1.0"
}
```

### Step 8: Set Server to Auto-Start (Optional)

**Method 1: Windows Task Scheduler**

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Monitoring Server"
4. Trigger: At log on
5. Action: Start a program
6. Program: `pythonw.exe`
7. Arguments: `E:\time-tracking-screenshot\server\main.py`
8. Start in: `E:\time-tracking-screenshot\server`

**Method 2: Startup Folder**

Create a batch file `start_server.bat`:
```batch
@echo off
cd /d E:\time-tracking-screenshot\server
pythonw.exe main.py
```

Place this in:
`C:\Users\<Username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`

---

## Part 2: Deploy Client Application

Deploy the client to each computer you want to monitor.

### Step 1: Configure Client

Edit `client/config.py`:

```python
# Network sync settings
SERVER_ADDRESS = '192.168.1.100'  # IP of your central server
SERVER_PORT = 5000
API_TOKEN = 'your-secret-token-here'  # MUST match server token

# Screenshot settings
SCREENSHOT_INTERVAL = 30  # seconds
SCREENSHOT_QUALITY = 65

# Sync frequency
SYNC_INTERVAL = 600  # seconds (10 minutes)
```

**IMPORTANT**: The `API_TOKEN` must match exactly with the server configuration!

### Step 2: Build Client Executable

```bash
cd E:\time-tracking-screenshot\client
pip install -r requirements.txt
python ..\build.py
```

This creates `dist\SystemHealthMonitor.exe`

### Step 3: Test Client (Before Deployment)

1. Copy the .exe to the target computer
2. Run it manually first to test
3. Check server logs to verify connection
4. Verify data appears in server storage folder

### Step 4: Deploy to Target Computers

**Option A: Manual Installation**

1. Copy `SystemHealthMonitor.exe` to target computer
2. Place in: `C:\Program Files\SystemHealthMonitor\`
3. Run the auto-start installer (see below)

**Option B: Group Policy Deployment**

Use GPO to deploy the executable across domain computers

### Step 5: Set Up Auto-Start

The client includes auto-start functionality. To enable:

```python
# On target computer, run Python script:
from client.auto_start import AutoStartManager

manager = AutoStartManager()
manager.install()  # Adds to registry and startup folder
```

Or manually add to registry:
```
Key: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
Value Name: SystemHealthMonitor
Value Data: C:\Program Files\SystemHealthMonitor\SystemHealthMonitor.exe
```

---

## Part 3: Verify System Operation

### Check Server Dashboard

1. Open browser
2. Navigate to: `http://192.168.1.100:5000/`
3. Add header: `X-API-Token: your-secret-token-here`
4. View statistics and connected computers

**Using curl with authentication:**
```bash
curl -H "X-API-Token: your-secret-token-here" http://192.168.1.100:5000/stats
```

### Check Server Storage

Data is organized as:
```
MonitoringData/
 COMPUTER-1/
    2026-02-02/
       events_20260202_100000.json
       screenshots/
           screenshot_20260202_100030.jpg
           screenshot_20260202_100100.jpg
    2026-02-03/
        ...
 COMPUTER-2/
    ...
 COMPUTER-3/
     ...
```

### Troubleshooting

**Client can't connect to server:**
- Verify server IP address is correct
- Check firewall on server computer
- Ping server from client: `ping 192.168.1.100`
- Verify server is running
- Check API tokens match

**Authentication errors (401):**
- Verify API_TOKEN matches between client and server
- Check for extra spaces or special characters

**No data appearing:**
- Check client is running
- Verify sync interval (default 10 minutes)
- Check server logs for errors
- Verify network connectivity

**Server storage location:**
- Default: `~\MonitoringData`
- Change in `server/config.py`

---

## Security Considerations

1. **Change the default API token** to a strong random string
2. **Use IP whitelist** if possible to restrict access
3. **Enable HTTPS** for sensitive environments (requires SSL certificates)
4. **Restrict physical access** to server computer
5. **Regular backups** of stored data
6. **

---

## Maintenance

### Daily Monitoring

- Check server is running
- Verify disk space available
- Review any error logs

### Weekly Tasks

- Check data collection from all clients
- Verify backup status

### Cleanup

Old data is automatically cleaned up after 30 days (configurable in `server/config.py`).

Manual cleanup:
```bash
curl -X POST -H "X-API-Token: your-secret-token-here" http://192.168.1.100:5000/cleanup
```

---

## Support

For issues or questions, refer to:
- Main README.md
- Plan file: employee_monitoring_application_517eee20.plan.md
