"""
Session management for TradeStat website.
"""

import requests
from bs4 import BeautifulSoup


class TradeStatSession:
    def __init__(self, base_url: str, user_agent: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Referer": base_url,
        })

    def bootstrap(self, path: str):
        """Bootstrap session and get CSRF token."""
        url = f"{self.base_url}{path}"
        print(f"[*] Bootstrapping session: {url}")

        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # Extract CSRF token
        token_el = soup.find("input", {"name": "_token"})
        if not token_el:
            raise RuntimeError("Missing CSRF token")
        
        csrf_token = token_el.get("value")
        print(f"[+] Session bootstrapped successfully")
        
        return {"_token": csrf_token}
