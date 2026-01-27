from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from tradestat_ingestor.core.session import TradeStatSession
from tradestat_ingestor.core.scraper import scrape_export, scrape_import
from tradestat_ingestor.core.parser import parse_commodity_from_html
from tradestat_ingestor.config.settings import settings
from tradestat_ingestor.utils.constants import EXPORT_PATH


AVAILABLE_YEARS = ["2024", "2023", "2022", "2021", "2020", "2019", "2018"]


def _scrape_single_year(hsn: str, year: str, trade: str = "export") -> dict:
    """
    Scrape a single year for an HSN code.
    Called in parallel by ThreadPoolExecutor.
    Supports both export and import data.
    Returns parsed data without saving individual year files.
    """
    try:
        logger.info(f"Scraping HSN={hsn}, YEAR={year}, TYPE={trade}")
        
        # Create a new session for this thread
        session = TradeStatSession(
            base_url=settings.base_url,
            user_agent=settings.user_agent,
        )
        state = session.bootstrap(EXPORT_PATH)
        
        # Scrape based on trade type
        if trade.lower() == "import":
            html = scrape_import(session.session, settings.base_url, hsn, year, state)
        else:
            html = scrape_export(session.session, settings.base_url, hsn, year, state)
        
        # Parse
        parsed_data = parse_commodity_from_html(html, hsn=hsn, year=year)
        
        # Check if we got valid data
        if not parsed_data.get("countries"):
            logger.warning(f"No countries data found for HSN={hsn}, YEAR={year}")
            return {
                "year": year,
                "success": False,
                "reason": "No data found in response",
                "parsed_data": None
            }
        
        # Return parsed data without saving individual year files
        logger.success(f"Completed HSN={hsn}, YEAR={year}, TYPE={trade}")
        return {
            "year": year,
            "success": True,
            "countries_count": len(parsed_data.get("countries", [])),
            "parsed_data": parsed_data
        }
        
    except Exception as e:
        logger.error(f"Failed to scrape HSN={hsn}, YEAR={year}: {str(e)}")
        return {
            "year": year,
            "success": False,
            "reason": str(e),
            "parsed_data": None
        }


def scrape_all_years(hsn: str, trade: str = "export"):
    """
    Scrape data for all available years in parallel.
    Supports both export and import data.
    Handles missing years gracefully.
    Returns consolidated data structure (no individual year files saved).
    Uses ThreadPoolExecutor to scrape 7 years simultaneously.
    """
    results = {
        "commodity_hsn": hsn,
        "trade_type": trade,
        "successful": [],
        "failed": [],
        "consolidated_data": {
            "hsn_code": hsn,
            "years": {}
        }
    }
    
    # Scrape all years in parallel (7 threads, one per year)
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {
            executor.submit(_scrape_single_year, hsn, year, trade): year 
            for year in AVAILABLE_YEARS
        }
        
        for future in as_completed(futures):
            result = future.result()
            
            if result["success"]:
                results["successful"].append({
                    "year": result["year"],
                    "countries_count": result["countries_count"],
                })
                # Collect parsed data for consolidation
                results["consolidated_data"]["years"][result["year"]] = result["parsed_data"]
            else:
                results["failed"].append({
                    "year": result["year"],
                    "reason": result["reason"]
                })
    
    return results
