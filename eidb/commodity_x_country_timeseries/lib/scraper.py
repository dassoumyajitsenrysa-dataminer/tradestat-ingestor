"""Scraper module for EIDB Commodity x Country Timeseries data."""

import requests
from loguru import logger
from typing import Optional

EXPORT_PATH = "/eidb/commodity_country_timeseries_export"
IMPORT_PATH = "/eidb/commodity_country_timeseries_import"

VALUE_TYPES = {"usd": "2", "inr": "1", "quantity": "3"}


def fetch_timeseries_data(
    session: requests.Session,
    base_url: str,
    hscode: str,
    country_code: str,
    from_year: str,
    to_year: str,
    trade_type: str,
    value_type: str,
    state: dict
) -> Optional[str]:
    """Fetch commodity x country timeseries data from EIDB."""
    path = EXPORT_PATH if trade_type.lower() == "export" else IMPORT_PATH
    report_value = VALUE_TYPES.get(value_type.lower(), "2")
    
    payload = {
        "_token": state["_token"],
        "EidbHscode": hscode,
        "EidbCountry": country_code,
        "EidbFromYear": from_year,
        "EidbToYear": to_year,
        "Eidb_Report": report_value,
    }
    
    logger.info(f"Fetching timeseries: HS={hscode}, COUNTRY={country_code}, {from_year}-{to_year}")
    
    try:
        resp = session.post(base_url + path, data=payload, timeout=60)
        resp.raise_for_status()
        logger.success(f"Timeseries fetch successful: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        logger.error(f"Timeseries fetch failed: {e}")
        return None
