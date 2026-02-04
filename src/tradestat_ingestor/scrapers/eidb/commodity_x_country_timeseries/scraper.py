"""
Commodity x Country-wise scraper for TradeStat.
Fetches export/import data for a specific HS code and country.
"""

import requests


# Available years
AVAILABLE_YEARS = ["2024", "2023", "2022", "2021", "2020", "2019", "2018"]

# Value type mapping
VALUE_TYPES = {
    "usd": "2",    # US $ Million
    "inr": "1",    # ₹ Crore
}

# Country code mapping (major countries - full list in HTML)
COUNTRIES = {
    "1": "AFGHANISTAN",
    "17": "AUSTRALIA",
    "27": "BANGLADESH PR",
    "33": "BELGIUM",
    "43": "BRAZIL",
    "59": "CANADA",
    "77": "CHINA P RP",
    "129": "FRANCE",
    "147": "GERMANY",
    "179": "HONG KONG",
    "187": "INDONESIA",
    "189": "IRAN",
    "191": "IRAQ",
    "193": "IRELAND",
    "197": "ITALY",
    "205": "JAPAN",
    "217": "KOREA RP",
    "219": "KUWAIT",
    "245": "MALAYSIA",
    "259": "MEXICO",
    "273": "NEPAL",
    "275": "NETHERLAND",
    "285": "NEW ZEALAND",
    "291": "NIGERIA",
    "297": "NORWAY",
    "301": "OMAN",
    "309": "PAKISTAN IR",
    "323": "PHILIPPINES",
    "325": "POLAND",
    "335": "QATAR",
    "344": "RUSSIA",
    "351": "SAUDI ARAB",
    "359": "SINGAPORE",
    "365": "SOUTH AFRICA",
    "367": "SPAIN",
    "369": "SRI LANKA DSR",
    "387": "SWEDEN",
    "389": "SWITZERLAND",
    "397": "THAILAND",
    "405": "TRINIDAD",
    "407": "TUNISIA",
    "409": "TURKEY",
    "419": "U ARAB EMTS",
    "421": "U K",
    "423": "U S A",
    "437": "VIETNAM SOC REP",
    "999": "Trade to Unspecified Countries",
    "599": "UNSPECIFIED",
}


def get_base_url(trade_type: str) -> str:
    """Get the base URL for the given trade type."""
    if trade_type == "export":
        return "https://tradestat.commerce.gov.in/eidb/commodityx_countries_wise_export"
    else:
        return "https://tradestat.commerce.gov.in/eidb/commodityx_countries_wise_import"


def fetch_commodity_country_data(
    session: requests.Session,
    csrf_token: str,
    trade_type: str,
    hs_code: str,
    year: str,
    country_code: str,
    value_type: str = "usd"
) -> str:
    """
    Fetch commodity x country data for a specific HS code and country.
    
    Args:
        session: Requests session with cookies
        csrf_token: CSRF token for the request
        trade_type: "export" or "import"
        hs_code: HS code (2, 4, 6, or 8 digits)
        year: Year code (e.g., "2024") - determines which 5-year range to show
        country_code: Country code (e.g., "423" for USA)
        value_type: "usd" or "inr"
        
    Returns:
        HTML response text
    """
    url = get_base_url(trade_type)
    value_code = VALUE_TYPES.get(value_type, "2")
    
    # Build payload based on trade type
    # Export: searchTerm, ContEidbey, ContEidbe, ReportEidbe
    # Import: searchTerm, ContEidbyi, ContEidbi, ReportEidbi
    if trade_type == "export":
        payload = {
            "_token": csrf_token,
            "searchTerm": hs_code,
            "ContEidbey": year,
            "ContEidbe": country_code,
            "ReportEidbe": value_code,
        }
    else:
        # Import field names
        payload = {
            "_token": csrf_token,
            "searchTerm": hs_code,
            "ContEidbyi": year,
            "ContEidbi": country_code,
            "ReportEidbi": value_code,
        }
    
    response = session.post(url, data=payload)
    response.raise_for_status()
    
    return response.text


def get_country_name(code: str) -> str:
    """Get country name from code."""
    return COUNTRIES.get(code, f"Unknown ({code})")
