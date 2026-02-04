"""
MEIDB Commodity-wise scraper: fetches monthly data for all/specific HS codes at 2/4/6/8 digit levels.
"""

from loguru import logger
from typing import Optional

# URL paths for MEIDB commodity-wise reports
COMMODITY_WISE_EXPORT_PATH = "/meidb/commoditywise_export"
COMMODITY_WISE_IMPORT_PATH = "/meidb/commoditywise_import"

# Full URLs (for backward compatibility)
EXPORT_URL = "https://tradestat.commerce.gov.in/meidb/commoditywise_export"
IMPORT_URL = "https://tradestat.commerce.gov.in/meidb/commoditywise_import"

EXPORT_FIELDS = {
    'month': 'ddMonth',
    'year': 'ddYear',
    'hs_level': 'ddCommodityLevel',
    'value_type': 'ddReportVal',
    'year_type': 'ddReportYear',
}
IMPORT_FIELDS = {
    'month': 'imddMonth',
    'year': 'imddYear',
    'hs_level': 'imddCommodityLevel',
    'value_type': 'imddReportVal',
    'year_type': 'imddReportYear',
}

# Month mapping
MONTHS = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


def scrape_meidb_commodity_wise(
    session,
    base_url: str,
    hscode: str,
    month: int,
    year: int,
    trade_type: str = "export",
    value_type: str = "usd",
    year_type: str = "financial",
    state: dict = None
) -> Optional[str]:
    """
    Scrape monthly commodity-wise data for a specific HS code from MEIDB.

    Args:
        session: requests.Session object with CSRF token support
        base_url: Base URL of tradestat website
        hscode: HS code (2, 4, 6, or 8 digit)
        month: Month (1-12)
        year: Year (e.g., 2024, 2025)
        trade_type: "export" or "import"
        value_type: "usd" (US $ Million), "inr" (₹ Crore), or "quantity"
        year_type: "financial" or "calendar"
        state: Dictionary containing CSRF token and other auth state

    Returns:
        HTML response as string, or None if request fails
    """
    # Validate month
    if month < 1 or month > 12:
        logger.error(f"Invalid month: {month}. Must be 1-12")
        return None

    # Determine the URL path based on trade type
    if trade_type.lower() == "export":
        path = COMMODITY_WISE_EXPORT_PATH
        fields = EXPORT_FIELDS
    elif trade_type.lower() == "import":
        path = COMMODITY_WISE_IMPORT_PATH
        fields = IMPORT_FIELDS
    else:
        logger.error(f"Invalid trade_type: {trade_type}. Must be 'export' or 'import'")
        return None

    # Map value_type to form value
    value_map = {
        "usd": "1",      # US $ Million
        "inr": "2",      # ₹ Crore
        "quantity": "3"  # Quantity
    }
    report_value = value_map.get(value_type.lower(), "1")

    # Map year_type to form value
    year_type_map = {
        "financial": "1",
        "calendar": "2"
    }
    report_year = year_type_map.get(year_type.lower(), "1")

    # Validate: quantity only available at 8-digit level
    if value_type.lower() == "quantity" and len(hscode) != 8:
        logger.error(f"Quantity data is only available at 8-digit level. Got {len(hscode)}-digit code: {hscode}")
        return None

    # Build payload for specific HS code
    payload = {
        "_token": state["_token"],
        fields['month']: str(month),
        fields['year']: str(year),
        "comlev": "specific",
        fields['hs_level']: str(len(hscode)),
        "comval": hscode,
        fields['value_type']: report_value,
        fields['year_type']: report_year,
    }

    month_name = MONTHS.get(month, str(month))
    logger.info(f"Scraping MEIDB commodity-wise {trade_type}: HS={hscode}, MONTH={month_name} {year}, VALUE_TYPE={value_type}")

    try:
        resp = session.post(
            base_url + path,
            data=payload,
            timeout=60,
        )
        resp.raise_for_status()
        logger.success(f"MEIDB commodity-wise {trade_type} scrape successful: HS={hscode}, MONTH={month_name} {year}")
        return resp.text
    except Exception as e:
        logger.error(f"MEIDB commodity-wise {trade_type} scrape failed: HS={hscode}, MONTH={month_name} {year}, Error: {e}")
        return None


