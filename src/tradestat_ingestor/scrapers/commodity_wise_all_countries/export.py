"""
Commodity-wise export data scraper.
Scrapes export data for a specific HSN code and financial year.
"""

from loguru import logger
from typing import Optional


def scrape_commodity_export(
    session,
    base_url: str,
    hsn: str,
    year: str,
    state: dict
) -> Optional[str]:
    """
    Scrape commodity-wise export data for an HSN code.

    Args:
        session: requests.Session object with CSRF token support
        base_url: Base URL of tradestat website
        hsn: HSN code (e.g., "09011112")
        year: Financial year (e.g., "2024")
        state: Dictionary containing CSRF token and other auth state

    Returns:
        HTML response as string, or None if request fails
    """
    from tradestat_ingestor.utils.constants import EXPORT_PATH

    payload = {
        "_token": state["_token"],
        "Eidbhscode_cmace": hsn,
        "EidbYear_cmace": year,
        "EidbReport_cmace": "2",  # 2 = Export
    }

    logger.info(f"Scraping export: HSN={hsn}, YEAR={year}")

    try:
        resp = session.post(
            base_url + EXPORT_PATH,
            data=payload,
            timeout=60,
        )
        resp.raise_for_status()
        logger.success(f"Export scrape successful: HSN={hsn}, YEAR={year}")
        return resp.text
    except Exception as e:
        logger.error(f"Export scrape failed: HSN={hsn}, YEAR={year}, Error: {e}")
        return None
