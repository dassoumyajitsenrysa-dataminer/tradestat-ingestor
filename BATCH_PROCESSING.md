# TradeStat Ingestor - Batch Processing Guide

## Overview

For processing 11,000+ HSN codes efficiently, this project uses **Redis Queue (RQ)** for distributed job processing. Each HSN code is submitted as a background job that scrapes all 7 years (2018-2024), consolidates the data, and exports a single JSON file.

## Architecture

```
HSN Codes CSV File
       |
       v
   CLI: batch-submit
       |
       v
   Load HSN Codes
       |
       v
   Submit to Redis Queue (background jobs)
       |
       +-> Worker 1: scrape_all_years() -> merge_years -> save_export()
       +-> Worker 2: scrape_all_years() -> merge_years -> save_export()
       +-> Worker N: scrape_all_years() -> merge_years -> save_export()
       |
       v
   Output: data/raw/export/{HSN}/{HSN}_export.json (7 years consolidated)
```

## Prerequisites

1. **Redis Server** - Must be running on localhost:6379 (or configured in settings)
   - Windows: Install Redis from https://github.com/microsoftarchive/redis/releases or use WSL
   - Linux/Mac: `brew install redis` or `apt install redis-server`

2. **Environment Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -e .
   ```

3. **Redis URL** - Configured in `.env`
   ```
   REDIS_URL=redis://localhost:6379/0
   ```

## Step-by-Step Usage

### 1. Prepare HSN Codes File

Place your HSN codes file in `data/input/` directory. Two formats supported:

**Format A: One HSN per line (TXT)** - Recommended (`data/input/hsn_codes.txt`)
```
09011112
09021010
09031001
```

**Format B: CSV with header** (`data/input/hsn_codes.csv`)
```csv
hsn_code,description
09011112,Fresh or Dried Spice
09021010,Cinnamon
09031001,Cloves
```

Use the provided sample: `data/input/hsn_codes_sample.txt`

### 2. Start Redis Server

```bash
# Windows (WSL)
wsl redis-server

# Linux/Mac
redis-server

# Or check if running
redis-cli ping  # Should return "PONG"
```

### 3. Start RQ Workers

In a separate terminal:

```bash
# Start a single worker (processes 1 job at a time)
python scripts/rq_worker.py

# To start multiple workers (parallel processing)
# Terminal 1:
python scripts/rq_worker.py

# Terminal 2:
python scripts/rq_worker.py

# Terminal 3:
python scripts/rq_worker.py
```

Each worker processes one job at a time. With N workers, you process N HSN codes in parallel.

### 4. Submit Batch Jobs

```bash
# Submit all HSN codes to the queue
tradestat-ingest batch-submit --file data/input/hsn_codes_sample.txt

# Output:
# Loaded 14 HSN codes
# Submitting to Redis Queue...
# ============================================================
# Batch submission completed
# ============================================================
# Submitted: 14
# Failed: 0
```

### 5. Monitor Progress

**Check Queue Status** (real-time):
```bash
tradestat-ingest queue-status

# Output:
# ============================================================
# Queue Status
# ============================================================
# Jobs queued: 8
# 
# Queued jobs:
#   09011112: queued (ID: a1b2c3d4...)
#   09021010: started (ID: e5f6g7h8...)
```

**Get Batch Results** (completed jobs):
```bash
tradestat-ingest batch-results

# Output:
# ============================================================
# Batch Processing Results
# ============================================================
# Total HSN codes: 14
# Completed: 6
# Pending: 8
# 
# Completion Statistics:
#   Total countries scraped: 1428
#   Avg countries per HSN: 238.0
# 
# First 10 completed HSNs:
#   09011112: 7 years, 234 countries
#   09021010: 7 years, 247 countries
```

## Processing Timeline Estimation

**Performance Metrics:**
- Single HSN: ~15-30 seconds (7 years × ~30 countries = 210 requests)
- Total requests per HSN: ~210 (7 years × ~30 countries)
- Network I/O bound: Limited by server rate limits (~2-5 requests/sec)

**For 11,000 HSN codes:**
- Single worker: 11,000 × 25 sec = ~3 days
- 10 workers in parallel: ~7-8 hours
- 50 workers: ~2 hours

**Recommended Setup:**
```
Scenario 1 (Small Server):
- 4 workers
- Processing time: ~30 hours (1.25 days)

Scenario 2 (Medium Server):
- 10 workers
- Processing time: ~8 hours

