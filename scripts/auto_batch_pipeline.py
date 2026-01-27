#!/usr/bin/env python3
"""
Automatically submit import batch after export batch completes.
Monitors Redis queue and submits next batch when current completes.
"""
import redis
import time
import subprocess
import sys
from pathlib import Path
from loguru import logger

# Setup logging
log_file = Path(__file__).parent.parent / "logs" / "auto_batch.log"
log_file.parent.mkdir(exist_ok=True)
logger.add(str(log_file), rotation="500 MB")

def check_queue_status():
    """Check how many jobs are in the queue."""
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        queue_len = r.llen("rq:queue:default")
        return queue_len
    except Exception as e:
        logger.error(f"Redis error: {e}")
        return None

def submit_batch(trade_type):
    """Submit batch using CLI command."""
    try:
        hsn_file = Path(__file__).parent.parent / "hsn_codes.txt"
        if not hsn_file.exists():
            logger.error(f"HSN file not found: {hsn_file}")
            return False
        
        cmd = f"tradestat-ingest batch-submit --file {hsn_file} --trade {trade_type}"
        logger.info(f"Submitting {trade_type} batch: {cmd}")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.success(f"✅ {trade_type.upper()} batch submitted successfully")
            logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"❌ Failed to submit {trade_type} batch")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error submitting batch: {e}")
        return False

def monitor_and_submit():
    """Monitor export batch, then submit import batch."""
    logger.info("🚀 Starting auto batch pipeline monitor")
    logger.info("📊 Monitoring export jobs...")
    
    check_count = 0
    last_queue_len = check_queue_status()
    
    while True:
        queue_len = check_queue_status()
        
        if queue_len is None:
            logger.warning("⚠️  Unable to connect to Redis, retrying...")
            time.sleep(10)
            continue
        
        check_count += 1
        
        # Log every 10 checks (every ~50 seconds)
        if check_count % 10 == 0:
            logger.info(f"📈 Queue status: {queue_len} jobs remaining")
        
        # Export batch complete - submit import batch
        if queue_len == 0 and last_queue_len > 0:
            logger.success("✅ EXPORT BATCH COMPLETE!")
            logger.info("⏳ Waiting 5 seconds before submitting import batch...")
            time.sleep(5)
            
            # Verify queue is still empty (no other jobs added)
            queue_len = check_queue_status()
            if queue_len == 0:
                logger.info("📤 Submitting IMPORT batch...")
                if submit_batch("import"):
                    logger.success("✅ IMPORT batch queued successfully!")
                    logger.info("👷 Workers will now process import jobs...")
                    return True
                else:
                    logger.error("❌ Failed to submit import batch")
                    return False
        
        last_queue_len = queue_len
        time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    try:
        monitor_and_submit()
    except KeyboardInterrupt:
        logger.info("⏹️  Pipeline monitor stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
