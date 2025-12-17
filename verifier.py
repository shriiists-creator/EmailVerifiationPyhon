# e:/Email Verifaction/verifier.py

import smtplib
import dns.resolver
import socket
import random
import time
import re
import whois
from datetime import datetime

import config

class EmailVerifier:
    """
    A comprehensive email verification class that performs syntax checks,
    DNS validation, and SMTP handshakes without sending actual emails.
    """

    def __init__(self, enable_whois=config.ENABLE_WHOIS):
        """Initializes the verifier and loads data from external files."""
        self.enable_whois = enable_whois
        self._load_data_files()

    def _load_data_files(self):
        """Loads disposable domains and abuse lists from files."""
        try:
            with open(config.DISPOSABLE_DOMAINS_FILE, 'r') as f:
                self.disposable_domains = {line.strip().lower() for line in f}
        except FileNotFoundError:
            print(f"Warning: {config.DISPOSABLE_DOMAINS_FILE} not found. Disposable check disabled.")
            self.disposable_domains = set()

        try:
            with open(config.ABUSE_LIST_FILE, 'r') as f:
                self.abuse_list = {line.strip().lower() for line in f}
        except FileNotFoundError:
            self.abuse_list = set() # Optional file

    def verify(self, email: str) -> dict:
        """
        Performs full verification for a single email address.
        """
        email = email.lower().strip()
        local_part, domain = self._split_email(email)

        # Initialize result structure
        result = self._get_initial_result(email)

        # --- Level 1: Syntax and Basic Checks ---
        if not self._is_valid_syntax(email) or not local_part or not domain:
            return self._finalize_result(result, "INVALID", "Invalid syntax")

        result['is_role'] = self._is_role_account(local_part)
        result['is_disposable'] = self._is_disposable(domain)
        result['is_free_provider'] = self._is_free_provider(domain)

        if result['is_disposable']:
            return self._finalize_result(result, "DISPOSABLE", "Domain is from a disposable provider")

        is_abuse, abuse_reason = self._is_abuse_or_spamtrap(local_part, email)
        if is_abuse:
            return self._finalize_result(result, abuse_reason['status'], abuse_reason['details'])

        # --- Level 2: Domain/DNS Health Check ---
        mx_records = self._get_mx_records(domain)
        result['mx_records'] = mx_records
        result['domain_health'] = self._check_domain_health(domain)

        if not mx_records:
            return self._finalize_result(result, "NO-MX", "No MX records found for domain")

        # --- Level 3: SMTP Handshake ---
        smtp_result = self._perform_smtp_check(local_part, domain, mx_records)
        result.update(smtp_result)

        return self._finalize_result(result, result.get('status'), result.get('details'))

    def _get_initial_result(self, email: str) -> dict:
        """Returns the default dictionary structure for a verification result."""
        return {
            "email": email,
            "status": "UNKNOWN",
            "smtp_code": None,
            "details": "",
            "is_role": False,
            "is_disposable": False,
            "is_catch_all": False,
            "is_free_provider": False,
            "risk_score": 0,
            "mx_records": [],
            "domain_health": {
                "a_record": False, "spf": False, "dkim": False, "dmarc": False
            }
        }

    def _finalize_result(self, result: dict, status: str, details: str) -> dict:
        """Sets final status and details, and calculates risk score before returning."""
        result['status'] = status
        result['details'] = details
        result['risk_score'] = self._calculate_risk_score(result)
        return result

    def _split_email(self, email: str) -> tuple:
        """Splits email into local part and domain."""
        parts = email.split('@')
        return (parts[0], parts[1]) if len(parts) == 2 else (None, None)

    def _is_valid_syntax(self, email: str) -> bool:
        """Basic regex check for email syntax."""
        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        return re.match(pattern, email) is not None

    def _is_role_account(self, local_part: str) -> bool:
        """Checks if the local part corresponds to a role account."""
        return local_part in config.ROLE_ACCOUNTS

    def _is_disposable(self, domain: str) -> bool:
        """Checks if the domain is in the disposable list."""
        return domain in self.disposable_domains

    def _is_free_provider(self, domain: str) -> bool:
        """Checks if the domain is a known free email provider."""
        return domain in config.FREE_PROVIDERS

    def _is_abuse_or_spamtrap(self, local_part: str, email: str) -> tuple:
        """Checks for spamtrap usernames or if the email is on an abuse list."""
        if local_part in config.SPAMTRAP_USERNAMES:
            return True, {"status": "SPAMTRAP", "details": "Username is a known spamtrap"}
        if email in self.abuse_list:
            return True, {"status": "ABUSE", "details": "Email is on a known abuse list"}
        return False, {}

    def _get_mx_records(self, domain: str) -> list:
        """Gets MX records for a domain, sorted by priority."""
        try:
            records = dns.resolver.resolve(domain, 'MX')
            mx_records = sorted([(r.preference, str(r.exchange).rstrip('.')) for r in records])
            return [exchange for _, exchange in mx_records]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.resolver.LifetimeTimeout):
            return []

    def _check_domain_health(self, domain: str) -> dict:
        """Checks for A, SPF, DKIM, and DMARC records."""
        health = {"a_record": False, "spf": False, "dkim": False, "dmarc": False}
        
        # Define a common set of DNS exceptions to catch, including timeouts.
        dns_exceptions = (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.LifetimeTimeout)

        try:
            # A Record
            dns.resolver.resolve(domain, 'A')
            health['a_record'] = True
        except dns_exceptions:
            pass

        try:
            # SPF Record
            txt_records = dns.resolver.resolve(domain, 'TXT')
            for record in txt_records:
                if 'v=spf1' in record.to_text().lower():
                    health['spf'] = True
                    break
        except dns_exceptions:
            pass

        # DKIM (checks for common selector _domainkey)
        try:
            dns.resolver.resolve(f"default._domainkey.{domain}", 'TXT')
            health['dkim'] = True
        except dns_exceptions:
            pass

        # DMARC
        try:
            dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
            health['dmarc'] = True
        except dns_exceptions:
            pass

        return health

    def _perform_smtp_check(self, local_part: str, domain: str, mx_records: list) -> dict:
        """
        Connects to mail servers and simulates sending an email to check validity.
        Also performs catch-all detection.
        """
        email = f"{local_part}@{domain}"
        result = {}
        
        for mx_host in mx_records:
            helo_domain = random.choice(config.HELO_DOMAINS)
            from_email = random.choice(config.MAIL_FROM_EMAILS)
            
            for i in range(config.RETRY_COUNT + 1):
                try:
                    with smtplib.SMTP(mx_host, config.SMTP_PORT, timeout=config.SMTP_TIMEOUT) as server:
                        server.set_debuglevel(config.SMTP_DEBUG_LEVEL)
                        
                        # SMTP Handshake
                        server.helo(helo_domain)
                        server.mail(from_email)
                        code, message = server.rcpt(email)
                        
                        result['smtp_code'] = code
                        
                        # Interpret SMTP response code
                        if 200 <= code < 300: # 250, 251, 252
                            # Potential valid or catch-all, need to test further
                            is_catch_all = self._detect_catch_all(server, domain, from_email)
                            result['is_catch_all'] = is_catch_all
                            if is_catch_all:
                                result['status'] = "CATCH-ALL"
                                result['details'] = f"Domain is a catch-all, accepted by {mx_host}"
                            else:
                                result['status'] = "VALID"
                                result['details'] = f"Accepted by {mx_host}"
                            return result
                        
                        elif code in {421, 450, 451, 452}: # Temporary failure
                            result['status'] = "UNKNOWN"
                            result['details'] = f"Temporary SMTP error on {mx_host} (Code {code})"
                            # This break will trigger the retry logic below
                            break 
                        
                        elif code >= 500: # 550, 551, 553, etc.
                            result['status'] = "INVALID"
                            result['details'] = f"Rejected by {mx_host} (Code {code})"
                            return result
                        
                except (socket.timeout, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, OSError) as e:
                    result['status'] = "UNKNOWN"
                    result['details'] = f"Could not connect to {mx_host}: {e}"
                    # This break will move to the next MX record
                    break
                
                # If we had a temporary failure, wait and retry
                if i < config.RETRY_COUNT:
                    time.sleep(config.RETRY_DELAY)

            # If we exhausted retries for this MX host, continue to the next one
            if result.get('status') == "UNKNOWN":
                continue

        # If all MX servers failed
        if not result:
            return {"status": "UNKNOWN", "details": "Could not connect to any mail server"}
            
        return result

    def _detect_catch_all(self, server: smtplib.SMTP, domain: str, from_email: str) -> bool:
        """
        Tests random, likely non-existent email addresses on the same domain
        to determine if the server is a catch-all.
        """
        for _ in range(config.CATCH_ALL_TEST_COUNT):
            # Generate a random username that is highly unlikely to exist
            random_user = f"nouser-{random.randint(10000, 99999)}-{int(time.time())}"
            test_email = f"{random_user}@{domain}"
            
            try:
                # We need to restart the transaction for some servers
                server.docmd("RSET")
                server.mail(from_email)
                code, _ = server.rcpt(test_email)
                
                if code >= 500:
                    # If any random email is rejected, it's not a catch-all
                    return False
            except smtplib.SMTPException:
                # If the server fails on a random check, assume not catch-all for safety
                return False
        
        # If all random emails were accepted, it's a catch-all
        return True

    def _calculate_risk_score(self, result: dict) -> int:
        """Calculates a risk score from 0 to 100 based on verification results."""
        score = 0
        if result['is_disposable']:
            score += config.RISK_WEIGHTS.get('is_disposable', 40)
        if result['is_catch_all']:
            score += config.RISK_WEIGHTS.get('is_catch_all', 20)
        if result['status'] == "NO-MX":
            score += config.RISK_WEIGHTS.get('no_mx', 50)
        if result['status'] == "INVALID":
            score += config.RISK_WEIGHTS.get('smtp_fail', 30)
        if result['status'] == "SPAMTRAP":
            score += config.RISK_WEIGHTS.get('is_spamtrap', 80)
        if result['status'] == "ABUSE":
            score += config.RISK_WEIGHTS.get('is_abuse', 60)

        # Domain health reduces risk
        if result['domain_health']['a_record']:
            score += config.RISK_WEIGHTS.get('domain_health_a_record', -5)
        if result['domain_health']['spf']:
            score += config.RISK_WEIGHTS.get('domain_health_spf', -5)
        if result['domain_health']['dkim']:
            score += config.RISK_WEIGHTS.get('domain_health_dkim', -5)
        if result['domain_health']['dmarc']:
            score += config.RISK_WEIGHTS.get('domain_health_dmarc', -10)
        
        # Optional: Domain Age (if WHOIS is enabled and successful)
        if self.enable_whois:
            try:
                domain_info = whois.whois(self._split_email(result['email'])[1])
                if domain_info.creation_date:
                    creation_date = domain_info.creation_date
                    if isinstance(creation_date, list):
                        creation_date = creation_date[0]
                    age_days = (datetime.now() - creation_date).days
                    if age_days < 90:
                        score += 15 # Newer domains are riskier
                    elif age_days < 365:
                        score += 5
            except Exception:
                pass # Ignore WHOIS errors

        return max(0, min(100, score))