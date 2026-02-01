# Setup Guide - Employee Monitoring Application

## Prerequisites

- Windows 10 or later
- Python 3.10 or higher
- Administrator privileges for installation
- Firebase account (free tier is sufficient)

## Step-by-Step Setup

### Step 1: Install Python Dependencies

Open PowerShell or Command Prompt in the project directory:

```bash
pip install -r requirements.txt
```

### Step 2: Firebase Configuration

#### 2.1 Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Add project"
3. Enter project name (e.g., "employee-monitoring")
4. Disable Google Analytics (optional)
5. Click "Create project"

#### 2.2 Enable Firebase Storage

1. In your Firebase project, go to "Storage" in the left menu
2. Click "Get Started"
3. Choose "Start in production mode"
4. Select a Cloud Storage location (choose closest to your region)
5. Click "Done"

#### 2.3 Configure Storage Rules (Optional for Testing)

For testing purposes, you can set temporary open rules:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

**WARNING**: For production, implement proper authentication and security rules!

#### 2.4 Get Service Account Credentials

1. Go to Project Settings (gear icon) → Service Accounts
2. Click "Generate New Private Key"
3. Save the JSON file as `firebase-credentials.json`
4. **Keep this file secure!**

#### 2.5 Update Configuration

Edit `src/config.py` and update:

```python
FIREBASE_BUCKET_NAME = "your-project-id.appspot.com"
```

Replace `your-project-id` with your actual Firebase project ID.

### Step 3: Test in Development Mode

Before building, test the application:

```bash
cd src
python main.py
```

**Test checklist**:
- [ ] No errors on startup
- [ ] Screenshots are being saved to local folder
- [ ] Events are being logged (check database)
- [ ] Check `%APPDATA%\Microsoft\Windows\SystemData\` folder

To stop the test: Press `Ctrl+C`

### Step 4: Build Executable

```bash
python build.py
```

This will create:
- `dist/SystemHealthMonitor.exe`
- `dist/install.bat`
- `dist/uninstall.bat`
- `dist/README.txt`

### Step 5: Prepare for Deployment

#### 5.1 Encrypt Firebase Credentials

For security, you should encrypt the Firebase credentials before deployment:

```python
from cryptography.fernet import Fernet

# Generate a key
key = Fernet.generate_key()
cipher = Fernet(key)

# Read credentials
with open('firebase-credentials.json', 'rb') as f:
    credentials = f.read()

# Encrypt
encrypted = cipher.encrypt(credentials)

# Save encrypted credentials
with open('firebase-credentials.enc', 'wb') as f:
    f.write(encrypted)

# Store the key securely (DO NOT put in code!)
print(f"Encryption key: {key.decode()}")
```

**IMPORTANT**: Store the encryption key securely (e.g., environment variable, secure key management system)

#### 5.2 Copy Files to Deployment Package

Create a deployment folder with:
- `SystemHealthMonitor.exe`
- `install.bat`
- `uninstall.bat`
- `README.txt`
- `firebase-credentials.enc` (encrypted)

### Step 6: Installation on Target Machine

#### 6.1 Legal Compliance First! ⚠️

**BEFORE INSTALLATION**:
1. Obtain written consent from employees
2. Provide clear disclosure about monitoring
3. Comply with local labor laws
4. Document the legal basis for monitoring

#### 6.2 Install the Application

1. Copy deployment folder to target machine
2. Right-click `install.bat` → "Run as administrator"
3. Wait for installation to complete

#### 6.3 Verify Installation

Check:
- [ ] Process running: Open Task Manager, look for `SystemHealthMonitor.exe`
- [ ] Auto-start entry: Run `regedit`, navigate to `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- [ ] Data folder created: `%APPDATA%\Microsoft\Windows\SystemData\`

### Step 7: Monitor and Maintain

#### 7.1 Check Firebase Storage

1. Go to Firebase Console → Storage
2. Verify files are being uploaded
3. Monitor storage usage (5GB free tier)

#### 7.2 Local Data Management

The application automatically:
- Cleans up data older than 7 days (configurable)
- Syncs to Firebase every 10 minutes
- Compresses screenshots to save space

#### 7.3 Viewing Collected Data

**Events**: Query the SQLite database at:
```
%APPDATA%\Microsoft\Windows\SystemData\data.db
```

**Screenshots**: Check Firebase Storage or local folder:
```
%APPDATA%\Microsoft\Windows\SystemData\screenshots\
```

## Troubleshooting

### Application Not Starting

1. Check Windows Event Viewer for errors
2. Try running manually: `SystemHealthMonitor.exe`
3. Verify Python dependencies are embedded in .exe

### No Data Being Collected

1. Check if process is running in Task Manager
2. Verify local storage folder exists
3. Check database file for entries

### Firebase Sync Not Working

1. Verify internet connectivity
2. Check Firebase credentials are valid
3. Verify storage bucket name in config
4. Check Firebase Storage rules

### High CPU or Memory Usage

- Reduce screenshot frequency in config
- Lower screenshot quality
- Check for memory leaks in Task Manager

## Uninstallation

1. Run `uninstall.bat` as Administrator
2. Manually delete data if needed:
   - Local: `%APPDATA%\Microsoft\Windows\SystemData\`
   - Cloud: Firebase Console → Storage

## Advanced Configuration

### Change Screenshot Interval

Edit `config.py`:
```python
SCREENSHOT_INTERVAL = 60  # Change to 60 seconds
```

Rebuild the executable after changes.

### Change Storage Location

Edit `config.py`:
```python
LOCAL_STORAGE_PATH = "C:\\CustomPath\\MonitorData"
```

### Customize Application Name

Edit `config.py`:
```python
APP_NAME = "CustomServiceName"
```

## Security Best Practices

1. **Encrypt credentials**: Never store Firebase credentials in plain text
2. **Limit access**: Restrict who can access collected data
3. **Secure transmission**: Firebase uses HTTPS by default
4. **Regular audits**: Review collected data periodically
5. **Update regularly**: Keep dependencies updated for security patches

## Compliance Checklist

Before deploying to production:

- [ ] Legal counsel reviewed monitoring policy
- [ ] Employees signed consent forms
- [ ] Privacy policy updated
- [ ] Data retention policy defined
- [ ] Access controls implemented
- [ ] Incident response plan created
- [ ] Regular compliance audits scheduled

## Support

For technical issues:
1. Check application logs
2. Review Windows Event Viewer
3. Test Firebase connection manually
4. Verify all dependencies are installed

For legal questions:
- Consult with legal counsel
- Review local labor laws
- Check data protection regulations
