"""
MEIDB Commodity-wise All Countries scraper.
Fetches monthly data for a specific HS code across all countries.
"""

from loguru import logger
from typing import Optional

# URL paths for MEIDB commodity-wise all countries reports
EXPORT_PATH = "/meidb/commodity_wise_all_countries_export"
IMPORT_PATH = "/meidb/commodity_wise_all_countries_import"

# Form field names differ between export and import
# Export uses 'cwacex' prefix, Import uses 'cwacim' prefix
EXPORT_FIELDS = {
    'hscode': 'cwacexHSCODE',
    'month': 'cwacexMonth',
    'year': 'cwacexYear',
    'value_type': 'cwacexReportVal',
    'year_type': 'cwacexReportYear',
}

IMPORT_FIELDS = {
    'hscode': 'cwacimHSCODE',
    'month': 'cwacimMonth',
    'year': 'cwacimYear',
    'value_type': 'cwacimReportVal',
    'year_type': 'cwacimReportYear',
}

# Month mapping
MONTHS = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


def scrape_meidb_commodity_wise_all_countries(
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
    Scrape monthly commodity-wise data for a specific HS code across all countries from MEIDB.

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

    # Determine the URL path and fields based on trade type
    if trade_type.lower() == "export":
        path = EXPORT_PATH
        fields = EXPORT_FIELDS
    elif trade_type.lower() == "import":
        path = IMPORT_PATH
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

    # Build payload
    payload = {
        "_token": state["_token"],
        fields['hscode']: hscode,
        fields['month']: str(month),
        fields['year']: str(year),
        fields['value_type']: report_value,
        fields['year_type']: report_year,
    }

    month_name = MONTHS.get(month, str(month))
    logger.info(f"Scraping MEIDB commodity-wise all countries {trade_type}: HS={hscode}, MONTH={month_name} {year}, VALUE_TYPE={value_type}")

    try:
        resp = session.post(
            base_url + path,
            data=payload,
            timeout=120,  # Longer timeout for country data
        )
        resp.raise_for_status()
        logger.success(f"MEIDB commodity-wise all countries {trade_type} scrape successful: HS={hscode}, MONTH={month_name} {year}")
        return resp.text
    except Exception as e:
        logger.error(f"MEIDB commodity-wise all countries {trade_type} scrape failed: HS={hscode}, MONTH={month_name} {year}, Error: {e}")
        return None
