#!/usr/bin/env python3
"""
RQ Worker script for processing batch jobs (Windows compatible).
Usage: python scripts/rq_worker.py
Note: On Windows, RQ has limitations. Consider using WSL for production.
"""

import sys
import platform
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from redis import Redis
from rq import Worker, Queue
from tradestat_ingestor.config.settings import settings

if __name__ == "__main__":
    # Check if running on Windows
    if platform.system() == "Windows":
        print("WARNING: Running RQ worker on Windows has limitations.")
        print("For production, consider running workers in WSL or Docker.")
        print("\nStarting worker in compatibility mode...\n")
    
    # Connect to Redis
    redis_conn = Redis.from_url(settings.redis_url)
    q = Queue(connection=redis_conn)
    
    print(f"Redis URL: {settings.redis_url}")
    print(f"Queue: {q.name}")
    print("Waiting for jobs...\n")
    
    try:
        # Create worker
        worker = Worker([q], connection=redis_conn)
        
        # Work with Windows-compatible settings
        worker.work(
            with_scheduler=False,
            max_jobs=None,
            logging_level="INFO"
        )
    except Exception as e:
        print(f"Error: {e}")
        if "fork" in str(e).lower():
            print("\nRQ requires Unix/Linux for proper operation.")
            print("Please run this worker in WSL:")
            print("  wsl")
            print("  cd /mnt/c/Users/dassa/Desktop/tradestat-ingestor")
            print("  python scripts/rq_worker.py")
