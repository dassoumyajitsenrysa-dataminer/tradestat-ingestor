"""Session management for EIDB Commodity x Country Timeseries scraper."""

import requests
from bs4 import BeautifulSoup
from loguru import logger


def create_session(user_agent: str) -> requests.Session:
    """Create a new requests session with default headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return session


def bootstrap_session(session: requests.Session, base_url: str, path: str) -> dict:
    """Bootstrap the session by fetching the page and extracting CSRF token."""
    url = f"{base_url}{path}"
    logger.info(f"Bootstrapping session: {url}")
    
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "lxml")
    token_input = soup.find("input", {"name": "_token"})
    if not token_input:
        raise RuntimeError("Missing CSRF token")
    
    logger.info("Successfully bootstrapped session")
    return {"_token": token_input.get("value")}
