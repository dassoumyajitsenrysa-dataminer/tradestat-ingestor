"""Scraper for EIDB Region-wise All Commodities data."""

import requests
from loguru import logger
from typing import Optional

EXPORT_PATH = "/eidb/region_wise_all_commodities_export"
IMPORT_PATH = "/eidb/region_wise_all_commodities_import"
VALUE_TYPES = {"usd": "2", "inr": "1", "quantity": "3"}


def fetch_region_commodities_data(
    session: requests.Session,
    base_url: str,
    country_code: str,
    year: str,
    digit_level: int,
    trade_type: str,
    value_type: str,
    state: dict
) -> Optional[str]:
    path = EXPORT_PATH if trade_type.lower() == "export" else IMPORT_PATH
    
    payload = {
        "_token": state["_token"],
        "EidbCountry": country_code,
        "EidbYear": year,
        "EidbComLevel": str(digit_level),
        "Eidb_Report": VALUE_TYPES.get(value_type.lower(), "2"),
    }
    
    logger.info(f"Fetching: COUNTRY={country_code}, YEAR={year}, LEVEL={digit_level}")
    
    try:
        resp = session.post(base_url + path, data=payload, timeout=120)
        resp.raise_for_status()
        logger.success(f"Fetch successful: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return None
