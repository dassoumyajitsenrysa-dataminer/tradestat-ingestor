"""
Chapter-wise all commodities scraper for TradeStat.
Fetches export/import data by HS code chapter at different digit levels.
"""

import requests


# Available years
AVAILABLE_YEARS = ["2024", "2023", "2022", "2021", "2020", "2019", "2018"]

# Value type mapping
VALUE_TYPES = {
    "usd": "2",    # US $ Million
    "inr": "1",    # ₹ Crore
    "qty": "3",    # Quantity
}

# HS code digit levels
HS_LEVELS = ["2", "4", "6", "8"]


def get_base_url(trade_type: str) -> str:
    """Get the base URL for the given trade type."""
    if trade_type == "export":
        return "https://tradestat.commerce.gov.in/eidb/chapter_wise_all_commodities_export"
    else:
        return "https://tradestat.commerce.gov.in/eidb/chapter_wise_all_commodities_import"


def get_hs_level(hs_code: str) -> str:
    """Determine the HS level from the code length."""
    if hs_code == "all":
        return "2"
    length = len(hs_code)
    if length <= 2:
        return "2"
    elif length <= 4:
        return "4"
    elif length <= 6:
        return "6"
    else:
        return "8"


def get_chapter_from_hs(hs_code: str) -> str:
    """Extract the 2-digit chapter from an HS code."""
    if hs_code == "all":
        return "all"
    return hs_code[:2].zfill(2)


def fetch_chapter_data(
    session: requests.Session,
    csrf_token: str,
    trade_type: str,
    year: str,
    hs_code: str = "all",
    value_type: str = "usd"
) -> str:
    """
    Fetch chapter-wise data for a specific year and HS code.
    
    Args:
        session: Requests session with cookies
        csrf_token: CSRF token for the request
        trade_type: "export" or "import"
        year: Year code (e.g., "2024")
        hs_code: HS code (2, 4, 6, or 8 digits) or "all"
        value_type: "usd", "inr", or "qty"
        
    Returns:
        HTML response text
    """
    url = get_base_url(trade_type)
    value_code = VALUE_TYPES.get(value_type, "2")
    level = get_hs_level(hs_code)
    chapter = get_chapter_from_hs(hs_code)
    
    # Build payload based on trade type
    # Export: eidbYearChwe, eidbReportChwe, eidbChapterEx
    # Import: eidbcwacoimpYear, eidbcwacoimpddReportVal, eidbcwacoimpddChapter
    if trade_type == "export":
        payload = {
            "_token": csrf_token,
            "level": level,
            "eidbYearChwe": year,
            "eidbReportChwe": value_code,
            "eidbChapterEx": chapter,
        }
        # For 4, 6, 8 digit levels, we need to pass the full HS code
        if level != "2" and hs_code != "all":
            payload["hscode"] = hs_code
    else:
        # Import field names
        payload = {
            "_token": csrf_token,
            "level": level,
            "eidbcwacoimpYear": year,
            "eidbcwacoimpddReportVal": value_code,
            "eidbcwacoimpddChapter": chapter,
        }
        if level != "2" and hs_code != "all":
            payload["hscode"] = hs_code
    
    response = session.post(url, data=payload)
    response.raise_for_status()
    
    return response.text
