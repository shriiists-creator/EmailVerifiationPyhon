"""
Configuration Template for Email Verification Tool

Copy this file to config.py and update with your settings.
"""

# Path to your Google Cloud service account credentials file
CREDENTIALS_FILE = 'credentials.json'

# Name of your Google Sheet (must match exactly)
SPREADSHEET_NAME = 'Email Verification'

# Delay in seconds between email verifications
# Increase this if you're getting rate limited
# Decrease to speed up processing (not recommended)
RATE_LIMIT_DELAY = 2

# SMTP timeout in seconds
SMTP_TIMEOUT = 10

# Sender email used for SMTP verification (can be fake)
SMTP_FROM_EMAIL = 'verify@example.com'

# Domain used for SMTP HELO command (can be fake)
SMTP_HELO_DOMAIN = 'verify.example.com'

# Enable debug mode for detailed SMTP logging
DEBUG_MODE = False
