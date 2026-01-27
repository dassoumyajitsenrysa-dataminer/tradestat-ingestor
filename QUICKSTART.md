# Quick Start: Batch Processing 11,000+ HSN Codes

## TL;DR Setup (5 minutes)

### 1. Install & Configure
```bash
# Install
pip install -e .

# Create .env
echo 'REDIS_URL=redis://localhost:6379/0' > .env
echo 'BASE_URL=https://tradestat.gov.in' >> .env
```

### 2. Start Redis
```bash
# Windows (WSL) or Linux
redis-server

# Or verify it's running
redis-cli ping  # Should print: PONG
```

### 3. Prepare Your HSN Codes
```bash
# Create data/input/hsn_codes.txt with one HSN code per line:
# 09011112
# 09021010
# 09031001
# ... (add your 11,000 codes)

# Or use the sample:
cp data/input/hsn_codes_sample.txt data/input/hsn_codes.txt
```

### 4. Start Processing
```bash
# Terminal 1: Start 4 workers (processes 4 jobs in parallel)
python scripts/rq_worker.py &
python scripts/rq_worker.py &
python scripts/rq_worker.py &
python scripts/rq_worker.py &

# Terminal 2: Monitor progress
watch -n 5 'tradestat-ingest queue-status'

# Terminal 3: Monitor results
watch -n 10 'tradestat-ingest batch-results'
```

### 5. Submit All HSN Codes
```bash
tradestat-ingest batch-submit --file data/input/hsn_codes.txt
```

Done! Processing will run in the background. With 4 workers:
- 11,000 codes × 25 sec per code ÷ 4 workers = **~76 hours** (3 days)
- Add more workers for faster processing

## CLI Commands

```bash
# Single HSN + year (quick test)
tradestat-ingest scrape --hsn 09011112 --year 2024

# Single HSN + all years (consolidate)
tradestat-ingest scrape-years --hsn 09011112

# Export to single JSON file
tradestat-ingest export-data --hsn 09011112

# Submit batch from CSV
tradestat-ingest batch-submit --file hsn_codes.csv

# Check queue
tradestat-ingest queue-status

# See results
tradestat-ingest batch-results
```

## Output Location
```
data/raw/export/{HSN}/{HSN}_export.json
```

Each file contains 7 years (2018-2024) of trade data, ~80-300 KB per file.

## Expected Processing Time

| Workers | 11,000 Codes | Time |
|---------|-------------|------|
| 1 | ~229 hours | 9.5 days |
| 4 | ~57 hours | 2.4 days |
| 10 | ~23 hours | ~1 day |
| 20 | ~12 hours | 0.5 days |

**Recommendation**: Start with 4 workers, increase if needed.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "ConnectionError" | Make sure `redis-server` is running |
| "No jobs processing" | Check workers: `ps aux \| grep rq_worker` |
| "Jobs stuck in queue" | Restart a worker: `python scripts/rq_worker.py` |
| "Rate limit errors" | Reduce workers to 5, add delay in `scraper.py` |

## Full Documentation
See [BATCH_PROCESSING.md](BATCH_PROCESSING.md) for detailed setup, monitoring, and optimization.
