import csv
import os
import sys
import time
import openpyxl
from openpyxl.styles import PatternFill
from verifier import EmailVerifier

INPUT_FILE = 'emails_input.txt'
OUTPUT_TXT = 'emails_output.txt'
OUTPUT_CSV = 'emails_output.csv'
OUTPUT_XLSX = 'emails_output.xlsx'
RATE_LIMIT = 1.0

def get_status(result):
    """Maps verifier result to VALID, INVALID, or UNKNOWN."""
    if isinstance(result, dict):
        s = result.get('status', 'UNKNOWN').upper()
    else:
        s = str(result).upper()
    
    if s == 'VALID':
        return 'VALID'
    elif s in ('INVALID', 'NO-MX', 'SPAMTRAP', 'ABUSE', 'DISPOSABLE'):
        return 'INVALID'
    else:
        return 'UNKNOWN'

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, INPUT_FILE)
    
    if not os.path.exists(input_path):
        print(f"Error: {INPUT_FILE} not found.")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        emails = [line.strip() for line in f if line.strip()]

    if not emails:
        print("No emails to verify.")
        sys.exit(0)

    try:
        verifier = EmailVerifier(enable_whois=False)
    except TypeError:
        verifier = EmailVerifier()

    print(f"Starting verification for {len(emails)} emails...")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Email', 'Status'])
    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

    csv_path = os.path.join(base_dir, OUTPUT_CSV)
    txt_path = os.path.join(base_dir, OUTPUT_TXT)
    xlsx_path = os.path.join(base_dir, OUTPUT_XLSX)

    with open(csv_path, 'w', newline='', encoding='utf-8') as f_csv, \
         open(txt_path, 'w', encoding='utf-8') as f_txt:
        
        writer = csv.writer(f_csv)
        writer.writerow(['Email', 'Status'])

        for i, email in enumerate(emails, 1):
            print(f"[{i}/{len(emails)}] Verifying: {email}")
            result = verifier.verify(email)
            status = get_status(result)

            writer.writerow([email, status])
            f_txt.write(f"{email}: {status}\n")

            ws.append([email, status])
            if status in ('INVALID', 'UNKNOWN'):
                cell = ws.cell(row=ws.max_row, column=2)
                cell.fill = red_fill

            time.sleep(RATE_LIMIT)

    wb.save(xlsx_path)
    print("Verification complete.")

if __name__ == "__main__":
    main()