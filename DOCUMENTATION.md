# TradeSTAT Ingestor - Complete Documentation

## Project Overview

**TradeSTAT Ingestor** is a high-performance web scraper for downloading trade data (export and import) from India's EIDB (Economic Intelligence Data Bank) system. It scrapes **11,185+ HSN (Harmonized System of Nomenclature) codes** across **7 years (2018-2024)** in parallel, consolidating the data into JSON format for analysis.

### Key Achievements
- ✅ Scraped **11,185 HSN codes** for export data
- ✅ Scraped **11,185 HSN codes** for import data
- ✅ **22,370+ consolidated JSON files** created
- ✅ Data with **7-year history** per HSN code
- ✅ Processing time: **~30-40 minutes** with 30 concurrent workers
- ✅ All data pushed to GitHub for version control

---

## Architecture

### Technology Stack
- **Language**: Python 3.10+
- **Web Framework**: Requests + BeautifulSoup4
- **Queue System**: Redis Queue (RQ)
- **Task Runner**: RQ Workers (30 concurrent)
- **Data Format**: JSON (consolidated)
- **Environment**: WSL (Windows Subsystem for Linux)
- **Version Control**: Git

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Batch Processing Pipeline                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input: HSN Codes List (11,185 codes)                      │
│        ↓                                                     │
│  Queue Manager: Submit jobs to Redis Queue                 │
│        ↓                                                     │
│  30 RQ Workers (in parallel)                               │
│    ├─ Worker 1 ──┐                                          │
│    ├─ Worker 2 ──┤                                          │
│    ├─ Worker 3 ──┤                                          │
│    └─ Worker 30 ─┤                                          │
│                  ↓                                           │
│  Per-HSN Job Pipeline:                                      │
│    1. Scrape 7 years in parallel (ThreadPoolExecutor)      │
│    2. Parse HTML tables → Extract country data             │
│    3. Consolidate 7 years into single JSON                 │
│    4. Save to data/raw/{export|import}/{HSN}/              │
│    5. Push to Git (optional)                               │
│                  ↓                                           │
│  Output: JSON files (one per HSN code)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. **Session Management** (`core/session.py`)
- Bootstraps HTTP session with Laravel CSRF token
- Reuses session for multiple requests

#### 2. **Scrapers** (`core/scraper.py`)
- `scrape_export()`: Fetches export data via POST
- `scrape_import()`: Fetches import data via POST
- Both use same endpoint with different report flags

#### 3. **Parser** (`core/parser.py`)
- Parses HTML tables into structured data
- Extracts: country names, quantities, values
- Metadata: commodity details, dates

#### 4. **Batch Scraper** (`tasks/batch_scraper.py`)
- `scrape_all_years()`: Parallelizes 7 years using ThreadPoolExecutor
- Per-HSN time: **~4 seconds** (vs 25 seconds sequential)
- Returns consolidated data structure

#### 5. **Background Jobs** (`tasks/jobs.py`)
- RQ job handler: orchestrates full pipeline
- Steps: scrape → consolidate → save → git push

#### 6. **Storage** (`storage/export.py`)
- `get_export_dir()`: Routes to correct directory (export/import)
- `save_consolidated_export()`: Saves JSON with metadata

#### 7. **Batch Manager** (`tasks/batch_manager.py`)
- `submit_batch_jobs()`: Loads HSN codes, queues jobs
- `get_queue_status()`: Checks remaining jobs

---

## Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/tradestat-ingestor.git
cd tradestat-ingestor
```

### 2. Configure Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup in WSL (Optional but Recommended for Performance)
```bash
# Install WSL if not present
wsl --install -d Ubuntu

# Inside WSL:
python3 -m venv ~/tradestat-venv
source ~/tradestat-venv/bin/activate
pip install -r requirements.txt

# Install and start Redis
sudo apt-get install redis-server
redis-server &
```

### 4. Create HSN Codes File
```bash
# Create file with one HSN code per line
cat > data/input/hsn_codes.txt << EOF
01012100
01012910
01012990
...
EOF
```

---

## Usage & Commands

### Step 1: Start Redis Server
```bash
# Windows (WSL)
wsl -e redis-server

# Or in WSL terminal
redis-server
```

### Step 2: Test Single HSN (Export)
```bash
tradestat-ingest scrape-years --hsn 01012100
```

**Output:**
```
2026-01-27 12:00:00 | SUCCESS | Scraped 7 years for HSN=01012100
Files created:
  - data/raw/export/01012100/01012100_export.json
