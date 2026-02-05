"""Session management for MEIDB Commodity-wise All Countries scraper."""

import requests
from bs4 import BeautifulSoup
from loguru import logger


def create_session(user_agent: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    return session


def bootstrap_session(session: requests.Session, base_url: str, path: str) -> dict:
    url = f"{base_url}{path}"
    logger.info(f"Bootstrapping: {url}")
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    token = soup.find("input", {"name": "_token"})
    if not token:
        raise RuntimeError("Missing CSRF token")
    logger.info("Session bootstrapped")
    return {"_token": token.get("value")}
