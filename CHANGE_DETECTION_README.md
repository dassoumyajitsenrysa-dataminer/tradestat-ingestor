# Change Detection & Version Control System

## Overview

The change detection system automatically tracks all data modifications between scraping incidents, providing comprehensive delta reports, version history, and audit trails. This ensures data integrity, enables compliance tracking, and facilitates troubleshooting of data discrepancies.

**Key Features:**
- 🔍 Automatic change detection between consecutive scrapes
- 📊 Data drift analysis (NO_CHANGE, MINIMAL, MODERATE, SIGNIFICANT, CRITICAL)
- 📝 Complete version history with timestamps and checksums
- 🔄 Country-level change tracking (added, removed, modified)
- 📈 Value-level change metrics (USD, quantities, growth percentages)
- 🗂️ Persistent version storage in `.versions/` directory
- 📋 Changelog generation for audit trails

---

## Usage Examples

### 1. **Scrape with Change Detection (Show Changes)**

```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes
```

**Output:**
```
[*] Change Detection Report:
    Status: INITIAL_DATA
    Data Drift: BASELINE
    Total Changes: 0
    Percent Change: 100.0%
[+] Saved to: src/data/raw/commodity_wise_all_countries/export/09011112_2024.json
[+] Extracted 34 countries
```

### 2. **Rescrape and Detect No Changes**

```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes
```

**Output:**
```
[*] Change Detection Report:
    No changes detected (data identical to previous version)
```

### 3. **View Complete Version Changelog**

```bash
python scrape_cli.py --hsn 09011112 --type export --changelog
```

**Output:**
```
[*] Changelog for HSN 09011112 (EXPORT):
================================================================================

Year: 2023
  Timestamp: 2026-01-29T08:03:36.657924
  Checksum: fc9fbaacd6667d657856115dcfbb240a
  Data Quality: 82.76% complete, VALID validation
  [+] Changes detected in this version

Year: 2024
  Timestamp: 2026-01-29T08:03:45.840216
  Checksum: b164ae154a4d639325a492e5717ffd16
  Data Quality: 82.35% complete, VALID validation
```

---

## How It Works

### Detection Process

1. **Extraction**: Scraper retrieves live data from website
2. **Parsing**: HTML converted to structured JSON format
3. **History Lookup**: System checks for previous version of same HSN/Year
4. **Comparison**: Current data compared against previous version
5. **Delta Calculation**: Changes identified at country and value levels
6. **Drift Analysis**: Overall data change percentage calculated
7. **Persistence**: Current version saved to history
8. **Reporting**: Changes summarized in JSON output and CLI

### Change Categories

#### Added Countries
New countries that appear in current but not in previous version:
- Indicates expanded market coverage
- May signal new trade relationships

#### Removed Countries
Countries in previous version but missing in current:
- Could indicate discontinued exports
- May require investigation for data quality

#### Modified Countries
Countries with changed values:
- **USD Value Changes**: Trade volume modifications
- **Quantity Changes**: Volume adjustments
- **Growth % Changes**: Calculated percentage updates

### Data Drift Levels

| Drift Level | Percent Change | Interpretation |
|-------------|---|---|
| **NO_CHANGE** | 0% | Data identical to previous version |
| **MINIMAL** | 0-5% | Minor natural fluctuations (expected) |
| **MODERATE** | 5-15% | Typical quarterly/annual variations |
| **SIGNIFICANT** | 15-30% | Notable market changes (requires review) |
| **CRITICAL** | 30%+ | Major changes (urgent investigation) |

---

## JSON Output Structure

### Change Detection Section

```json
{
  "change_detection": {
    "status": "COMPARISON_COMPLETE",
    "change_type": "DATA_UPDATE",
    "has_changes": false,
    "changes_summary": {
      "countries_added": [],
      "countries_removed": [],
      "countries_modified": [],
      "detailed_changes": {}
    },
    "change_metrics": {
      "total_changes": 0,
      "percent_change": 0.0,
      "data_drift": "NO_CHANGE",
      "countries_added_count": 0,
      "countries_removed_count": 0,
      "countries_modified_count": 0
    },
    "timestamp": "2026-01-29T08:03:45.829024"
  }
}
```

