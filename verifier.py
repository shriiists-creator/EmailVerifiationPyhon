import re
import os
import dns.resolver
from typing import Tuple, Set


class EmailVerifier:
    """Handles email validation using DNS-based checks (NO SMTP)."""
    
    def __init__(self, enable_whois=False):
        self.email_regex = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        self.disposable_domains = self._load_disposable_domains()
        self.role_prefixes = {
            'admin', 'administrator', 'webmaster', 'postmaster', 'hostmaster',
            'support', 'help', 'sales', 'info', 'contact', 'billing', 'security',
            'abuse', 'noreply', 'marketing', 'jobs', 'hr', 'no-reply', 'donotreply'
        }
    
    def _load_disposable_domains(self) -> Set[str]:
        """Load disposable email domains from file."""
        domains = set()
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(base_dir, 'disposable_domains.txt')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        domain = line.strip().lower()
                        if domain and not domain.startswith('#'):
                            domains.add(domain)
        except Exception:
            pass
        return domains
    
    def verify(self, email: str) -> str:
        """
        Validate email using DNS checks (NO SMTP).
        
        Returns:
            'VALID', 'INVALID', or 'RISKY'
        """
        email = email.strip().lower()
        
        if not email:
            return 'INVALID'
        
        # Syntax check
        if not self.email_regex.match(email):
            return 'INVALID'
        
        if '@' not in email:
            return 'INVALID'
        
        username, domain = email.rsplit('@', 1)
        
        # Check for disposable domain
        if domain in self.disposable_domains:
            return 'RISKY'
        
        # Check for role-based email
        username_clean = username.replace('.', '').replace('-', '').replace('_', '')
        if username_clean in self.role_prefixes:
            return 'RISKY'
        
        # DNS MX record check
        mx_records = self._get_mx_records(domain)
        if not mx_records:
            return 'INVALID'
        
        # Domain existence check (A record)
        if not self._check_domain_exists(domain):
            return 'RISKY'
        
        return 'VALID'
    
    def _get_mx_records(self, domain: str) -> list:
        """Check if domain has MX records."""
        try:
            records = dns.resolver.resolve(domain, 'MX')
            mx_records = sorted([(r.preference, str(r.exchange).rstrip('.')) for r in records])
            return [exchange for _, exchange in mx_records]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return []
        except Exception:
            return []
    
    def _check_domain_exists(self, domain: str) -> bool:
        """Check if domain has A or AAAA records."""
        try:
            dns.resolver.resolve(domain, 'A')
            return True
        except:
            pass
        
        try:
            dns.resolver.resolve(domain, 'AAAA')
            return True
        except:
            pass
        
        return False