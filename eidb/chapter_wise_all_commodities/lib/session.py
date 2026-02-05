"""
Session management for EIDB Chapter-wise All Commodities scraper.
Handles HTTP session creation and CSRF token retrieval.
"""

import requests
from bs4 import BeautifulSoup
from loguru import logger


def create_session(user_agent: str) -> requests.Session:
    """
    Create a new requests session with default headers.
    
    Args:
        user_agent: User agent string for HTTP requests
        
    Returns:
        Configured requests.Session object
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    return session


def bootstrap_session(session: requests.Session, base_url: str, path: str) -> dict:
    """
    Bootstrap the session by fetching the page and extracting CSRF token.
    
    Args:
        session: Requests session object
        base_url: Base URL of the TradeStat portal
        path: Path to the page to bootstrap from
        
    Returns:
        Dictionary containing the CSRF token and other form state
    """
    url = f"{base_url}{path}"
    logger.info(f"Bootstrapping session: {url}")
    
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "lxml")
    
    # Extract CSRF token
    token_input = soup.find("input", {"name": "_token"})
    if not token_input:
        raise RuntimeError("Missing CSRF token in page")
    
    csrf_token = token_input.get("value")
    logger.info("Successfully bootstrapped session with CSRF token")
    
    return {
        "_token": csrf_token,
    }
