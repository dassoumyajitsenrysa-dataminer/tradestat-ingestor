"""
Region-wise all commodities scraper for TradeStat.
Fetches export/import data by region with commodity breakdown at different HS code levels.
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

# Region code mapping (main regions + sub-regions)
REGIONS = {
    # Main regions
    "1": "Europe",
    "2": "Africa",
    "3": "America",
    "4": "Asia",
    "5": "CIS & Baltics",
    "9": "Unspecified Region",
    
    # Europe sub-regions
    "111": "EU Countries",
    "112": "European Free Trade Association (EFTA)",
    "120": "Other European Countries",
    
    # Africa sub-regions
    "210": "Southern African Customs Union (SACU)",
    "211": "Other South African Countries",
    "220": "West Africa",
    "230": "Central Africa",
    "240": "East Africa",
    "250": "North Africa",
    
    # America sub-regions
    "310": "North America",
    "320": "Latin America",
    
    # Asia sub-regions
    "410": "East Asia (Oceania)",
    "420": "ASEAN",
    "430": "West Asia - GCC",
    "431": "Other West Asia",
    "440": "NE Asia",
    "450": "South Asia",
    
    # CIS & Baltics sub-regions
    "510": "CARs Countries",
    "520": "Other CIS Countries",
    "530": "Baltics Countries",
    
    # Unspecified
    "999": "Unspecified",
}


def get_base_url(trade_type: str) -> str:
    """Get the base URL for the given trade type."""
    if trade_type == "export":
        return "https://tradestat.commerce.gov.in/eidb/region_wise_all_commodities_export"
    else:
        return "https://tradestat.commerce.gov.in/eidb/region_wise_all_commodities_import"


def fetch_region_commodities_data(
    session: requests.Session,
    csrf_token: str,
    trade_type: str,
    year: str,
    region_code: str = "1",
    hs_level: str = "2",
    value_type: str = "usd"
) -> str:
    """
    Fetch region-wise commodities data for a specific year and region.
    
    Args:
        session: Requests session with cookies
        csrf_token: CSRF token for the request
        trade_type: "export" or "import"
        year: Year code (e.g., "2024")
        region_code: Region code (e.g., "1" for Europe, "420" for ASEAN)
        hs_level: HS code level ("2", "4", "6", "8")
        value_type: "usd", "inr", or "qty"
        
    Returns:
        HTML response text
    """
    url = get_base_url(trade_type)
    value_code = VALUE_TYPES.get(value_type, "2")
    
    # Validate HS level
    if hs_level not in HS_LEVELS:
        hs_level = "2"
    
    # Build payload based on trade type
    # Export: eidbRwacmeYear, eidbRwacmereg, eidbRwacmeLevel, eidbRwacmeReport
    # Import: eidbRwacmiYear, eidbRwacmireg, eidbRwacmiLevel, eidbRwacmiReport
    if trade_type == "export":
        payload = {
            "_token": csrf_token,
            "eidbRwacmeYear": year,
            "eidbRwacmereg": region_code,
            "eidbRwacmeLevel": hs_level,
            "eidbRwacmeReport": value_code,
        }
    else:
        # Import field names
        payload = {
            "_token": csrf_token,
            "eidbRwacmiYear": year,
            "eidbRwacmireg": region_code,
            "eidbRwacmiLevel": hs_level,
            "eidbRwacmiReport": value_code,
        }
    
    response = session.post(url, data=payload)
    response.raise_for_status()
    
    return response.text


def get_region_name(code: str) -> str:
    """Get region name from code."""
    return REGIONS.get(code, f"Unknown ({code})")


def get_main_regions() -> dict:
    """Get only main regions (single digit codes)."""
    return {k: v for k, v in REGIONS.items() if len(k) == 1}


def get_sub_regions(main_region_code: str) -> dict:
    """Get sub-regions for a main region."""
    # Sub-regions start with the main region code
    return {k: v for k, v in REGIONS.items() if len(k) > 1 and k.startswith(main_region_code)}
