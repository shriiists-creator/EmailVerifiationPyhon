# Email Validation Configuration

# Input/Output Files
INPUT_FILE = 'emails_input.txt'
OUTPUT_TXT = 'emails_output.txt'
OUTPUT_CSV = 'emails_output.csv'
OUTPUT_XLSX = 'emails_output.xlsx'

# Disposable Domain Detection
DISPOSABLE_DOMAINS_FILE = 'disposable_domains.txt'

# Role-Based Account Prefixes
ROLE_ACCOUNTS = {
    'admin', 'administrator', 'webmaster', 'postmaster', 'hostmaster',
    'support', 'help', 'sales', 'info', 'contact', 'billing', 'security',
    'abuse', 'noreply', 'marketing', 'jobs', 'hr', 'no-reply', 'donotreply'
}