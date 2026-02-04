"""
Region-wise scraper for TradeStat.
Fetches export/import data by region.
"""

import requests


# Region code mapping
REGIONS = {
    "all": "All",
    "1": "Europe",
    "2": "Africa",
    "3": "America",
    "4": "Asia",
    "5": "CIS & Baltics",
    "9": "Unspecified Region",
}

# Available years
AVAILABLE_YEARS = ["2024", "2023", "2022", "2021", "2020", "2019", "2018"]

# Value type mapping
VALUE_TYPES = {
    "usd": "2",  # US $ Million
    "inr": "1",  # ₹ Crore
}


def get_base_url(trade_type: str) -> str:
    """Get the base URL for the given trade type."""
    if trade_type == "export":
        return "https://tradestat.commerce.gov.in/eidb/region_wise_export"
    else:
        return "https://tradestat.commerce.gov.in/eidb/region_wise_import"


def fetch_region_data(
    session: requests.Session,
    csrf_token: str,
    trade_type: str,
    year: str,
    region_code: str = "all",
    value_type: str = "usd"
) -> str:
    """
    Fetch region-wise data for a specific year and region.
    
    Args:
        session: Requests session with cookies
        csrf_token: CSRF token for the request
        trade_type: "export" or "import"
        year: Year code (e.g., "2024")
        region_code: Region code or "all"
        value_type: "usd" or "inr"
        
    Returns:
        HTML response text
    """
    url = get_base_url(trade_type)
    value_code = VALUE_TYPES.get(value_type, "2")
    
    # Build payload based on trade type
    # Export: eidbYearRwe, eidbrwexp_regid, eidbReportRwe
    # Import: eidbrwimpddYear, eidbrwimp_regid, eidbrwimpddReportVal
    if trade_type == "export":
        payload = {
            "_token": csrf_token,
            "eidbYearRwe": year,
            "eidbrwexp_regid": region_code,
            "eidbReportRwe": value_code,
        }
    else:
        payload = {
            "_token": csrf_token,
            "eidbrwimpddYear": year,
            "eidbrwimp_regid": region_code,
            "eidbrwimpddReportVal": value_code,
        }
    
    response = session.post(url, data=payload)
    response.raise_for_status()
    
    return response.text


def get_region_name(code: str) -> str:
    """Get region name from code."""
    return REGIONS.get(code, f"Unknown ({code})")
