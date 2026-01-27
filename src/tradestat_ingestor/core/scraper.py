from loguru import logger
from tradestat_ingestor.utils.constants import EXPORT_PATH
from tradestat_ingestor.utils.import_config import IMPORT_PATH

def scrape_export(session, base_url: str, hsn: str, year: str, state: dict) -> str:
    payload = {
        "_token": state["_token"],
        "Eidbhscode_cmace": hsn,
        "EidbYear_cmace": year,
        "EidbReport_cmace": "2",  # US$ Million
    }

    logger.info(f"Submitting export scrape: HSN={hsn}, YEAR={year}")

    resp = session.post(
        base_url + EXPORT_PATH,
        data=payload,
        timeout=60,
    )
    resp.raise_for_status()

    return resp.text


def scrape_import(session, base_url: str, hsn: str, year: str, state: dict) -> str:
    """
    Scrape import data for HSN code.
    Uses export endpoint but with report flag = "1" for import data.
    """
    payload = {
        "_token": state["_token"],
        "Eidbhscode_cmace": hsn,
        "EidbYear_cmace": year,
        "EidbReport_cmace": "1",  # 1 = Import, 2 = Export
    }

    logger.info(f"Submitting import scrape: HSN={hsn}, YEAR={year}")

    resp = session.post(
        base_url + EXPORT_PATH,  # Use export endpoint with import flag
        data=payload,
        timeout=60,
    )
    resp.raise_for_status()

    return resp.text
