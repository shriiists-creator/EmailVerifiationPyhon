# email_verifier/config.py

# --- SMTP Configuration ---
SMTP_TIMEOUT = 10  # seconds
SMTP_PORT = 25
SMTP_DEBUG_LEVEL = 0  # Set to 1 for verbose smtplib output

# --- Verification Logic ---
# Domains to use in HELO/EHLO commands. Using your own domains is best.
HELO_DOMAINS = [
    "gmail.com",
    "yahoo.com",
    "outlook.com",
]

# Email addresses to use in the 'MAIL FROM' command.
# Use addresses from domains you control if possible.
MAIL_FROM_EMAILS = [
    "test@example.com",
    "verify@example.org",
    "noreply@example.net",
]

# Number of retries for temporary SMTP errors (e.g., 4xx codes)
RETRY_COUNT = 1
RETRY_DELAY = 2  # seconds

# --- Catch-All Detection ---
# Number of random usernames to test for catch-all detection.
CATCH_ALL_TEST_COUNT = 3

# --- Risk Scoring Weights (Total should ideally be 100) ---
RISK_WEIGHTS = {
    'is_disposable': 40,
    'is_catch_all': 20,
    'no_mx': 50,
    'smtp_fail': 30,
    'is_spamtrap': 80,
    'is_abuse': 60,
    'domain_health_spf': -5,  # Negative because presence is good
    'domain_health_dkim': -5,
    'domain_health_dmarc': -10,
    'domain_health_a_record': -5,
}

# --- Provider Lists ---
FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "icloud.com", "mail.com", "zoho.com", "protonmail.com", "yandex.com"
}

# --- Role-Based Account Prefixes ---
ROLE_ACCOUNTS = {
    "admin", "administrator", "webmaster", "postmaster", "hostmaster",
    "support", "help", "sales", "info", "contact", "billing", "security",
    "abuse", "noreply", "marketing", "jobs", "hr"
}

# --- Spam Trap / Abuse Detection ---
SPAMTRAP_USERNAMES = {
    "spamtrap", "spam", "abuse-report", "phish", "phishing"
}

# --- File Paths ---
DISPOSABLE_DOMAINS_FILE = "disposable_domains.txt"
ABUSE_LIST_FILE = "abuse_list.txt"

# --- Optional Features ---
ENABLE_WHOIS = False # Set to True to enable domain age check (can be slow)