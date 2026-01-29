# Change Detection Quick Reference

## TL;DR - Quick Start

### Command to scrape with change detection:
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes
```

### Command to view all scraped versions:
```bash
python scrape_cli.py --hsn 09011112 --type export --changelog
```

---

## What Gets Detected?

✅ **Countries Added** - New countries appearing in current scrape  
✅ **Countries Removed** - Countries no longer in data  
✅ **Values Modified** - USD, quantities, or growth percentages changed  
✅ **Data Drift** - Percentage change from NO_CHANGE to CRITICAL  
✅ **Checksum** - MD5 hash for integrity verification  

---

## Where Is Data Stored?

**Version History Location:**
```
src/data/raw/.versions/
```

**Example File:**
```
src/data/raw/.versions/commodity_wise_all_countries_export_09011112_history.json
```

**Single Year Output:**
```
src/data/raw/commodity_wise_all_countries/export/09011112_2024.json
```

Each file includes:
- `change_detection`: Complete delta report
- `metadata`: Extraction details + change_detection_enabled flag
- `parsed_data`: The actual trade data
- `audit_trail`: Who, when, what was scraped

---

## Output Examples

### No Changes (Rerun)
```
[*] Change Detection Report:
    No changes detected (data identical to previous version)
```

### First Run (New Data)
```
[*] Change Detection Report:
    Status: INITIAL_DATA
    Data Drift: BASELINE
    Total Changes: 0
    Percent Change: 100.0%
```

### Changes Detected
```
[*] Change Detection Report:
    Status: DATA_UPDATE
    Data Drift: MODERATE
    Total Changes: 5
    Percent Change: 14.71%
    [+] Countries Added: VIETNAM, THAILAND
    [~] Countries Modified: 3 countries
```

---

## Data Drift Levels

| Level | Range | Meaning |
|-------|-------|---------|
| NO_CHANGE | 0% | Identical to previous |
| MINIMAL | <5% | Normal fluctuation |
| MODERATE | 5-15% | Expected variation |
| SIGNIFICANT | 15-30% | Notable change (review) |
| CRITICAL | >30% | Major change (investigate) |

---

## JSON Change Detection Format

```json
{
  "change_detection": {
    "has_changes": false,
    "data_drift": "NO_CHANGE",
    "changes_summary": {
      "countries_added": [],
      "countries_removed": [],
      "countries_modified": [],
      "detailed_changes": {}
    },
    "change_metrics": {
      "total_changes": 0,
      "percent_change": 0.0
    }
  }
}
```

---

## CLI Flags Reference

| Flag | Purpose | Example |
|------|---------|---------|
| `--show-changes` | Display changes during scrape | `--year 2024 --show-changes` |
| `--changelog` | View all versions for HSN | `--type export --changelog` |

**Both work with:**
- `--hsn` (required): 8-digit code
- `--type` (optional): export/import (default: export)

---

## Common Use Cases

### 1. Verify data hasn't changed
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes
# Output: "No changes detected"
```

### 2. Track data over time
```bash
python scrape_cli.py --hsn 09011112 --type export --changelog
# Shows: 2023, 2024 versions with checksums
```

### 3. Monitor for issues
```bash
python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --show-changes
# Shows percent_change for each year
```

### 4. Audit data quality
Check JSON file for:
```json
"data_quality": {
  "extraction_completeness_percent": 82.35,
  "validation_status": "VALID"
}
```

---

## Checksum Verification (Python)

```python
import json, hashlib
data = json.load(open('09011112_2024.json'))
checksum = hashlib.md5(
    json.dumps(data['parsed_data'], sort_keys=True, default=str).encode()
).hexdigest()
print(checksum == data['data_manifest']['checksum_md5'])  # True = verified
```

---

## How Version History Works

**First scrape:**
- Creates version file in `.versions/`
- Stores complete snapshot
- Marks as "NEW_EXTRACTION"

**Second scrape (same year):**
- Compares with previous snapshot
- Detects changes (or "No changes")
- Updates version with new checksum
- Maintains full history

**Multi-year scrape:**
- Each year compared to its own history
- Independent change reports
- All stored in same `.versions/` file

---

## Metadata Fields Added

**In Output JSON:**
```json
"metadata": {
  "version": {
    "change_detection_enabled": true  // NEW
  },
  "lineage": {
    "processing_chain": [..., "detect_changes"]  // NEW
  }
}
```

**In Audit Trail:**
```json
"audit_trail": {
  "scraper_configuration": {
    "change_detection": true  // NEW
  }
}
```

---

## Performance Impact

- Change detection adds **<1ms** overhead
- Version history files **~1-2MB** per HSN per 7 years
- No impact on scraping speed
- Automatic compression available (future)

---

## Troubleshooting

**Q: Why "INITIAL_DATA" on first run?**  
A: No previous version exists yet. This is normal.

**Q: Why "No changes" on rerun?**  
A: Data is identical to previous scrape. Website hasn't changed.

**Q: Where can I see detailed changes?**  
A: In JSON under `change_detection.changes_summary.detailed_changes`

**Q: Can I manually edit version history?**  
A: Not recommended. Delete `.versions/` file to reset if needed.

---

## Next Steps

1. ✅ Run: `python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes`
2. ✅ View: `python scrape_cli.py --hsn 09011112 --type export --changelog`
3. ✅ Check: `src/data/raw/commodity_wise_all_countries/export/09011112_2024.json`
4. ✅ Verify: Inspect the `change_detection` section in JSON

For detailed info, see: `CHANGE_DETECTION_README.md`

