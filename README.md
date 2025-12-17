# Email Verification Tool with Google Sheets Integration

A Python-based email verification tool that performs comprehensive 3-level email validation and integrates with Google Sheets to read emails and write back verification results.

## Features

✅ **3-Level Email Verification:**
- **Level 1 (Syntax):** Regex-based email format validation
- **Level 2 (DNS):** MX record verification to ensure the domain can receive emails
- **Level 3 (SMTP):** SMTP handshake to verify the specific email address is accepted by the server

✅ **Google Sheets Integration:**
- Reads emails from Column A
- Writes results to Column B
- Automatic authentication using service account

✅ **Robust Error Handling:**
- Graceful handling of network errors
- Per-email error isolation (one failure doesn't crash the entire process)
- Rate limiting to avoid API/server blocks

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up Google Cloud credentials** (see detailed setup below)

## Google Cloud Console Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top and select **"New Project"**
3. Enter a project name (e.g., "Email Verifier") and click **"Create"**
4. Wait for the project to be created and select it

### Step 2: Enable Google Sheets API

1. In the Google Cloud Console, go to **"APIs & Services" > "Library"**
2. Search for **"Google Sheets API"**
3. Click on it and press **"Enable"**
4. Also search for **"Google Drive API"** and enable it as well

### Step 3: Create a Service Account

1. Go to **"APIs & Services" > "Credentials"**
2. Click **"Create Credentials"** and select **"Service Account"**
3. Enter a service account name (e.g., "email-verifier") and click **"Create and Continue"**
4. For role, select **"Editor"** (or you can skip this step)
5. Click **"Continue"** and then **"Done"**

### Step 4: Generate the credentials.json File

1. In the **"Credentials"** page, you'll see your newly created service account listed under **"Service Accounts"**
2. Click on the service account email
3. Go to the **"Keys"** tab
4. Click **"Add Key" > "Create new key"**
5. Select **"JSON"** as the key type
6. Click **"Create"**
7. A JSON file will be downloaded automatically - **this is your `credentials.json` file**
8. **IMPORTANT:** Rename this file to `credentials.json` and place it in the same directory as `verify_emails.py`

### Step 5: Note the Service Account Email

1. In the downloaded `credentials.json` file, look for the `"client_email"` field
2. It will look something like: `email-verifier@your-project.iam.gserviceaccount.com`
3. **Copy this email** - you'll need it in the next step

## Google Sheets Setup

### Step 1: Create Your Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet or use an existing one
3. Name it **"Email Verification"** (or change the `SPREADSHEET_NAME` variable in the script)

### Step 2: Format Your Sheet

Set up your sheet with the following structure:

| Column A (Email) | Column B (Result) |
|------------------|-------------------|
| Email            | Result            |
| user1@example.com|                   |
| user2@gmail.com  |                   |
| invalid-email    |                   |

- **Column A:** List all emails you want to verify (one per row)
- **Column B:** Leave empty - the script will fill this with results
- **Row 1:** Headers (will be ignored by the script)

### Step 3: Share the Sheet with Your Service Account

> [!IMPORTANT]
> This is a critical step - without it, the script cannot access your sheet!

1. In your Google Sheet, click the **"Share"** button (top-right corner)
2. Paste the **service account email** (from Step 5 above) into the "Add people and groups" field
3. Set the permission to **"Editor"**
4. **Uncheck** "Notify people" (service accounts don't need notifications)
5. Click **"Share"**

Your sheet is now accessible by the script!

## Usage

1. **Ensure all prerequisites are met:**
   - `credentials.json` is in the same directory as `verify_emails.py`
   - Google Sheet is created and shared with the service account
   - Column A contains emails to verify
   - Dependencies are installed

2. **Update the configuration (if needed):**
   
   Open `verify_emails.py` and modify these constants if needed:
   ```python
   CREDENTIALS_FILE = 'credentials.json'  # Path to credentials file
   SPREADSHEET_NAME = 'Email Verification'  # Your Google Sheet name
   RATE_LIMIT_DELAY = 2  # Seconds between checks
   ```

3. **Run the script:**
   ```bash
   python verify_emails.py
   ```

4. **Monitor the output:**
   
   The script will display progress for each email:
   ```
   ============================================================
   Email Verification Tool
   ============================================================
   
   Connecting to Google Sheets...
   ✓ Successfully connected to Google Sheet: 'Email Verification'
   
   Reading emails from sheet...
   ✓ Found 3 emails to verify
   
   Starting verification of 3 emails...
   ------------------------------------------------------------
   [1/3] Verifying: user@example.com
       Result: Valid - All checks passed
   [2/3] Verifying: invalid@nonexistentdomain123456.com
       Result: Invalid - No MX records found
   [3/3] Verifying: notanemail
       Result: Invalid - Failed syntax check
   ------------------------------------------------------------
   
   ✓ Verification complete! Processed 3 emails.
   ============================================================
   ```

5. **Check your Google Sheet:**
   
   Column B will now contain the verification results for each email.

## How It Works

### Verification Process

For each email address, the script performs:

1. **Syntax Check (Regex):**
   - Validates the email format using a regular expression
   - Checks for basic structure: `username@domain.tld`

2. **DNS/MX Record Check:**
   - Uses `dnspython` to query DNS for MX records
   - Verifies that the domain has mail servers configured
   - Retrieves mail server addresses sorted by priority

3. **SMTP Handshake:**
   - Connects to the mail server using `smtplib`
   - Performs SMTP handshake (HELO)
   - Sends MAIL FROM and RCPT TO commands
   - Checks if the server accepts the specific email address
   - **Important:** Quits before sending any actual data (no email is sent)

### Rate Limiting

The script includes a configurable delay between checks (`RATE_LIMIT_DELAY = 2` seconds by default) to:
- Avoid hitting Google API rate limits
- Prevent being blocked by mail servers for too many rapid connections
- Ensure reliable verification results

### Error Handling

The script is designed to be robust:
- Each email is processed independently
- Network errors or timeouts don't crash the entire process
- Failed verifications are logged with specific error details
- Connection errors to Google Sheets are caught and reported clearly

## Troubleshooting

### "Credentials file not found"
- Ensure `credentials.json` is in the same directory as the script
- Check the `CREDENTIALS_FILE` variable in the script

### "Spreadsheet not found"
- Verify the `SPREADSHEET_NAME` matches exactly (case-sensitive)
- Ensure the sheet is shared with your service account email

### "Permission denied" or access errors
- Make sure you shared the sheet with the service account as "Editor"
- Re-check the service account email in `credentials.json`

### SMTP verification failures
- Some mail servers may block verification attempts
- Corporate/enterprise mail servers often reject SMTP verification
- This is expected behavior and doesn't mean the email is invalid

### Rate limiting or timeouts
- Increase `RATE_LIMIT_DELAY` if you're getting blocked
- Some servers have strict rate limiting - consider smaller batches

## Security Notes

> [!CAUTION]
> **Keep your `credentials.json` file secure!**

- This file provides access to your Google account
- Never commit it to version control (add to `.gitignore`)
- Never share it publicly
- Store it securely and restrict file permissions

## Limitations

- **SMTP verification accuracy:** Some mail servers reject SMTP verification attempts, which may result in false negatives
- **Rate limits:** Both Google Sheets API and mail servers have rate limits
- **Temporary emails:** Disposable email services may pass verification but be unreliable
- **Catch-all domains:** Domains with catch-all configurations will accept any email address

## License

This project is open source and available for personal and commercial use.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all setup steps were completed correctly
3. Check the console output for specific error messages
#   E m a i l V e r i f i a t i o n P y h o n  
 