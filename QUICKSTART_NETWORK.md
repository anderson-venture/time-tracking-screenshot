# Quick Start Guide - Network Setup

Get your employee monitoring system up and running in 15 minutes!

## Prerequisites

- Python 3.10+ installed on all computers
- All computers on same local network
- Administrator access

---

## Part 1: Server Setup (5 minutes)

### 1. Install Dependencies

```bash
cd E:\time-tracking-screenshot\server
pip install -r requirements.txt
```

### 2. Configure Server

Copy the example config:
```bash
copy config.example.py config.py
```

Edit `config.py`:
```python
API_TOKEN = 'MySecureToken123!'  # Change this!
STORAGE_ROOT = r'E:\MonitoringData'
```

### 3. Configure Firewall

Run as Administrator:
```powershell
New-NetFirewallRule -DisplayName "Monitoring Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

### 4. Start Server

```bash
python main.py
```

You should see:
```
============================================================
  Monitoring Server Starting
============================================================
Host: 0.0.0.0
Port: 5000
...
```

### 5. Test Server

From another computer:
```bash
curl http://<SERVER-IP>:5000/health
```

 **Server is ready!** Note the server IP address for client setup.

---

## Part 2: Client Setup (10 minutes)

### 1. Install Dependencies

```bash
cd E:\time-tracking-screenshot\client
pip install -r requirements.txt
```

### 2. Configure Client

Copy the example config:
```bash
copy config.example.py config.py
```

Edit `config.py`:
```python
SERVER_ADDRESS = '192.168.1.100'  # Your server IP
SERVER_PORT = 5000
API_TOKEN = 'MySecureToken123!'   # MUST match server!
```

### 3. Test Client (Optional)

```bash
python main.py
```

Let it run for a minute, then check server storage folder for data.

Press Ctrl+C to stop.

### 4. Build Executable

```bash
cd E:\time-tracking-screenshot
python build.py
```

This creates: `dist\SystemHealthMonitor.exe`

### 5. Deploy to Target Computers

**Option A: Manual**
1. Copy `SystemHealthMonitor.exe` to target computer
2. Run `dist\install.bat` as Administrator

**Option B: Network Share**
1. Place .exe on network share
2. Create startup shortcut on each computer

---

## Verification

### Check Server Dashboard

Browser: `http://<SERVER-IP>:5000/`  
Header: `X-API-Token: MySecureToken123!`

Or with curl:
```bash
curl -H "X-API-Token: MySecureToken123!" http://192.168.1.100:5000/stats
```

### Check Data Collection

Navigate to server storage folder:
```
E:\MonitoringData\
 <COMPUTER-NAME>\
     <DATE>\
         events_*.json
         screenshots\
             screenshot_*.jpg
```

---

## Common Issues

**Can't connect to server?**
- Verify server IP: `ipconfig` on server computer
- Test connectivity: `ping <SERVER-IP>`
- Check firewall is open

**Authentication failed?**
- Verify API_TOKEN matches exactly in both configs
- Check for spaces or quotes

**No data appearing?**
- Wait 10 minutes (default sync interval)
- Check client is running
- Review server console for errors

---

## Next Steps

1.  Test with 1-2 computers first
2.  Verify data collection for 1 hour
3.  Review server storage and disk space
4.  Deploy to all target computers
5.  Set up server auto-start (see NETWORK_SETUP.md)
6.  Schedule regular backups

---

## Need More Details?

See **[NETWORK_SETUP.md](NETWORK_SETUP.md)** for comprehensive setup guide.

