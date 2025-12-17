# e:/Email Verifaction/verifier.py

import smtplib
import dns.resolver
import random
import config

class EmailVerifier:
    def __init__(self, enable_whois=False):
        pass

    def verify(self, email: str) -> str:
        if not email:
            return "INVALID"
        email = email.strip()
        if '@' not in email:
            return "INVALID"

        domain = email.split('@')[-1]
        mx_records = self._get_mx_records(domain)

        if not mx_records:
            return "INVALID"

        return self._perform_smtp_check(email, mx_records)

    def _get_mx_records(self, domain: str) -> list:
        try:
            records = dns.resolver.resolve(domain, 'MX')
            mx_records = sorted([(r.preference, str(r.exchange).rstrip('.')) for r in records])
            return [exchange for _, exchange in mx_records]
        except Exception:
            return []

    def _perform_smtp_check(self, email: str, mx_records: list) -> str:
        for mx_host in mx_records:
            try:
                with smtplib.SMTP(mx_host, config.SMTP_PORT, timeout=config.SMTP_TIMEOUT) as server:
                    server.helo(random.choice(config.HELO_DOMAINS))
                    server.mail(random.choice(config.MAIL_FROM_EMAILS))
                    code, _ = server.rcpt(email)

                    if code == 250:
                        return "VALID"
                    elif code >= 500:
                        return "INVALID"
            except Exception:
                continue
        
        return "UNKNOWN"