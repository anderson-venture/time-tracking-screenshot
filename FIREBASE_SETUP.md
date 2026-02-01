# Firebase Storage Setup Guide

This guide walks you through setting up Firebase Storage for the employee monitoring application.

## Why Firebase?

- **Free Tier**: 5GB storage, 1GB/day download, 20K uploads/day
- **Easy Integration**: Simple Python SDK
- **Reliable**: Google Cloud infrastructure
- **Scalable**: Can upgrade if needed

## Step-by-Step Setup

### 1. Create Firebase Account

1. Go to https://console.firebase.google.com
2. Sign in with Google account
3. Accept terms of service

### 2. Create New Project

1. Click "Add project" or "Create a project"
2. Enter project name: `employee-monitoring-prod` (or your choice)
3. Click "Continue"
4. **Google Analytics**: Disable (not needed for this application)
5. Click "Create project"
6. Wait for project creation (30-60 seconds)
7. Click "Continue"

### 3. Enable Firebase Storage

1. In left sidebar, click "Build" → "Storage"
2. Click "Get Started"
3. **Security Rules**: Select "Start in production mode"
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
4. Click "Next"
5. **Cloud Storage location**: Choose closest to your region
   - `us-central1` (Iowa) - North America
   - `europe-west` (Belgium) - Europe
   - `asia-northeast1` (Tokyo) - Asia
6. Click "Done"

### 4. Configure Storage Rules

For this application (service-to-service, no user auth), update rules:

1. Go to Storage → Rules tab
2. Replace with:
   ```
   rules_version = '2';
   service firebase.storage {
     match /b/{bucket}/o {
       match /{allPaths=**} {
         allow read, write: if true;  // WARNING: Open for testing only!
       }
     }
   }
   ```
3. Click "Publish"

**⚠️ IMPORTANT**: These rules allow anyone to read/write. For production:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Only allow uploads from authenticated service accounts
    match /events/{document=**} {
      allow write: if request.auth != null;
      allow read: if request.auth != null;
    }
    match /screenshots/{document=**} {
      allow write: if request.auth != null;
      allow read: if request.auth != null;
    }
  }
}
```

### 5. Get Service Account Credentials

1. Click the **gear icon** (⚙️) → "Project settings"
2. Go to "Service accounts" tab
3. You'll see: "Firebase Admin SDK"
4. Select **Python** from the dropdown
5. Click "Generate new private key"
6. Confirm "Generate key"
7. A JSON file will download: `your-project-name-firebase-adminsdk-xxxxx.json`
8. **Rename it** to `firebase-credentials.json`
9. **⚠️ KEEP THIS FILE SECRET** - It has full access to your project!

### 6. Get Your Bucket Name

Your bucket name is shown in the Storage section:
- Format: `your-project-id.appspot.com`
- Example: `employee-monitoring-prod.appspot.com`

Copy this - you'll need it for configuration.

### 7. Update Application Configuration

Edit `src/config.py`:

```python
# Firebase settings
FIREBASE_BUCKET_NAME = "your-project-id.appspot.com"  # Replace with your bucket
```

### 8. Test Connection

Create a test script `test_firebase.py`:

```python
import firebase_admin
from firebase_admin import credentials, storage
import os

# Initialize Firebase
cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your-project-id.appspot.com'  # Replace
})

# Get bucket
bucket = storage.bucket()

# Test upload
test_file = 'test.txt'
with open(test_file, 'w') as f:
    f.write('Firebase connection test')

# Upload
blob = bucket.blob('test/test.txt')
blob.upload_from_filename(test_file)

print("✓ Upload successful!")

# Test download
blob.download_to_filename('test_downloaded.txt')
print("✓ Download successful!")

# Clean up
os.remove(test_file)
os.remove('test_downloaded.txt')
blob.delete()

print("✓ All tests passed!")
```

Run it:
```bash
python test_firebase.py
```

### 9. Security: Encrypt Credentials

Don't deploy the raw JSON file! Encrypt it:

```python
from cryptography.fernet import Fernet
import os

