"""Scraper module for EIDB Region-wise data."""

import requests
from loguru import logger
from typing import Optional

EXPORT_PATH = "/eidb/region_wise_export"
IMPORT_PATH = "/eidb/region_wise_import"
VALUE_TYPES = {"usd": "2", "inr": "1", "quantity": "3"}


def fetch_region_data(
    session: requests.Session,
    base_url: str,
    hscode: str,
    year: str,
    trade_type: str,
    value_type: str,
    state: dict
) -> Optional[str]:
    """Fetch region-wise data for a specific HS code."""
    path = EXPORT_PATH if trade_type.lower() == "export" else IMPORT_PATH
    
    payload = {
        "_token": state["_token"],
        "EidbHscode": hscode,
        "EidbYear": year,
        "Eidb_Report": VALUE_TYPES.get(value_type.lower(), "2"),
    }
    
    logger.info(f"Fetching region-wise: HS={hscode}, YEAR={year}")
    
    try:
        resp = session.post(base_url + path, data=payload, timeout=60)
        resp.raise_for_status()
        logger.success(f"Region-wise fetch successful: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        logger.error(f"Region-wise fetch failed: {e}")
        return None
