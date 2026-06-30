# Firebase Cloud Messaging (FCM) Setup Guide for OTP Delivery

## Overview
Firebase Cloud Messaging is a **free** alternative to SMS/WhatsApp for sending OTP and notifications. No phone number purchase required!

## Architecture

```
User Registration Flow:
┌──────────────────┐
│   User Registers │
│ (username, phone) │
└────────┬─────────┘
         │
    ┌────▼────────────────┐
    │ Firebase Backend:    │
    │ - Generate OTP       │
    │ - Store in Database  │
    │ - Get Device Token   │
    │ - Send to FCM        │
    └────┬───────────────┘
         │
    ┌────▼──────────────────────┐
    │  User's Device (Web/App)  │
    │  - FCM SDK Receives       │
    │  - Displays Notification  │
    │  - User sees OTP          │
    └───────────────────────────┘
```

## Step-by-Step Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Create a project"**
3. Enter project name (e.g., "Job-Detection-AI")
4. Accept the terms and click **"Create project"**
5. Wait for project creation (~1-2 minutes)

### 2. Get Service Account Key

1. In Firebase Console, click **⚙️ Settings** (gear icon) → **Project Settings**
2. Go to **Service Accounts** tab
3. Click **"Generate New Private Key"** (or "Generate Key")
4. A JSON file will download (e.g., `firebase-credentials.json`)
5. **Important:** Keep this file secret! Add to `.gitignore`:
   ```
   firebase-credentials.json
   ```

### 3. Place Credentials File

1. Move the downloaded JSON file to your project root:
   ```
   d:\Ai-job-dectection-\firebase-credentials.json
   ```

2. Update `.env`:
   ```
   FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
   ```

### 4. Enable Cloud Messaging API (Optional but Recommended)

1. In Firebase Console, go to **APIs**
2. Search for "Cloud Messaging"
3. Click and enable it
4. This ensures higher quota limits

### 5. Test Firebase Connection

```bash
cd d:\Ai-job-dectection-

# Test Firebase import
AItest\Scripts\python.exe -c "
import firebase_admin
from firebase_admin import credentials
creds = credentials.Certificate('firebase-credentials.json')
print('✓ Firebase credentials loaded successfully')
"
```

## Client-Side Setup (For Users' Devices)

For users to **receive** OTP via Firebase, they need to:

### Option A: Web App (Recommended for now)

The web app will have a simple script to register device tokens:

```html
<!-- In your base template, add: -->
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging.js"></script>

<script>
// Initialize Firebase (use your config)
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_ID",
  appId: "YOUR_APP_ID"
};
firebase.initializeApp(firebaseConfig);

// Get messaging instance
const messaging = firebase.messaging();

// Request permission
Notification.requestPermission().then((permission) => {
  if (permission === 'granted') {
    messaging.getToken().then((token) => {
      // Send token to backend
      fetch('/register-device-token', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          device_token: token,
          phone: userPhone
        })
      });
    });
  }
});

// Listen for messages
messaging.onMessage((payload) => {
  console.log('Received:', payload);
  new Notification('Job Detection AI', {
    body: payload.notification.body,
    icon: '/static/images/logo.png'
  });
});
</script>
```

### Option B: Mobile App (Requires React Native/Flutter)

For a mobile app, use Firebase SDK for iOS/Android.

## Testing

### 1. Register a Device Token

```python
from database import register_device_token

# Simulate user registering device
result = register_device_token(
    phone='+918197420471',
    device_token='fake_device_token_12345',
    device_name='Test Device'
)
print(result)
```

### 2. Send Test OTP

```python
from database import send_sms, generate_otp, save_otp

username = 'testuser'
phone = '+918197420471'
otp = generate_otp()

# Save OTP to database
save_otp(username, phone, otp)

# Send via Firebase
send_sms(phone, f'Your OTP is: {otp}')
# [FCM SENT] message will appear
```

### 3. Check Device Tokens

```python
from database import get_device_tokens

tokens = get_device_tokens('+918197420471')
print(f"Registered devices: {tokens}")
```

## Troubleshooting

### Error: "Firebase credentials file not found"
- Ensure `firebase-credentials.json` is in the project root
- Check `.env` has correct path: `FIREBASE_CREDENTIALS_PATH=firebase-credentials.json`

### Error: "No device tokens found"
- User hasn't registered a device yet
- Device token registration requires user action on the frontend (Notification.requestPermission)
- Make sure web app has Firebase SDK and token registration code

### Error: "Invalid device token"
- Device token might be expired or revoked
- Tokens expire after ~60 days of inactivity
- User needs to load the web app again to refresh token

### Messages not appearing on device
- Check browser notifications are enabled in settings
- Ensure device token is registered (check `user_devices` table)
- Check Firebase console logs for errors

## Advantages of Firebase
✅ Completely FREE (no pay-per-message)  
✅ No phone number setup needed  
✅ Instant delivery  
✅ Works globally  
✅ Integrates with mobile apps  
✅ Rich notifications support  

## Limitations
⚠️ Requires user to register device (one-time)  
⚠️ Only works if user has app/browser open  
⚠️ Not true SMS (won't reach offline devices until they come online)  

## Production Checklist

- [ ] Firebase project created and credentials stored securely
- [ ] `firebase-credentials.json` added to `.gitignore`
- [ ] Web app has Firebase SDK and token registration code
- [ ] Tested OTP sending to registered device
- [ ] Error handling for missing device tokens
- [ ] Device token refresh logic implemented
- [ ] Database `user_devices` table populated with test devices

## Further Resources

- [Firebase Cloud Messaging Docs](https://firebase.google.com/docs/cloud-messaging)
- [Firebase Web SDK](https://firebase.google.com/docs/web/setup)
- [Firebase Console](https://console.firebase.google.com/)
