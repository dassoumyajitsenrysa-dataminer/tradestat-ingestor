"""
Batch scraping job for multiple HSN codes using Redis Queue.
"""
from loguru import logger
from datetime import datetime
from tradestat_ingestor.tasks.batch_scraper import scrape_all_years
from tradestat_ingestor.storage.export import save_consolidated_export
from tradestat_ingestor.storage.git import push_file_to_git
from tradestat_ingestor.config.settings import settings


def process_hsn_code(hsn: str, trade: str = "export") -> dict:
    """
    Background job to scrape and consolidate data for a single HSN code.
    Called by RQ worker.
    Saves only consolidated export (no individual year files).
    """
    logger.info(f"[JOB] Processing HSN={hsn}")
    
    try:
        # Step 1: Scrape all years in parallel
        logger.info(f"[JOB] Step 1: Scraping years for HSN={hsn}")
        scrape_results = scrape_all_years(hsn, trade)
        
        if not scrape_results["successful"]:
            logger.warning(f"[JOB] No successful scrapes for HSN={hsn}")
            return {
                "hsn": hsn,
                "status": "failed",
                "reason": "No data scraped successfully"
            }
        
        # Step 2: Build consolidated structure from scraped data
        logger.info(f"[JOB] Step 2: Consolidating data for HSN={hsn}")
        consolidated_data = scrape_results["consolidated_data"]
        
        # Add metadata
        consolidated_data["metadata"] = {
            "consolidated_at": datetime.utcnow().isoformat(),
            "trade_type": trade,
            "years_count": len(scrape_results["successful"]),
            "schema_version": "2.0"
        }
        
        # Step 3: Save consolidated export directly
        logger.info(f"[JOB] Step 3: Saving consolidated export for HSN={hsn}")
        
        # Use save_consolidated_export to handle the save
        final_export_file = save_consolidated_export(trade, hsn, consolidated_data)
        
        # Count total countries across all years
        total_countries = sum(
            len(consolidated_data["years"].get(year, {}).get("countries", []))
            for year in consolidated_data.get("years", {})
        )
        
        # Push to Git if enabled
        if settings.git_enabled and settings.git_repo_url:
            logger.info(f"[JOB] Step 4: Pushing to Git for HSN={hsn}")
            git_pushed = push_file_to_git(str(final_export_file), trade, hsn)
            if git_pushed:
                logger.success(f"[JOB] Pushed to Git: {hsn}")
            else:
                logger.warning(f"[JOB] Failed to push to Git: {hsn}")
        
        logger.success(f"[JOB] Completed HSN={hsn}")
        return {
            "hsn": hsn,
            "status": "success",
            "years_scraped": len(consolidated_data.get("years", {})),
            "export_file": str(final_export_file),
            "total_countries": total_countries,
            "git_pushed": settings.git_enabled and settings.git_repo_url
        }
        
    except Exception as e:
        logger.error(f"[JOB] Error processing HSN={hsn}: {str(e)}")
        return {
            "hsn": hsn,
            "status": "failed",
            "reason": str(e)
        }
