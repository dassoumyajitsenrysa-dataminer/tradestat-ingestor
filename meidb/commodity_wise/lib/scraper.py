"""Scraper for MEIDB Commodity-wise data."""

import requests
from loguru import logger
from typing import Optional

EXPORT_PATH = "/meidb/commoditywise_export"
IMPORT_PATH = "/meidb/commoditywise_import"

VALUE_TYPES = {"usd": "1", "inr": "2", "quantity": "3"}
YEAR_TYPES = {"financial": "1", "calendar": "2"}
MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
          7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}


def fetch_commodity_data(
    session: requests.Session,
    base_url: str,
    hscode: str,
    month: int,
    year: int,
    trade_type: str,
    value_type: str,
    year_type: str,
    state: dict
) -> Optional[str]:
    path = EXPORT_PATH if trade_type.lower() == "export" else IMPORT_PATH
    
    # Build payload based on trade type
    if trade_type.lower() == "export":
        payload = {
            "_token": state["_token"],
            "ddMonth": str(month),
            "ddYear": str(year),
            "comlev": "specific",
            "comval": hscode,
            "ddCommodityLevel": str(len(hscode)),
            "ddReportVal": VALUE_TYPES.get(value_type.lower(), "1"),
            "ddReportYear": YEAR_TYPES.get(year_type.lower(), "1"),
        }
    else:
        payload = {
            "_token": state["_token"],
            "imddMonth": str(month),
            "imddYear": str(year),
            "comlev": "specific",
            "comval": hscode,
            "imddCommodityLevel": str(len(hscode)),
            "imddReportVal": VALUE_TYPES.get(value_type.lower(), "1"),
            "imddReportYear": YEAR_TYPES.get(year_type.lower(), "1"),
        }
    
    logger.info(f"Fetching: HS={hscode}, MONTH={MONTHS.get(month)}/{year}")
    
    try:
        resp = session.post(base_url + path, data=payload, timeout=60)
        resp.raise_for_status()
        logger.success(f"Fetch successful: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return None
