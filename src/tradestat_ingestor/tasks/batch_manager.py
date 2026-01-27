"""
Batch queue management for scraping multiple HSN codes.
"""
from pathlib import Path
from typing import List
import csv
from loguru import logger
from redis import Redis
from rq import Queue
from rq.job import JobStatus
from tradestat_ingestor.tasks.jobs import process_hsn_code
from tradestat_ingestor.config.settings import settings


def load_hsn_codes_from_file(file_path: str) -> List[str]:
    """
    Load HSN codes from a CSV file.
    Expected format: one HSN code per line or CSV with 'hsn_code' column.
    """
    hsn_codes = []
    file = Path(file_path)
    
    if not file.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    try:
        with open(file, "r", encoding="utf-8") as f:
            # Try CSV format first
            reader = csv.DictReader(f)
            for row in reader:
                if "hsn_code" in row or "hsn" in row:
                    hsn = row.get("hsn_code") or row.get("hsn")
                    if hsn and hsn.strip():
                        hsn_codes.append(hsn.strip())
        
        # If no CSV rows found, try simple line format
        if not hsn_codes:
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    hsn = line.strip()
                    if hsn and not hsn.startswith("#"):  # Skip comments
                        hsn_codes.append(hsn)
        
        logger.info(f"Loaded {len(hsn_codes)} HSN codes from {file_path}")
        return hsn_codes
        
    except Exception as e:
        logger.error(f"Error loading HSN codes: {str(e)}")
        return []


def submit_batch_jobs(hsn_codes: List[str], trade: str = "export") -> dict:
    """
    Submit multiple scraping jobs to Redis Queue.
    """
    redis_conn = Redis.from_url(settings.redis_url)
    queue = Queue(connection=redis_conn)
    
    results = {
        "submitted": [],
        "failed": [],
    }
    
    logger.info(f"Submitting {len(hsn_codes)} jobs to queue")
    
    for hsn in hsn_codes:
        try:
            job = queue.enqueue(
                process_hsn_code,
                hsn=hsn,
                trade=trade,
                job_timeout=600,  # 10 minutes per job
            )
            results["submitted"].append({
                "hsn": hsn,
                "job_id": job.id,
                "status": job.get_status()
            })
            logger.info(f"Submitted job for HSN={hsn}, Job ID={job.id}")
        except Exception as e:
            logger.error(f"Failed to submit job for HSN={hsn}: {str(e)}")
            results["failed"].append({
                "hsn": hsn,
                "reason": str(e)
            })
    
    return results


def get_queue_status() -> dict:
    """
    Get current status of Redis Queue.
    """
    redis_conn = Redis.from_url(settings.redis_url)
    queue = Queue(connection=redis_conn)
    
    status = {
        "queued": len(queue),
        "jobs": {}
    }
    
    # Get all jobs in queue
    for job_id in queue.job_ids:
        try:
            job = queue.fetch_job(job_id)
            if job:
                status["jobs"][job_id] = {
                    "status": job.get_status(),
                    "hsn": job.args[0] if job.args else "unknown",
                }
        except:
            pass
    
    return status


def get_batch_results(trade: str = "export") -> dict:
    """
    Scan for completed export files and their stats.
    """
    from tradestat_ingestor.config.settings import settings
    import json
    
    base_dir = Path(settings.raw_data_dir) / trade.lower()
    
    results = {
        "total_hsn": 0,
        "completed": [],
        "pending": [],
    }
    
    if not base_dir.exists():
        return results
    
    # Find all HSN directories
    for hsn_dir in base_dir.iterdir():
        if hsn_dir.is_dir():
            hsn = hsn_dir.name
            export_file = hsn_dir / f"{hsn}_export.json"
            
            if export_file.exists():
                try:
                    with open(export_file) as f:
                        data = json.load(f)
                    results["completed"].append({
                        "hsn": hsn,
                        "years": data["metadata"]["years_count"],
                        "countries": sum(len(y["countries"]) for y in data["years"].values()),
                    })
                except:
                    pass
            else:
                results["pending"].append(hsn)
            
            results["total_hsn"] += 1
    
    return results
