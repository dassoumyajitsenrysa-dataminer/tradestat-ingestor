"""
Session management for TradeStat website.
Handles CSRF token extraction and session cookies.
"""

import requests
from bs4 import BeautifulSoup


def create_session(base_url: str) -> tuple:
    """
    Create a requests session and extract CSRF token from the page.
    
    Args:
        base_url: The URL to fetch CSRF token from
        
    Returns:
        Tuple of (session, csrf_token)
    """
    session = requests.Session()
    
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    })
    
    response = session.get(base_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'lxml')
    csrf_input = soup.find('input', {'name': '_token'})
    
    if not csrf_input:
        raise ValueError("Could not find CSRF token on page")
    
    csrf_token = csrf_input.get('value')
    
    return session, csrf_token
