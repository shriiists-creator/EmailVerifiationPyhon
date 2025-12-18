# Email Validation Tool

A Python-based email validation tool that performs DNS-based checks without using SMTP connections. Designed to run in GitHub Actions and other headless environments.

## Features

✅ **Multi-Layer Email Validation:**
- **Syntax Validation:** RFC-compliant email format checking
- **DNS MX Records:** Verify domain can receive emails
- **Disposable Domain Detection:** Identify temporary/throwaway email services
- **Role-Based Detection:** Flag generic role accounts (admin@, info@, support@, etc.)
- **Domain Existence:** Verify domain has A/AAAA records

✅ **GitHub Actions Compatible:**
- No SMTP connections required
- No external API dependencies
- Runs in headless Linux environments
- No authentication or secrets needed

✅ **Multiple Output Formats:**
- `emails_output.txt` - Simple text format
- `emails_output.csv` - CSV format
- `emails_output.xlsx` - Excel with color-coded results

## Installation

1. **Clone this repository**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

1. **Add emails to validate:**
   
   Edit `emails_input.txt` and add one email per line:
   ```
   user@example.com
   admin@company.org
   test@tempmail.com
   ```

2. **Run the validation:**
   ```bash
   python main.py
   ```

3. **Check the results:**
   - `emails_output.txt` - Quick text view
   - `emails_output.csv` - Import into spreadsheets
   - `emails_output.xlsx` - Color-coded Excel file (red = INVALID/RISKY)

## Validation Statuses

- **VALID** - Email passes all checks (syntax, MX, domain exists, not disposable, not role-based)
- **INVALID** - Failed syntax check or no MX records found
- **RISKY** - Disposable domain, role-based account, or uncertain domain

## How It Works

### Validation Process

1. **Syntax Check:**
   - Uses regex to validate RFC-compliant email format
   - Checks basic structure: `username@domain.tld`

2. **DNS MX Record Check:**
   - Queries DNS for MX records
   - Verifies domain has mail servers configured

3. **Disposable Domain Detection:**
   - Checks against known disposable email providers
   - Identifies temporary/throwaway email services

4. **Role-Based Detection:**
   - Identifies generic role accounts (admin@, info@, support@, etc.)
   - Flags emails likely not monitored by individuals

5. **Domain Existence:**
   - Verifies domain has A or AAAA records
   - Confirms domain infrastructure exists

### No SMTP Connections

This tool does **NOT** use SMTP handshake verification:
- No outbound SMTP connections (port 25)
- No `RCPT TO` commands
- Fully compatible with GitHub Actions and headless environments
- No risk of being blocked by mail servers

## Configuration

Edit `config.py` to customize:
- Input/output file paths
- Role-based account prefixes

Edit `disposable_domains.txt` to add more disposable email providers.

## GitHub Actions Usage

Create `.github/workflows/validate-emails.yml`:

```yaml
name: Validate Emails

on: [push]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python main.py
      - uses: actions/upload-artifact@v2
        with:
          name: validation-results
          path: |
            emails_output.txt
            emails_output.csv
            emails_output.xlsx
```

## Limitations

- **Cannot verify if email address exists:** Without SMTP, we cannot confirm if a specific email address is valid, only that the domain can receive emails
- **Disposable domain list:** Requires manual updates as new services emerge
- **Catch-all domains:** Cannot detect catch-all configurations that accept any email
- **False positives:** Some legitimate emails may be flagged as RISKY if they use role-based addresses

## Honesty Note

This tool performs **email validation**, not **email verification**. It cannot guarantee an email address exists or is actively monitored. It validates:
- Correct syntax
- Domain can receive emails (has MX records)
- Not from known disposable providers
- Not a generic role account

## License

This project is open source and available for personal and commercial use.