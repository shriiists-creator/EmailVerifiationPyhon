# How to Enable Level 4 Email Sending

Level 4 verification actually sends a test email to verify the address can receive messages.

## Quick Setup (Gmail)

### Step 1: Enable 2-Step Verification

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left menu
3. Under "Signing in to Google", click **2-Step Verification**
4. Follow the steps to enable it

### Step 2: Create an App Password

1. Go to: https://myaccount.google.com/apppasswords
2. In the "App name" field, type: **Email Verifier**
3. Click **Create**
4. Google will show you a 16-character password - **COPY IT**
5. This is your `SENDER_PASSWORD`

### Step 3: Configure the Script

Open `verify_emails.py` and update lines 18-22:

```python
# Level 4: Email Sending Configuration
ENABLE_EMAIL_SENDING = True          # Set to True to enable
SENDER_EMAIL = 'your-email@gmail.com'  # Replace with YOUR Gmail
SENDER_PASSWORD = 'xxxx xxxx xxxx xxxx'  # Paste the 16-char app password
SMTP_SERVER = 'smtp.gmail.com'       # Keep as is for Gmail
SMTP_PORT = 587                      # Keep as is
```

**Example:**
```python
ENABLE_EMAIL_SENDING = True
SENDER_EMAIL = 'smit93888@gmail.com'
SENDER_PASSWORD = 'abcd efgh ijkl mnop'  # 16-character app password from Google
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
```

### Step 4: Run the Script

```bash
python verify_emails.py
```

Now the script will:
1. Level 1: Check syntax ✓
2. Level 2: Check DNS/MX records ✓
3. Level 3: Check SMTP handshake ✓
4. Level 4: **Send test email** ✓ (NEW!)

---

## Using Other Email Providers

### Yahoo Mail
```python
SMTP_SERVER = 'smtp.mail.yahoo.com'
SMTP_PORT = 587
```

### Outlook/Hotmail
```python
SMTP_SERVER = 'smtp-mail.outlook.com'
SMTP_PORT = 587
```

### Custom SMTP Server
```python
SENDER_EMAIL = 'your-email@yourdomain.com'
SENDER_PASSWORD = 'your-email-password'
SMTP_SERVER = 'smtp.yourdomain.com'
SMTP_PORT = 587  # or 465 for SSL
```

---

## What Gets Sent?

Recipients will receive a professional test email with:
- Subject: "Email Verification - Test Message"
- A random 6-character verification code
- Professional HTML formatting
- Clear message that it's an automated test

**Example:**
```
Email Verification Test

Verification Code: A3X9K2

If you did not request this verification, please ignore this email.
```

---

## Disable Level 4

To run only levels 1-3 (without sending emails):

```python
ENABLE_EMAIL_SENDING = False
```

---

## Security Notes

⚠️ **IMPORTANT:**
- Never share your app password
- Never commit it to version control
- App passwords bypass 2-step verification, so keep them secure
- If compromised, revoke it immediately at https://myaccount.google.com/apppasswords

---

## Troubleshooting

**"Authentication failed"**
→ Verify your app password is correct (16 characters, no spaces in code)

**"SMTP error while sending"**
→ Check your internet connection and SMTP server settings

**Level 4 shows as DISABLED**
→ Make sure you changed `SENDER_EMAIL` from the default `your-email@gmail.com`
