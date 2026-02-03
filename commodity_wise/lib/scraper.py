"""
Commodity-wise data scraper.
Scrapes commodity data for a specific HS code and financial year.
"""

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
        session: requests.Session object
        base_url: Base URL of tradestat website
        hscode: HS code (2, 4, 6, or 8 digit)
        year: Financial year (e.g., "2024" for 2024-2025)
        trade_type: "export" or "import"
        value_type: "usd" (US $ Million), "inr" (₹ Crore), or "quantity"
        state: Dictionary containing CSRF token

    Returns:
        HTML response as string, or None if request fails
    """
    # Determine URL path
    if trade_type.lower() == "export":
        path = COMMODITY_WISE_EXPORT_PATH
    elif trade_type.lower() == "import":
        path = COMMODITY_WISE_IMPORT_PATH
    else:
        print(f"[!] Invalid trade_type: {trade_type}")
        return None

    # Map value_type to form value
    value_map = {"usd": "2", "inr": "1", "quantity": "3"}
    report_value = value_map.get(value_type.lower(), "2")
    
    # Validate quantity
    if value_type.lower() == "quantity" and len(hscode) != 8:
        print(f"[!] Quantity only available at 8-digit level")
        return None

    # Build payload (different field names for export vs import)
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
    else:
        payload = {
            "_token": state["_token"],
            "Eidb_YearCwi": year,
            "commodityType": "specific",
            "Eidb_ComLevelCwi": str(len(hscode)),
            "Eidb_hscodeCwi": hscode,
            "Eidb_ReportCwi": report_value,
        }

    print(f"[*] Scraping {trade_type}: HS={hscode}, YEAR={year}, VALUE={value_type}")

    try:
        resp = session.post(base_url + path, data=payload, timeout=60)
        resp.raise_for_status()
        print(f"[+] Scrape successful: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        print(f"[!] Scrape failed: {e}")
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
    """
    if digit_level not in [2, 4, 6, 8]:
        print(f"[!] Invalid digit_level: {digit_level}")
        return None
        
    if value_type.lower() == "quantity" and digit_level != 8:
        print(f"[!] Quantity only available at 8-digit level")
        return None

    if trade_type.lower() == "export":
        path = COMMODITY_WISE_EXPORT_PATH
    elif trade_type.lower() == "import":
        path = COMMODITY_WISE_IMPORT_PATH
    else:
        print(f"[!] Invalid trade_type: {trade_type}")
        return None

    value_map = {"usd": "2", "inr": "1", "quantity": "3"}
    report_value = value_map.get(value_type.lower(), "2")

    if trade_type.lower() == "export":
        payload = {
            "_token": state["_token"],
            "EidbYearCwe": year,
            "comType": "all",
            "EidbComLevelCwe": str(digit_level),
            "Eidb_ReportCwe": report_value,
        }
    else:
        payload = {
            "_token": state["_token"],
            "Eidb_YearCwi": year,
            "commodityType": "all",
            "Eidb_ComLevelCwi": str(digit_level),
            "Eidb_ReportCwi": report_value,
        }

    print(f"[*] Scraping all {digit_level}-digit commodities: {trade_type}, YEAR={year}")

    try:
        resp = session.post(base_url + path, data=payload, timeout=120)
        resp.raise_for_status()
        print(f"[+] Scrape successful: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        print(f"[!] Scrape failed: {e}")
        return None
