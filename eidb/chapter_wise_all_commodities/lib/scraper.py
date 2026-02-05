"""
Scraper module for EIDB Chapter-wise All Commodities data.
Handles HTTP requests to fetch trade data.
"""

import requests
from loguru import logger
from typing import Optional

# URL paths
EXPORT_PATH = "/eidb/chapter_wise_export"
IMPORT_PATH = "/eidb/chapter_wise_import"

# Available years
AVAILABLE_YEARS = list(range(2018, 2026))

# HS code levels
HS_LEVELS = [2, 4, 6, 8]

# Value types
VALUE_TYPES = {
    "usd": "2",  # US $ Million
    "inr": "1",  # ₹ Crore
}


def fetch_chapter_data(
    session: requests.Session,
    base_url: str,
    year: str,
    digit_level: int,
    trade_type: str,
    value_type: str,
    state: dict
) -> Optional[str]:
    """
    Fetch chapter-wise all commodities data from EIDB.
    
    Args:
        session: Requests session object
        base_url: Base URL of TradeStat portal
        year: Financial year (e.g., "2024")
        digit_level: HS code level (2, 4, 6, or 8)
        trade_type: "export" or "import"
        value_type: "usd" or "inr"
        state: Dictionary containing CSRF token
        
    Returns:
        HTML response as string, or None if request fails
    """
    if trade_type.lower() == "export":
        path = EXPORT_PATH
    else:
        path = IMPORT_PATH
    
    # Map value type to form value
    report_value = VALUE_TYPES.get(value_type.lower(), "2")
    
    # Build payload
    payload = {
        "_token": state["_token"],
        "EidbYear": year,
        "EidbComLevel": str(digit_level),
        "Eidb_Report": report_value,
    }
    
    logger.info(f"Fetching chapter-wise data: YEAR={year}, LEVEL={digit_level}, TYPE={trade_type}")
    
    try:
        resp = session.post(
            base_url + path,
            data=payload,
            timeout=120,
        )
        resp.raise_for_status()
        logger.success(f"Chapter-wise data fetch successful: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        logger.error(f"Chapter-wise data fetch failed: {e}")
        return None