def scrape_meidb_commodity_wise_all(
    session,
    base_url: str,
    digit_level: int,
    month: int,
    year: int,
    trade_type: str = "export",
    value_type: str = "usd",
    year_type: str = "financial",
    state: dict = None
) -> Optional[str]:
    """
    Scrape all commodities at a specific digit level from MEIDB (monthly).

    Args:
        session: requests.Session object with CSRF token support
        base_url: Base URL of tradestat website
        digit_level: HS code level (2, 4, 6, or 8)
        month: Month (1-12)
        year: Year (e.g., 2024, 2025)
        trade_type: "export" or "import"
        value_type: "usd" (US $ Million), "inr" (₹ Crore), or "quantity"
        year_type: "financial" or "calendar"
        state: Dictionary containing CSRF token and other auth state

    Returns:
        HTML response as string, or None if request fails
    """
    # Validate digit level
    if digit_level not in [2, 4, 6, 8]:
        logger.error(f"Invalid digit_level: {digit_level}. Must be 2, 4, 6, or 8")
        return None

    # Validate month
    if month < 1 or month > 12:
        logger.error(f"Invalid month: {month}. Must be 1-12")
        return None

    # Validate: quantity only available at 8-digit level
    if value_type.lower() == "quantity" and digit_level != 8:
        logger.error(f"Quantity data is only available at 8-digit level. Got {digit_level}-digit level")
        return None

    # Determine the URL path based on trade type
    if trade_type.lower() == "export":
        path = COMMODITY_WISE_EXPORT_PATH
        fields = EXPORT_FIELDS
    elif trade_type.lower() == "import":
        path = COMMODITY_WISE_IMPORT_PATH
        fields = IMPORT_FIELDS
    else:
        logger.error(f"Invalid trade_type: {trade_type}. Must be 'export' or 'import'")
        return None

    # Map value_type to form value
    value_map = {
        "usd": "1",
        "inr": "2",
        "quantity": "3"
    }
    report_value = value_map.get(value_type.lower(), "1")

    # Map year_type to form value
    year_type_map = {
        "financial": "1",
        "calendar": "2"
    }
    report_year = year_type_map.get(year_type.lower(), "1")

    # Build payload for all commodities at digit level
    payload = {
        "_token": state["_token"],
        fields['month']: str(month),
        fields['year']: str(year),
        "comlev": "all",
        fields['hs_level']: str(digit_level),
        fields['value_type']: report_value,
        fields['year_type']: report_year,
    }

    month_name = MONTHS.get(month, str(month))
    logger.info(f"Scraping all MEIDB commodities at {digit_level}-digit level: {trade_type}, MONTH={month_name} {year}")

    try:
        resp = session.post(
            base_url + path,
            data=payload,
            timeout=120,  # Longer timeout for all commodities
        )
        resp.raise_for_status()
        logger.success(f"MEIDB all commodities scrape successful: {digit_level}-digit, MONTH={month_name} {year}")
        return resp.text
    except Exception as e:
        logger.error(f"MEIDB all commodities scrape failed: {digit_level}-digit, MONTH={month_name} {year}, Error: {e}")
        return None


# Legacy function for backward compatibility
def fetch_commodity_wise_data(session, csrf_token, trade_type, month, year, hs_level, value_type, year_type, comlev='all', comval=None):
    """
    Fetch commodity-wise data (monthly) from MEIDB.
    trade_type: 'export' or 'import'
    month: 1-12
    year: 2018-2025
    hs_level: 2, 4, 6, 8
    value_type: 1=USD, 2=INR, 3=Quantity
    year_type: 1=Financial, 2=Calendar
    comlev: 'all' or 'specific'
    comval: HS code (if specific)
    """
    if trade_type == 'export':
        url = EXPORT_URL
        fields = EXPORT_FIELDS
    else:
        url = IMPORT_URL
        fields = IMPORT_FIELDS
    
    data = {
        '_token': csrf_token,
        fields['month']: str(month),
        fields['year']: str(year),
        'comlev': comlev,
        fields['hs_level']: str(hs_level),
        fields['value_type']: str(value_type),
        fields['year_type']: str(year_type),
    }
    if comlev == 'specific' and comval:
        data['comval'] = str(comval)
    
    resp = session.post(url, data=data)
    resp.raise_for_status()
    return resp.text