# Generate encryption key
key = Fernet.generate_key()
print(f"Encryption key (SAVE THIS SECURELY): {key.decode()}")

# Encrypt credentials
cipher = Fernet(key)
with open('firebase-credentials.json', 'rb') as f:
    credentials = f.read()

encrypted = cipher.encrypt(credentials)

# Save encrypted version
with open('firebase-credentials.enc', 'wb') as f:
    f.write(encrypted)

print("✓ Credentials encrypted and saved as firebase-credentials.enc")
```

To decrypt (in your application):

```python
from cryptography.fernet import Fernet
import json

# Get key from secure location (environment variable, key vault, etc.)
key = os.getenv('FIREBASE_KEY').encode()
cipher = Fernet(key)

# Decrypt
with open('firebase-credentials.enc', 'rb') as f:
    encrypted = f.read()

decrypted = cipher.decrypt(encrypted)
credentials = json.loads(decrypted)
```

### 10. Monitoring Usage

#### Check Storage Usage

1. Firebase Console → Storage
2. See "Usage" at top
3. Monitor:
   - **Storage**: Max 5GB free
   - **Downloads**: Max 1GB/day free
   - **Uploads**: Max 20K/day free

#### Set Up Alerts

1. Firebase Console → Project Settings
2. Go to "Usage and billing"
3. Click "Set budget alerts"
4. Set alert at 80% of free tier limits

## Data Organization

The application organizes data as:

```
storage-bucket/
├── events/
│   ├── events_20260201_120000.json
│   ├── events_20260201_121000.json
│   └── ...
└── screenshots/
    ├── screenshot_20260201_120000.jpg
    ├── screenshot_20260201_120030.jpg
    └── ...
```

## Best Practices

### 1. Separate Projects for Dev/Prod

- Development: `employee-monitoring-dev`
- Production: `employee-monitoring-prod`

### 2. Implement Lifecycle Policies

Set up automatic deletion of old files:

1. Google Cloud Console → Cloud Storage
2. Select your bucket
3. "Lifecycle" tab
4. Add rule: "Delete objects older than X days"

### 3. Monitor Costs

- Free tier is generous for this use case
- ~500 screenshots/day × 50KB = ~25MB/day
- Well within free limits for small teams

### 4. Backup Strategy

- Firebase Storage is already redundant
- For critical data, export to another location
- Use Firebase's export feature

## Troubleshooting

### "Permission denied" errors

**Solution**: Update storage rules or check service account permissions

### Upload fails

**Possible causes**:
- No internet connection
- Invalid credentials
- Storage rules blocking upload
- Bucket name incorrect

### Quota exceeded

**Solution**:
- Reduce screenshot frequency
- Increase compression
- Upgrade to paid plan (Blaze)

## Alternative: Google Drive API

If you prefer Google Drive (15GB free):

1. Enable Google Drive API
2. Use `google-api-python-client`
3. Authenticate with service account
4. Upload to specific folder

Code example available in `firebase_sync.py` (can be adapted).

## Upgrading to Paid Plan

If you exceed free tier:

1. Firebase Console → Upgrade
2. Select "Blaze" plan (pay-as-you-go)
3. Pricing:
   - Storage: $0.026/GB/month
   - Downloads: $0.12/GB
   - Operations: $0.05/10K operations

For 100 employees with 500 screenshots/day:
- Storage: ~5GB/month = ~$0.13
- Uploads: ~1.5M/month = ~$7.50
- **Total**: ~$8/month

## Security Checklist

Before production deployment:

- [ ] Credentials encrypted
- [ ] Storage rules configured for auth
- [ ] Service account has minimal required permissions
- [ ] Credentials not in version control (.gitignore)
- [ ] Encryption key stored securely
- [ ] Regular security audits scheduled
- [ ] Access logs monitored

## Additional Resources

- [Firebase Storage Documentation](https://firebase.google.com/docs/storage)
- [Security Rules Guide](https://firebase.google.com/docs/storage/security)
- [Python Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Pricing Calculator](https://firebase.google.com/pricing)