### Example with Changes Detected

```json
{
  "change_detection": {
    "status": "COMPARISON_COMPLETE",
    "change_type": "DATA_UPDATE",
    "has_changes": true,
    "changes_summary": {
      "countries_added": ["VIETNAM", "THAILAND"],
      "countries_removed": [],
      "countries_modified": ["GERMANY", "BELGIUM", "CHINA"],
      "detailed_changes": {
        "GERMANY": {
          "usd_y2024_2025": {
            "previous": 11.5,
            "current": 12.07,
            "difference": 0.57,
            "percent_change": 4.96
          },
          "qty_y2024_2025": {
            "previous": 2100000.0,
            "current": 2150000.0,
            "difference": 50000.0,
            "percent_change": 2.38
          }
        }
      }
    },
    "change_metrics": {
      "total_changes": 5,
      "percent_change": 14.71,
      "data_drift": "MODERATE",
      "countries_added_count": 2,
      "countries_removed_count": 0,
      "countries_modified_count": 3
    },
    "timestamp": "2026-01-29T08:05:12.341567"
  }
}
```

---

## Version History Storage

### Location
```
src/data/raw/.versions/{feature}_{type}_{hsn}_history.json
```

**Example:**
```
src/data/raw/.versions/commodity_wise_all_countries_export_09011112_history.json
```

### Structure

Each version stored with:
- `timestamp`: ISO 8601 timestamp of extraction
- `checksum`: MD5 hash for integrity verification
- `snapshot`: Complete parsed data at that point in time
- `changes`: Delta report from previous version
- `commodity`: Commodity metadata
- `data_quality`: Quality metrics (extraction completeness, validation status)

### Version History Example

```json
{
  "2024": {
    "timestamp": "2026-01-29T08:03:45.840216",
    "checksum": "b164ae154a4d639325a492e5717ffd16",
    "snapshot": { ... },
    "changes": { ... },
    "commodity": { ... },
    "data_quality": { ... }
  },
  "2023": {
    "timestamp": "2026-01-29T08:03:36.657924",
    "checksum": "fc9fbaacd6667d657856115dcfbb240a",
    "snapshot": { ... },
    "changes": { ... },
    "commodity": { ... },
    "data_quality": { ... }
  }
}
```

---

## CLI Arguments

### `--show-changes`

Display change detection report during scraping:

```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes
```

Shows:
- Change type (INITIAL_DATA, DATA_UPDATE)
- Data drift level (NO_CHANGE, MINIMAL, MODERATE, SIGNIFICANT, CRITICAL)
- Total number of changes
- Percent change
- Countries added/removed/modified (first 5 with ellipsis if more)

### `--changelog`

Display complete version history for an HSN:

```bash
python scrape_cli.py --hsn 09011112 --type export --changelog
```

Shows all versions sorted by year with:
- Timestamp of each extraction
- MD5 checksum for integrity
- Data quality metrics
- Whether changes were detected

---

## Metadata Integration

### Scraper Version Update

When change detection is enabled, scraper version increments:

```json
"version": {
  "schema_version": "2.0",
  "scraper_version": "1.2",
  "change_detection_enabled": true
}
```

### Processing Chain Update

```json
"processing_chain": [
  "scrape_html",
  "parse_html", 
  "extract_structure",
  "validate_data",
  "detect_changes"  // NEW
]
```

### Audit Trail Enhancement

```json
"audit_trail": {
  "scraper_configuration": {
    "change_detection": true
  },
  "performance_metrics": {
    "change_detection_runtime_ms": 45
  }
}
```

---

## Data Quality Metrics

### Checksum Validation

Every version stored with MD5 checksum for verification:

```python
checksum_md5: "b164ae154a4d639325a492e5717ffd16"
```

Use to verify data integrity:
```python
import hashlib
import json

data = json.load(open('09011112_2024.json'))
checksum = hashlib.md5(
    json.dumps(data['parsed_data'], sort_keys=True, default=str).encode()
).hexdigest()
assert checksum == data['data_manifest']['checksum_md5']
```

