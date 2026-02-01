# Quick Start Guide

Get the employee monitoring application running in 5 steps.

## Prerequisites

- Windows 10 or later
- Python 3.10+
- Administrator access
- Firebase account (free)

## Step 1: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

## Step 2: Test Locally (5 minutes)

```bash
python test_components.py
```

This will verify:
- ✓ Configuration is correct
- ✓ Storage works
- ✓ Screenshots capture properly
- ✓ Event tracking functions
- ✓ Firebase connection (if configured)

## Step 3: Configure Firebase (10 minutes)

### 3.1 Create Project
1. Go to https://console.firebase.google.com
2. Create new project
3. Enable Firebase Storage

### 3.2 Get Credentials
1. Project Settings → Service Accounts
2. Generate new private key
3. Save as `firebase-credentials.json`

### 3.3 Update Config
Edit `src/config.py`:
```python
FIREBASE_BUCKET_NAME = "your-project-id.appspot.com"
```

**Detailed guide**: See [FIREBASE_SETUP.md](FIREBASE_SETUP.md)

## Step 4: Build Executable (3 minutes)

```bash
python build.py
```

Output:
- `dist/SystemHealthMonitor.exe`
- `dist/install.bat`
- `dist/uninstall.bat`

## Step 5: Deploy (2 minutes)

### ⚠️ LEGAL COMPLIANCE FIRST!

**BEFORE installing on any machine**:
1. ✅ Obtain employee consent
2. ✅ Provide written disclosure
3. ✅ Review [LEGAL_NOTICE.md](LEGAL_NOTICE.md)
4. ✅ Consult legal counsel

### Install

1. Copy `dist/` folder to target machine
2. Run `install.bat` as Administrator
3. Verify it's running (Task Manager → SystemHealthMonitor.exe)

## Verification

### Check if Running
```bash
# PowerShell
Get-Process SystemHealthMonitor

# Command Prompt
tasklist | findstr SystemHealthMonitor
```

### Check Data Collection
1. Navigate to: `%APPDATA%\Microsoft\Windows\SystemData\`
2. Verify folders exist:
   - `screenshots/`
   - `events/`
   - `data.db`

### Check Firebase Sync
1. Firebase Console → Storage
2. Look for:
   - `events/` folder
   - `screenshots/` folder

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Screenshots not working
- Check if Pillow installed: `pip show Pillow`
- Run as Administrator

### Firebase not syncing
- Verify credentials file exists
- Check bucket name in config.py
- Test internet connection

### Not starting with Windows
- Re-run `install.bat` as Administrator
- Check registry: `regedit` → `HKEY_CURRENT_USER\...\Run`

## Next Steps

1. **Monitor Usage**: Check Firebase storage usage regularly
2. **Test Thoroughly**: Run on test machine first
3. **Document Everything**: Keep records of consent, policies
4. **Regular Audits**: Review collected data periodically
5. **Update Policy**: Keep monitoring policy current

## Support

### Documentation
- [README.md](README.md) - Full documentation
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup
- [FIREBASE_SETUP.md](FIREBASE_SETUP.md) - Firebase configuration
- [LEGAL_NOTICE.md](LEGAL_NOTICE.md) - Legal requirements

### Testing
```bash
# Test all components
python test_components.py

# Test manually
cd src
python main.py
# Press Ctrl+C to stop

# Check auto-start
python src/auto_start.py check
```

### Common Commands

```bash
# Build
python build.py

# Test Firebase
python -c "from firebase_admin import credentials; print('Firebase SDK installed')"

# Check config
python -c "from src.config import Config; print(f'Storage: {Config.LOCAL_STORAGE_PATH}')"
```

## Uninstallation

```bash
# On target machine
cd dist
uninstall.bat  # Run as Administrator
```

## Configuration

### Change Screenshot Interval

Edit `src/config.py`:
```python
SCREENSHOT_INTERVAL = 60  # Change to 60 seconds
```

Then rebuild: `python build.py`

### Change Storage Location

Edit `src/config.py`:
```python
LOCAL_STORAGE_PATH = "C:\\YourPath\\MonitorData"
```

### Adjust Compression

Edit `src/config.py`:
```python
SCREENSHOT_QUALITY = 50  # Lower = smaller files, lower quality
```

## Production Checklist

Before production deployment:

- [ ] Legal approval obtained
- [ ] Employee consent collected
- [ ] Monitoring policy distributed
- [ ] Data protection measures implemented
- [ ] Firebase security rules configured
- [ ] Tested on multiple machines
- [ ] Backup/recovery plan created
- [ ] Incident response plan ready
- [ ] Access controls configured
- [ ] Audit logging enabled

## Important Reminders

1. 🔴 **Legal Compliance is MANDATORY**
2. 🔴 **Transparency with Employees**
3. 🔴 **Secure Firebase Credentials**
4. 🔴 **Regular Security Audits**
5. 🔴 **Data Retention Limits**

---

**Need Help?**

1. Check documentation files
2. Run `python test_components.py`
3. Review error messages carefully
4. Verify all prerequisites installed
5. Test Firebase connection separately

**Ready to Deploy?**

✅ Legal compliance verified
✅ Tested thoroughly
✅ Firebase configured
✅ Documentation ready
✅ Monitoring policy in place

→ Run `install.bat` and start monitoring!
