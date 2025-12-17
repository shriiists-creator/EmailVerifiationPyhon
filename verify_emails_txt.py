#!/usr/bin/env python3
"""
Email Verification Tool
This script performs 3-level email verification using SMTP handshake.
"""

import re
import time
import smtplib
import dns.resolver
import csv
import random
import socket
from typing import Tuple, List

# Import configuration from config.py
try:
    import config
except ImportError:
    print("Error: Configuration file 'config.py' not found. Please create it.")
    exit()


class EmailVerifier:
    """Handles 3-level email verification: Syntax, DNS, and SMTP Handshake."""
    
    def __init__(self, from_domain: str):
        self.email_regex = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        self.from_domain = from_domain
    
    def verify_email(self, email: str) -> Tuple[str, str]:
        """
        Perform comprehensive email verification.
        
        Args:
            email: The email address to verify.
            
        Returns:
            A tuple of (status, details).
        """
        email = email.strip()
        
        if not email:
            return ('INVALID', 'Level 1: Empty email address')
        
        # Level 1: Syntax Check
        if not self._check_syntax(email):
            return ('INVALID', 'Level 1: Invalid syntax')
        
        # Extract domain
        try:
            domain = email.split('@')[1]
        except IndexError:
            return ('INVALID', 'Level 1: Invalid format')
        
        # Level 2: DNS/MX Record Check
        mx_records = self._check_dns(domain)
        if not mx_records:
            return ('NO-MX', 'Level 2: No MX records found')
        
        # Level 3: SMTP Handshake Check
        status, details = self._check_smtp(email, mx_records)
        return status, details
    
    def _check_syntax(self, email: str) -> bool:
        """Level 1: Validate email syntax using regex."""
        return bool(self.email_regex.match(email))
    
    def _check_dns(self, domain: str) -> List[str]:
        """
        Level 2: Check if domain has valid MX records.
        
        Returns:
            List of MX record hostnames, sorted by priority
        """
        try:
            print(f"    - L2: Querying MX records for {domain}...")
            mx_records = dns.resolver.resolve(domain, 'MX')
            # Sort by priority (lower number = higher priority)
            sorted_records = [str(r.exchange).rstrip('.') for r in sorted(mx_records, key=lambda r: r.preference)]
            print(f"    - L2: Found {len(sorted_records)} MX records.")
            return sorted_records
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout):
            return []
        except Exception as e:
            print(f"    - L2: DNS check error for {domain}: {str(e)}")
            return []
    
    def _check_smtp(self, email: str, mx_hosts: List[str]) -> Tuple[str, str]:
        """
        Level 3: Perform SMTP handshake to verify email acceptance.
        
        Connects to the mail server and uses RCPT TO to check recipient status.
        """
        # Generate a random local part for the 'MAIL FROM' address
        random_user = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
        from_email = f"{random_user}@{self.from_domain}"

        for mx_host in mx_hosts:
            try:
                print(f"    - L3: Connecting to {mx_host}...")
                with smtplib.SMTP(mx_host, port=25, timeout=10) as server:
                    server.helo(self.from_domain)
                    server.mail(from_email)
                    
                    # Send RCPT TO and check the response code
                    code, message = server.rcpt(email)
                    
                    if code == 250: # Success
                        return ('VALID', f'L3: Accepted by {mx_host}')
                    elif code == 550: # Recipient does not exist
                        return ('INVALID', f'L3: Recipient does not exist (Code {code})')
                    elif 200 <= code < 300: # Ambiguous success (e.g., 252)
                        return ('INVALID', f'L3: Rejected by {mx_host} (Code {code})')
                    else: # Other codes (e.g., 4xx temporary failures) are uncertain
                        return ('UNKNOWN', f'L3: Temporary error on {mx_host} (Code {code})')

            except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, socket.timeout, smtplib.SMTPHeloError):
                print(f"    - L3: Connection to {mx_host} failed. Trying next MX record.")
                continue
            except smtplib.SMTPRecipientsRefused:
                # This can happen if the server rejects the RCPT TO command immediately
                return ('INVALID', 'L3: Recipient refused by server')
            except Exception as e:
                print(f"    - L3: An unexpected error occurred with {mx_host}: {str(e)}")
                continue

        return ('UNKNOWN', 'Level 3: Could not connect to any mail server')


def read_emails_from_file(filename: str) -> List[str]:
    """
    Read emails from a text file.
    
    Args:
        filename: Path to the input file
        
    Returns:
        List of email addresses
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Read all lines, strip whitespace, and filter out empty lines
            emails = [line.strip() for line in f.readlines() if line.strip()]
        print(f"✓ Found {len(emails)} emails to verify in '{filename}'")
        return emails
    except FileNotFoundError:
        raise Exception(f"Input file not found: {filename}")
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")


def write_results_to_file(results: list, filename: str):
    """
    Write verification results to a CSV file.
    
    Args:
        results: List of tuples (email, status, details)
        filename: Path to the output CSV file
    """
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Write the header row
            writer.writerow(['Email', 'Status', 'Details'])
            
            # Write the data rows
            for email, status, details in results:
                writer.writerow([email, status, details])
        
        print(f"\n✓ Results written to: {filename}")
    except Exception as e:
        print(f"\n✗ Error writing results to file: {str(e)}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Email Verification Tool (SMTP Handshake)")
    print("=" * 60)
    
    try:
        # Initialize email verifier
        verifier = EmailVerifier(from_domain=config.SMTP_FROM_DOMAIN)
        
        # Read emails from file
        emails = read_emails_from_file(config.INPUT_FILE)
        
        if not emails:
            print("No emails found in the input file. Exiting.")
            return
        
        # Process each email
        print(f"\nStarting verification of {len(emails)} emails...")
        print("-" * 60)
        
        results = []
        
        for idx, email in enumerate(emails, 1):
            print(f"[{idx}/{len(emails)}] Verifying: {email}")
            
            status, details = verifier.verify_email(email)
            results.append((email, status, details))
            
            print(f"    → Result: {status} - {details}")
            
            # Rate limiting to avoid being blocked by mail servers
            if idx < len(emails):
                time.sleep(config.RATE_LIMIT_DELAY)
        
        print("-" * 60)
        
        # Sort results by status for easier review in the output file
        print("Sorting results by status...")
        sort_order = {'VALID': 0, 'CATCH-ALL': 1, 'UNKNOWN': 2, 'INVALID': 3, 'NO-MX': 4}
        results.sort(key=lambda res: sort_order.get(res[1], 99))
        
        # Write results to output file
        write_results_to_file(results, config.OUTPUT_FILE)
        
        # Print summary
        summary = {}
        for _, status, _ in results:
            summary[status] = summary.get(status, 0) + 1
            
        print("\n✓ Verification Complete!")
        print("  Summary:")
        for status, count in summary.items():
            print(f"    - {status}: {count}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user.")
    except Exception as e:
        print(f"\n✗ An unexpected error occurred: {str(e)}")
        print(f"  Please ensure '{config.INPUT_FILE}' exists and 'config.py' is set up correctly.")


if __name__ == '__main__':
    main()
