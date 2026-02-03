"""
Commodity-wise all countries scraper.
Scrapes export/import data for a specific HSN code across all countries.
"""

from typing import Optional

# URL path for commodity-wise all countries reports
EXPORT_PATH = "/eidb/commodity_wise_all_countries_export"
IMPORT_PATH = "/eidb/commodity_wise_all_countries_import"


def scrape_commodity_export(
    session,
    base_url: str,
    hsn: str,
    year: str,
    state: dict
) -> Optional[str]:
    """
    Scrape commodity-wise export data for an HSN code across all countries.

    Args:
        session: requests.Session object
        base_url: Base URL of tradestat website
        hsn: HSN code (e.g., "27101944")
        year: Financial year (e.g., "2024")
        state: Dictionary containing CSRF token

    Returns:
        HTML response as string, or None if request fails
    """
    payload = {
        "_token": state["_token"],
        "Eidbhscode_cmace": hsn,
        "EidbYear_cmace": year,
        "EidbReport_cmace": "2",  # 2 = Export
    }

    print(f"[*] Scraping export: HSN={hsn}, YEAR={year}")

    try:
        resp = session.post(base_url + EXPORT_PATH, data=payload, timeout=60)
        resp.raise_for_status()
        print(f"[+] Export scrape successful: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        print(f"[!] Export scrape failed: {e}")
        return None


def scrape_commodity_import(
    session,
    base_url: str,
    hsn: str,
    year: str,
    state: dict
) -> Optional[str]:
    """
    Scrape commodity-wise import data for an HSN code across all countries.

    Args:
        session: requests.Session object
        base_url: Base URL of tradestat website
        hsn: HSN code (e.g., "27101944")
        year: Financial year (e.g., "2024")
        state: Dictionary containing CSRF token

    Returns:
        HTML response as string, or None if request fails
    """
    payload = {
        "_token": state["_token"],
        "Eidbhscode_cmace": hsn,
        "EidbYear_cmace": year,
        "EidbReport_cmace": "1",  # 1 = Import
    }

    print(f"[*] Scraping import: HSN={hsn}, YEAR={year}")

    try:
        resp = session.post(base_url + EXPORT_PATH, data=payload, timeout=60)
        resp.raise_for_status()
        print(f"[+] Import scrape successful: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        print(f"[!] Import scrape failed: {e}")
        return None
