import requests
from bs4 import BeautifulSoup
from loguru import logger

class TradeStatSession:
    def __init__(self, base_url: str, user_agent: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Referer": base_url,
        })

    def bootstrap(self, path: str):
        url = f"{self.base_url}{path}"
        logger.info(f"Bootstrapping session: {url}")

        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        def _get(name: str, required=True):
            el = soup.find("input", {"name": name})
            if not el:
                if required:
                    raise RuntimeError(f"Missing form field: {name}")
                return None
            return el.get("value")

        # Extract CSRF token (Laravel uses _token instead of ASP.NET ViewState)
        csrf_token = _get("_token", required=True)
        
        logger.info(f"Successfully bootstrapped session with CSRF token")
        
        return {
            "_token": csrf_token,
        }