### Completeness Tracking

Each version tracks extraction completeness:

```json
"data_quality": {
  "extraction_completeness_percent": 82.35,
  "total_countries_count": 34,
  "countries_with_complete_data": 28,
  "countries_with_missing_data": 6,
  "validation_status": "VALID"
}
```

---

## Advanced Usage

### Detecting Specific Country Changes

```python
from pathlib import Path
import json
from tradestat_ingestor.core.change_detector import ChangeDetector

detector = ChangeDetector()

# Get comparison report
report = detector.get_comparison_report(
    feature="commodity_wise_all_countries",
    trade_type="export",
    hsn="09011112",
    year="2024"
)

# Check if Germany's values changed
if "GERMANY" in report['changes']['changes_summary']['detailed_changes']:
    changes = report['changes']['changes_summary']['detailed_changes']['GERMANY']
    print("Germany's changes:", changes)
```

### Generating Data Lineage Report

```python
from tradestat_ingestor.core.change_detector import ChangeDetector

detector = ChangeDetector()

# Get changelog
changelog = detector.generate_changelog(
    feature="commodity_wise_all_countries",
    trade_type="export",
    hsn="09011112"
)

for entry in changelog:
    print(f"Year {entry['year']}: {entry['checksum']}")
    print(f"  Quality: {entry['data_quality']['extraction_completeness_percent']}%")
```

### Monitoring Data Drift

```python
# Detect potential anomalies
if report['changes']['change_metrics']['data_drift'] in ['SIGNIFICANT', 'CRITICAL']:
    print("WARNING: Significant data changes detected!")
    print(f"Drift: {report['changes']['change_metrics']['percent_change']}%")
    
    # Alert administrators
    send_alert(
        severity="HIGH",
        message=f"Data drift of {report['changes']['change_metrics']['percent_change']}% detected"
    )
```

---

## Compliance & Audit Trail

### Complete Audit Trail

Every scrape creates permanent record:

```json
"audit_trail": {
  "operator": "automated_scraper",
  "execution_environment": "production",
  "scraper_configuration": {
    "hsn": "09011112",
    "year": "2024",
    "trade_type": "export",
    "change_detection": true
  },
  "performance_metrics": {
    "response_time_ms": 100,
    "parsing_efficient": "Optimized"
  }
}
```

### Long-Term Data Retention

Version history files stored with policy:

```json
"retention_policy": "LONG_TERM_ARCHIVE"
"reuse_conditions": "OPEN_DATA_CCBY4.0"
```

Ensures:
- ✅ Historical data preserved for compliance
- ✅ Audit trails available for investigations
- ✅ Data provenance traceable
- ✅ Regulatory requirements met

---

## Troubleshooting

### Issue: "No version history found"

**Cause**: First scrape for this HSN/year/type combination

**Solution**: This is expected. History will build with subsequent scrapes.

### Issue: False positive drift detection

**Cause**: Website updates or data corrections

**Action**: Review detailed changes to determine if legitimate. Update baseline if confirmed.

### Issue: Checksum mismatch

**Cause**: Data corruption or modification

**Action**: Rescrape the HSN to verify data integrity.

---

## Performance Characteristics

| Operation | Typical Duration | Notes |
|-----------|---|---|
| Single year scrape | 0.5-2 seconds | Includes change detection |
| Change detection | 1-3 ms | Negligible overhead |
| Changelog generation | 5-10 ms | Loads from stored history |
| Comparison report | 5-15 ms | Compares current vs previous |

---

## Future Enhancements

- [ ] Slack/Email alerts for critical drift detection
- [ ] Real-time monitoring dashboard
- [ ] Automated anomaly detection with ML
- [ ] Data recovery from version history
- [ ] Comparative analytics across years
- [ ] Export change reports to CSV/Excel

---

## Support

For issues or questions about change detection:
1. Check the `src/data/raw/.versions/` directory for version history
2. Review `SCHEMA_DOCUMENTATION.md` for data structure details
3. Enable `--show-changes` flag for debugging
4. Review audit trails in JSON output

