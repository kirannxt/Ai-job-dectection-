# Notification System Setup Guide

This application now supports **Email (SMTP)** and **WhatsApp (Twilio)** notifications for all major events.

## Quick Start Setup

### 1. Create `.env` File

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

### 2. Email Setup (Gmail SMTP)

**For Gmail:**

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Navigate to Security → App passwords
   - Generate password for "Mail" and "Mac"
   - Copy the 16-character password

3. Update `.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_16_char_app_password
```

**For Other Email Providers:**
- Outlook: `smtp-mail.outlook.com:587`
- Yahoo: `smtp.mail.yahoo.com:587`
- Custom: Use your provider's SMTP settings

### 3. WhatsApp Setup (Twilio)

1. Create a Twilio account at [twilio.com](https://www.twilio.com)
2. Get your credentials:
   - Account SID: From Twilio Console dashboard
   - Auth Token: From Twilio Console dashboard
   - WhatsApp Sandbox Number: From Twilio → Messaging → Try It Out → Send a WhatsApp Message

3. Update `.env`:
```
TWILIO_ACCOUNT_SID=AC6fa22140130ce48781cb3f87097cd8c8
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

**Getting WhatsApp Sandbox Ready:**
- Send "join [join-code]" to the Twilio WhatsApp sandbox number
- This connects your personal WhatsApp account to Twilio sandbox
- You'll receive a confirmation message

**Optional - Template Messages:**
1. Create message templates in Twilio Console → Messaging → Content → Templates
2. Get Content SID for each template
3. Update `.env` with Content SIDs:
```
TWILIO_WHATSAPP_CONTENT_SID_LOGIN=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_CONTENT_SID_UPLOAD=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_CONTENT_SID_TRAINING=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_CONTENT_SID_DETECTION=HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Notification Events

The system sends notifications for:

| Event | When | Medium |
|-------|------|--------|
| **Login** | User logs in | Email + WhatsApp |
| **File Upload** | CSV/Excel uploaded | Email + WhatsApp |
| **Model Training** | Training completes | Email + WhatsApp |
| **Job Detection** | Job analyzed | Email + WhatsApp |

## User Setup

### Step 1: Add WhatsApp Contact
1. Go to **Profile** → **Update Contact**
2. Enter your WhatsApp number with country code
   - Example: `+91 8197420471` (India)
   - Example: `+1 2025551234` (USA)

### Step 2: Enable WhatsApp Notifications
1. Go to **Settings**
2. Check "WhatsApp Notifications"
3. Save Changes

### Step 3: Join Twilio WhatsApp Sandbox
1. Send message to Twilio WhatsApp number with: `join [join-code]`
2. Join code from Twilio → Messaging → Try It Out → Send a WhatsApp Message
3. You'll get confirmation when connected

## Troubleshooting

### Email Not Sending?
- Check `.env` file has correct SENDER_EMAIL and SENDER_PASSWORD
- For Gmail: Verify App Password is 16 characters (spaces removed)
- Check user has email in their profile (Profile → Update Contact)
- Check email notifications enabled in Settings

### WhatsApp Not Sending?
- Verify in Twilio Console that WhatsApp is enabled
- Check `.env` has valid TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
- Verify WhatsApp number matches sandbox number
- Check you sent "join [code]" to sandbox to confirm connection
- Check user has WhatsApp number in Profile (Profile → Update Contact)
- Check WhatsApp Notifications enabled in Settings
- Ensure WhatsApp number has country code: +91, +1, etc.

### Testing
Perform these actions to test:
1. Log in → Check for welcome notification
2. Upload a file → Check upload notification
3. Train a model → Check training completion notification
4. Analyze a job → Check job detection notification

## Security Notes

⚠️ **Never commit `.env` to Git!** It's in `.gitignore`

- Keep your SENDER_PASSWORD and Twilio credentials confidential
- Use App Passwords (Gmail), not your primary password
- Regenerate credentials if compromised
- Keep Twilio Auth Token private

## Console Output

While testing:
- Notifications print to application console
- Shows `[WhatsApp SENT]` with recipient and SID
- Shows `[WhatsApp ERROR]` on failures
- Shows `[EMAIL SENT]` for email notifications
- Shows `[EMAIL ERROR]` for email failures

## Disabling Notifications

To disable temporarily:
1. Leave `.env` values empty/blank
2. Notifications will fail gracefully without crashing app
3. Console will show "credentials not configured" message

## Phone Number Format

**Important:** WhatsApp numbers must include:
- ✅ Country code: +91 (India), +1 (USA), +44 (UK), etc.
- ✅ Full phone number: +918197420471
- ✅ No spaces or special characters in storage
- ✅ Display format can include spaces: +91 8197 420471

## Support

For issues:
- Gmail: Check [Gmail Support](https://support.google.com/)
- Twilio: Check [Twilio Docs](https://www.twilio.com/docs/whatsapp)
- WhatsApp: Check [WhatsApp Business FAQ](https://www.whatsapp.com/business/)

## Example `.env` Configuration

```
# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_16_chars

# WhatsApp via Twilio
TWILIO_ACCOUNT_SID=AC6fa22140130ce48781cb3f87097cd8c8
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_CONTENT_SID_LOGIN=HXb5b62575e6e4ff6129ad7c8efe1f983e
TWILIO_WHATSAPP_CONTENT_SID_UPLOAD=HXb5b62575e6e4ff6129ad7c8efe1f983e
TWILIO_WHATSAPP_CONTENT_SID_TRAINING=HXb5b62575e6e4ff6129ad7c8efe1f983e
TWILIO_WHATSAPP_CONTENT_SID_DETECTION=HXb5b62575e6e4ff6129ad7c8efe1f983e
```