```

### Step 3: Submit Batch Jobs
```bash
# Submit export batch
tradestat-ingest batch-submit --file data/input/hsn_codes.txt --trade export

# Output:
# ============================================================
# Batch submission completed
# ============================================================
# Submitted: 11185
# Failed: 0
```

### Step 4: Start Workers (30 concurrent)
```bash
# Kill any existing workers first
wsl -e pkill -9 -f "rq_worker.py"

# Start 30 workers
wsl -e bash -c "for i in {1..30}; do (cd /mnt/c/Users/dassa/Desktop/tradestat-ingestor && source ~/tradestat-venv/bin/activate && python3 scripts/rq_worker.py) & done; wait"
```

### Step 5: Monitor Progress
```bash
# Check queue length
redis-cli LLEN "rq:queue:default"

# Count completed export files
(Get-ChildItem c:\Users\dassa\Desktop\tradestat-ingestor\src\data\raw\export -Recurse -Filter "*_export.json" | Measure-Object).Count

# Count completed import files
(Get-ChildItem c:\Users\dassa\Desktop\tradestat-ingestor\src\data\raw\import -Recurse -Filter "*_import.json" | Measure-Object).Count
```

### Step 6: Submit Import Batch (After Exports Finish)
```bash
tradestat-ingest batch-submit --file data/input/hsn_codes.txt --trade import
```

### Step 7: Commit & Push to GitHub
```bash
cd c:\Users\dassa\Desktop\tradestat-ingestor

# Stage all data
git add src/data/

# Commit
git commit -m "Add all trade data - export and import complete (11,185 HSN codes, 7 years each)"

# Push
git push origin master
```

---

## Process Flow (Detailed)

### Complete Workflow

```
USER INPUT
    ↓
[HSN Codes File: data/input/hsn_codes.txt]
    ↓
1. BATCH SUBMISSION
   └─ tradestat-ingest batch-submit --file data/input/hsn_codes.txt --trade export
      └─ Loads 11,185 HSN codes
      └─ Creates 11,185 RQ jobs
      └─ Jobs queued in Redis
    ↓
2. WORKER PROCESSING (30 workers in parallel)
   └─ Worker picks job from queue
   └─ For each HSN:
      ├─ Step 1: Scrape 7 years in parallel
      │  ├─ Year 2018 ──┐
      │  ├─ Year 2019 ──┤
      │  ├─ Year 2020 ──┤ (ThreadPoolExecutor)
      │  ├─ Year 2021 ──┤ ~4 seconds total
      │  ├─ Year 2022 ──┤
      │  ├─ Year 2023 ──┤
      │  └─ Year 2024 ──┘
      ├─ Step 2: Parse HTML tables
      │  └─ Extract countries, quantities, values
      ├─ Step 3: Consolidate 7 years
      │  └─ Create single data structure
      ├─ Step 4: Save to JSON
      │  └─ src/data/raw/export/{HSN}/{HSN}_export.json
      └─ Step 5: Push to Git (optional)
    ↓
3. OUTPUT GENERATION
   └─ 11,185 consolidated JSON files
   └─ Each file: ~10-100 KB
   └─ Total: ~500+ MB of data
    ↓
4. VERSION CONTROL
   └─ git add src/data/
   └─ git commit -m "..."
   └─ git push origin master
    ↓