Scenario 3 (High Availability):
- 20+ workers distributed across multiple machines
- Processing time: ~2-3 hours
```

## Output Structure

After batch processing, you'll have:

```
data/raw/export/
├── 09011112/
│   ├── 2024.json          (individual year data)
│   ├── 2023.json
│   ├── ...
│   └── 09011112_export.json  (consolidated - 7 years)
├── 09021010/
│   ├── 2024.json
│   └── 09021010_export.json
└── ...
```

Each `{HSN}_export.json` contains all 7 years consolidated:

```json
{
  "hsn_code": "09011112",
  "description": "Fresh or Dried Spice",
  "years": {
    "2024": {
      "financial_year": "2024",
      "commodity": "Fresh or Dried Spice",
      "unit": "Kg",
      "countries": [...],
      "metadata": {
        "scraped_at": "2024-01-15T10:30:00",
        "source_url": "..."
      }
    },
    "2023": {...},
    ...
  }
}
```

## Troubleshooting

### Problem: "ConnectionError: Error -2 connecting to localhost:6379"
- **Solution**: Start Redis server: `redis-server` (or `wsl redis-server` on Windows)

### Problem: Jobs stay in "queued" state
- **Solution**: Ensure workers are running: `python scripts/rq_worker.py`
- Check: `redis-cli` → `LLEN tradestat-ingestor:queue` (should decrease as jobs process)

### Problem: Worker crashes with "ConnectionRefused"
- **Solution**: Check target website availability and network connectivity
- Monitor: `tradestat-ingest queue-status` for failed jobs

### Problem: Batch submission fails with "No HSN codes loaded"
- **Solution**: Check CSV/TXT file format - ensure `hsn_code` column or one code per line

### Problem: Rate limiting from target server (503 errors)
- **Solution**: Add delays in `core/scraper.py`: `time.sleep(0.5)` between requests
- Or reduce worker count to 5-10 workers

## Advanced Configuration

### Multi-Machine Setup

**Machine 1 (Queue Server):**
```bash
# Just run Redis
redis-server --port 6379
```

**Machine 2-5 (Workers):**
```bash
# Point to remote Redis
export REDIS_URL=redis://machine1-ip:6379/0
python scripts/rq_worker.py
```

### Resume Interrupted Processing

Failed jobs remain in queue automatically. Run:
```bash
tradestat-ingest queue-status    # Check what's pending
python scripts/rq_worker.py       # Resume processing
```

## Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `scrape` | Single HSN + year | `tradestat-ingest scrape --hsn 09011112 --year 2024` |
| `scrape-years` | Single HSN, all years | `tradestat-ingest scrape-years --hsn 09011112` |
| `export-data` | Consolidate HSN into export file | `tradestat-ingest export-data --hsn 09011112` |
| `batch-submit` | Submit CSV of HSN codes | `tradestat-ingest batch-submit --file hsn_codes.csv` |
| `queue-status` | Check current queue state | `tradestat-ingest queue-status` |
| `batch-results` | Show completed jobs | `tradestat-ingest batch-results` |

## Monitoring & Logging

Worker logs appear in the worker terminal:
```
15:30:45 - tradestat_ingestor.tasks.jobs - INFO - Processing HSN: 09011112
15:30:45 - tradestat_ingestor.tasks.batch_scraper - INFO - Scraping 2024...
15:30:48 - tradestat_ingestor.tasks.batch_scraper - INFO - Scraping 2023...
...
15:31:10 - tradestat_ingestor.tasks.jobs - INFO - Consolidated export saved
```

For persistent logging, modify `rq_worker.py` to add file logging:
```python
import logging
logging.basicConfig(
    filename='logs/worker.log',
    level=logging.INFO
)
```

## Performance Optimization

1. **Increase Worker Count**: More workers = faster parallel processing
2. **Add Request Caching**: Avoid re-scraping same URLs
3. **Implement Checkpointing**: Save progress every 100 HSN codes
4. **Monitor Rate Limiting**: Add exponential backoff for 429/503 responses

## Next Steps

- [ ] Create full list of 11,000 HSN codes
- [ ] Prepare CSV file with all HSN codes  
- [ ] Set up Redis on production machine
- [ ] Deploy RQ workers (containerized if needed)
- [ ] Schedule batch runs (e.g., weekly updates)
- [ ] Set up monitoring dashboard for job progress
