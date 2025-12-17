# e:/Email Verifaction/main.py
import json
import time
import openpyxl
from openpyxl.styles import PatternFill
from verifier import EmailVerifier
import config

INPUT_FILE = 'emails_input.txt'
OUTPUT_FILE = 'emails_output.xlsx'
RATE_LIMIT_DELAY = 1 # seconds to wait between checks

def main():
    """
    Main function to run the email verification process.
    """
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            emails_to_verify = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found.")
        print("Please create it and add one email per line.")
        return

    # Initialize the verifier
    # Set enable_whois=True for domain age check (slower)
    verifier = EmailVerifier(enable_whois=config.ENABLE_WHOIS)

    print(f"Starting verification for {len(emails_to_verify)} emails from '{INPUT_FILE}'...")

    # Initialize Excel Workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    # Define red fill for VALID rows
    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
    headers = []

    try:
        for i, email in enumerate(emails_to_verify):
            print(f"[{i+1}/{len(emails_to_verify)}] Verifying: {email}")
            result = verifier.verify(email)
            
            # Write headers based on the first result
            if i == 0:
                headers = list(result.keys())
                ws.append(headers)

            # Write row data
            row_values = [str(result.get(h, '')) for h in headers]
            ws.append(row_values)

            # Apply formatting for VALID status
            if result.get('status') == 'VALID':
                for cell in ws[ws.max_row]:
                    cell.fill = red_fill

            # Save every 50 emails
            if (i + 1) % 50 == 0:
                print(f"Saving progress to '{OUTPUT_FILE}'...")
                wb.save(OUTPUT_FILE)

            time.sleep(RATE_LIMIT_DELAY)

    except Exception as e:
        print(f"\nAn error occurred during processing: {e}")
    finally:
        # Final save (runs even if error occurs)
        if len(emails_to_verify) > 0:
            wb.save(OUTPUT_FILE)
            print(f"\nResults saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()