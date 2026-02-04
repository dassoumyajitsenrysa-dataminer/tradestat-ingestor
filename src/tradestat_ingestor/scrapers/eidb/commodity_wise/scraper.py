"""
Commodity-wise data scraper.
Scrapes commodity data for a specific HS code and financial year.
"""

from loguru import logger
from typing import Optional

# URL paths for commodity-wise reports
COMMODITY_WISE_EXPORT_PATH = "/eidb/commodity_wise_export"
COMMODITY_WISE_IMPORT_PATH = "/eidb/commodity_wise_import"


def scrape_commodity_wise(
    session,
    base_url: str,
    hscode: str,
    year: str,
    trade_type: str = "export",
    value_type: str = "usd",
    state: dict = None
) -> Optional[str]:
    """
    Scrape commodity-wise data for an HS code.

    Args:
        session: requests.Session object with CSRF token support
        base_url: Base URL of tradestat website
        hscode: HS code (2, 4, 6, or 8 digit)
        year: Financial year (e.g., "2024" for 2024-2025)
        trade_type: "export" or "import"
        value_type: "usd" (US $ Million), "inr" (₹ Crore), or "quantity"
        state: Dictionary containing CSRF token and other auth state

    Returns:
        HTML response as string, or None if request fails
    """
    # Determine the URL path based on trade type
    if trade_type.lower() == "export":
        path = COMMODITY_WISE_EXPORT_PATH
    elif trade_type.lower() == "import":
        path = COMMODITY_WISE_IMPORT_PATH
    else:
        logger.error(f"Invalid trade_type: {trade_type}. Must be 'export' or 'import'")
        return None

    # Map value_type to form value
    value_map = {
        "usd": "2",      # US $ Million
        "inr": "1",      # ₹ Crore
        "quantity": "3"  # Quantity (only for 8-digit)
    }
    
    report_value = value_map.get(value_type.lower(), "2")
    
    # Validate: quantity only available at 8-digit level
    if value_type.lower() == "quantity" and len(hscode) != 8:
        logger.error(f"Quantity data is only available at 8-digit level. Got {len(hscode)}-digit code: {hscode}")
        return None

    # Build payload for specific HS code
    # When using specific HS code, we set the radio button to "specific"
    # and provide the HS code in the text field
    # Note: Export uses "Cwe" suffix, Import uses "Cwi" suffix
    if trade_type.lower() == "export":
        payload = {
            "_token": state["_token"],
            "EidbYearCwe": year,
            "comType": "specific",
            "commodityType": "specific",
            "EidbComLevelCwe": str(len(hscode)),
            "Eidb_hscodeCwe": hscode,
            "Eidb_ReportCwe": report_value,
        }
    else:  # import
        payload = {
            "_token": state["_token"],
            "Eidb_YearCwi": year,
            "commodityType": "specific",
            "Eidb_ComLevelCwi": str(len(hscode)),
            "Eidb_hscodeCwi": hscode,
            "Eidb_ReportCwi": report_value,
        }

    logger.info(f"Scraping commodity-wise {trade_type}: HS={hscode}, YEAR={year}, VALUE_TYPE={value_type}")

    try:
        resp = session.post(
            base_url + path,
            data=payload,
            timeout=60,
        )
        resp.raise_for_status()
        logger.success(f"Commodity-wise {trade_type} scrape successful: HS={hscode}, YEAR={year}")
        return resp.text
    except Exception as e:
        logger.error(f"Commodity-wise {trade_type} scrape failed: HS={hscode}, YEAR={year}, Error: {e}")
        return None


def scrape_commodity_wise_all(
    session,
    base_url: str,
    digit_level: int,
    year: str,
    trade_type: str = "export",
    value_type: str = "usd",
    state: dict = None
) -> Optional[str]:
    """
    Scrape all commodities at a specific digit level.

    Args:
        session: requests.Session object with CSRF token support
        base_url: Base URL of tradestat website
        digit_level: HS code level (2, 4, 6, or 8)
        year: Financial year (e.g., "2024" for 2024-2025)
        trade_type: "export" or "import"
        value_type: "usd" (US $ Million), "inr" (₹ Crore), or "quantity"
        state: Dictionary containing CSRF token and other auth state

    Returns:
        HTML response as string, or None if request fails
    """
    if digit_level not in [2, 4, 6, 8]:
        logger.error(f"Invalid digit_level: {digit_level}. Must be 2, 4, 6, or 8")
        return None
        
    # Validate: quantity only available at 8-digit level
    if value_type.lower() == "quantity" and digit_level != 8:
        logger.error(f"Quantity data is only available at 8-digit level. Got {digit_level}-digit level")
        return None

    # Determine the URL path based on trade type
    if trade_type.lower() == "export":
        path = COMMODITY_WISE_EXPORT_PATH
    elif trade_type.lower() == "import":
        path = COMMODITY_WISE_IMPORT_PATH
    else:
        logger.error(f"Invalid trade_type: {trade_type}. Must be 'export' or 'import'")
        return None

    # Map value_type to form value
    value_map = {
        "usd": "2",
        "inr": "1",
        "quantity": "3"
    }
    report_value = value_map.get(value_type.lower(), "2")

    # Build payload for all commodities at digit level
    # Note: Export uses "Cwe" suffix, Import uses "Cwi" suffix
    if trade_type.lower() == "export":
        payload = {
            "_token": state["_token"],
            "EidbYearCwe": year,
            "comType": "all",
            "EidbComLevelCwe": str(digit_level),
            "Eidb_ReportCwe": report_value,
        }
    else:  # import
        payload = {
            "_token": state["_token"],
            "Eidb_YearCwi": year,
            "commodityType": "all",
            "Eidb_ComLevelCwi": str(digit_level),
            "Eidb_ReportCwi": report_value,
        }

    logger.info(f"Scraping all commodities at {digit_level}-digit level: {trade_type}, YEAR={year}")

    try:
        resp = session.post(
            base_url + path,
            data=payload,
            timeout=120,  # Longer timeout for all commodities
        )
        resp.raise_for_status()
        logger.success(f"All commodities scrape successful: {digit_level}-digit, YEAR={year}")
        return resp.text
    except Exception as e:
        logger.error(f"All commodities scrape failed: {digit_level}-digit, YEAR={year}, Error: {e}")
        return None
