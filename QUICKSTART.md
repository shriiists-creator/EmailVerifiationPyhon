# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.7 or higher
- A Google account
- Internet connection

## Step-by-Step Setup

### 1. Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### 2. Get Google Credentials (2 minutes)

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable **Google Sheets API** and **Google Drive API**
4. Create a **Service Account**
5. Download the JSON key file
6. Rename it to `credentials.json` and place it in this folder

**Detailed guide:** See [README.md](README.md#google-cloud-console-setup)

### 3. Prepare Your Google Sheet (1 minute)

1. Create a new Google Sheet named **"Email Verification"**
2. Format it like this:

   | A (Email)        | B (Result) |
   |------------------|------------|
   | Email            | Result     |
   | test@gmail.com   |            |
   | user@yahoo.com   |            |

3. **Share** the sheet with the service account email from `credentials.json`
   - Look for `"client_email"` in the JSON file
   - Share with **Editor** permissions

### 4. Run the Script (30 seconds)

```bash
python verify_emails.py
```

That's it! The script will verify all emails and write results to Column B.

## Example Output

```
============================================================
Email Verification Tool
============================================================

Connecting to Google Sheets...
✓ Successfully connected to Google Sheet: 'Email Verification'

Reading emails from sheet...
✓ Found 2 emails to verify

Starting verification of 2 emails...
------------------------------------------------------------
[1/2] Verifying: test@gmail.com
    Result: Valid - All checks passed
[2/2] Verifying: user@yahoo.com
    Result: Valid - All checks passed
------------------------------------------------------------

✓ Verification complete! Processed 2 emails.
============================================================
```

## Troubleshooting

**"Credentials file not found"**
→ Make sure `credentials.json` is in the same folder as `verify_emails.py`

**"Spreadsheet not found"**
→ Check that the sheet name matches exactly (case-sensitive)

**"Permission denied"**
→ Share the Google Sheet with your service account email (Editor access)

For more help, see the full [README.md](README.md)

## Next Steps

- Customize settings by creating a `config.py` from `config.example.py`
- Add more emails to verify
- Adjust `RATE_LIMIT_DELAY` if needed