COMPLETION ✅
```

---

## Data Structure

### Output JSON Format
```json
{
  "metadata": {
    "consolidated_at": "2026-01-27T02:51:30.123456",
    "trade_type": "export",
    "years_count": 7,
    "schema_version": "2.0",
    "source_url": "https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_export"
  },
  "commodity": {
    "hsn_code": "01012100",
    "description": "Live horses"
  },
  "years": {
    "2024": {
      "report_date": "2024-12-31",
      "scraped_at": "2026-01-27T02:45:23",
      "countries": [
        {
          "name": "Afghanistan",
          "quantity": 15000,
          "unit": "No",
          "value": 1500000,
          "unit_price": 100
        },
        ...
      ],
      "totals": {
        "total_quantity": 150000,
        "total_value": 15000000
      }
    },
    ...
  }
}
```

### File Organization
```
src/data/raw/
├── export/
│   ├── 01012100/
│   │   └── 01012100_export.json (7 years consolidated)
│   ├── 01012910/
│   │   └── 01012910_export.json
│   └── ...
├── import/
│   ├── 01012100/
│   │   └── 01012100_import.json (7 years consolidated)
│   ├── 01012910/
│   │   └── 01012910_import.json
│   └── ...
```

---

## Performance Metrics

### Speed Optimization
| Metric | Value |
|--------|-------|
| Years per HSN | 7 |
| Parallelization | ThreadPoolExecutor (7 threads) |
| Time per HSN | ~4 seconds (parallel) |
| Time per HSN | ~25 seconds (sequential) |
| Speedup | **6.25x** |

### Throughput
| Scenario | Time | Jobs |
|----------|------|------|
| 1 worker | ~12 hours | 11,185 export |
| 20 workers | ~1-2 hours | 11,185 export + import |
| 30 workers | ~25-30 min | 11,185 export + import |

### Resource Usage
- **Memory**: ~200-300 MB per worker
- **CPU**: Multi-threaded parallel scraping
- **Network**: HTTP/HTTPS requests (with rate limiting via CSRF token)
- **Storage**: ~500+ MB for all 22,370 JSON files

---

## Troubleshooting

### Issue: "Permission denied: '/eidb'"
**Cause**: File path confusion (website URL vs file system path)
**Solution**: 
```python
# Ensure constants.py has proper DATA_ROOT
DATA_ROOT = Path(__file__).parent.parent.parent / "data"
EXPORT_DATA_DIR = DATA_ROOT / "raw" / "export"
```

### Issue: "500 Server Error" on Import
**Cause**: Wrong endpoint or payload format for import
**Solution**:
- Import uses same endpoint as export
- Payload flag: `"EidbReport_cmace": "1"` for import, `"2"` for export

### Issue: Queue not processing jobs
**Cause**: Redis not running or workers crashed
**Solution**:
```bash
# Check Redis
redis-cli PING  # Should return PONG

# Check queue
redis-cli LLEN "rq:queue:default"

# Restart workers
wsl -e pkill -9 -f "rq_worker.py"
wsl -e bash -c "for i in {1..30}; do (cd /path && python3 scripts/rq_worker.py) & done"
```

### Issue: Git push fails
**Cause**: Remote URL not configured or credentials missing
**Solution**:
```bash
# Check remote
git remote -v

# Add/update remote
git remote set-url origin https://github.com/yourusername/repo.git

# Configure credentials (one-time)
git config --global user.email "your@email.com"
git config --global user.name "Your Name"
```

---

## Advanced Configuration

### Environment Variables (.env)
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
GIT_ENABLED=true
GIT_REPO_URL=https://github.com/yourusername/tradestat-data.git
GIT_BRANCH=master
```

### Worker Configuration
- **Max workers**: Limited by system memory (30 recommended)
- **Timeout**: 60 seconds per HTTP request
- **Retries**: Automatic via RQ
- **Job expiration**: 500 seconds

### Rate Limiting
- CSRF token bootstrapped per scrape thread
- Natural rate limiting via HTTP request flow
- No artificial delays needed (website not blocking)

---

## Maintenance & Updates

### Adding New HSN Codes
```bash
echo "new_hsn_code" >> data/input/hsn_codes.txt
tradestat-ingest batch-submit --file data/input/hsn_codes.txt --trade export
```

### Updating to New Year's Data
```bash
# Website adds 2025 data in Oct 2025
# Code auto-adapts: years are discovered dynamically
# Just re-run batch jobs with existing HSN codes
```

### Backup Data
```bash
# Backup to external drive
robocopy src\data\raw E:\Backups\tradestat-backup /MIR

# Or create archive
tar -czf tradestat-backup-$(date +%Y%m%d).tar.gz src/data/raw/
```

---

## Summary

| Task | Command | Time |
|------|---------|------|
| Setup | `pip install -r requirements.txt` | 2 min |
| Test Single | `tradestat-ingest scrape-years --hsn 01012100` | 10 sec |
| Submit Batch | `tradestat-ingest batch-submit --file data/input/hsn_codes.txt --trade export` | 1 min |
| Process (30 workers) | Workers auto-process from queue | 20-30 min |
| Push to GitHub | `git add src/data/ && git commit && git push` | 5 min |
| **Total Time** | | **~40 minutes** |

---

## Contact & Support

For issues, questions, or improvements:
1. Check logs in `logs/` directory
2. Review troubleshooting section above
3. Check Redis queue status: `redis-cli`
4. Monitor worker output in terminal

---

**Project Status**: ✅ Production Ready  
**Last Updated**: 2026-01-27  
**Data Coverage**: 11,185 HSN codes × 7 years (2018-2024) × 2 trade types (export/import)  
**Total Records**: 22,370+ consolidated JSON files
