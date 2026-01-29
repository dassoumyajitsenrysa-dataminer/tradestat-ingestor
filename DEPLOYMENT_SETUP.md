# TradeSTAT Ingestor - Team Deployment Guide

## 📦 What's Included

This package contains the production-ready TradeSTAT scraper with:

```
tradestat-ingestor/
├── src/
│   └── tradestat_ingestor/          # Main package
│       ├── core/
│       │   ├── session.py           # HTTP session management
│       │   ├── change_detector.py   # Change detection system
│       │   └── __init__.py
│       ├── scrapers/
│       │   └── commodity_wise_all_countries/
│       │       ├── __init__.py
│       │       ├── export.py        # Export scraper
│       │       ├── import.py        # Import scraper
│       │       ├── parser.py        # HTML parser
│       │       └── consolidator.py  # Multi-year consolidation
│       ├── config/
│       │   ├── settings.py          # Configuration
│       │   └── __init__.py
│       ├── utils/
│       │   ├── constants.py
│       │   └── __init__.py
│       └── __init__.py
├── scrape_cli.py                    # Main CLI entry point
├── DEPLOYMENT_requirements.txt      # Minimal dependencies
├── DEPLOYMENT_SETUP.md              # This file
├── CHANGE_DETECTION_README.md       # Change detection documentation
├── CHANGE_DETECTION_QUICK_REF.md    # Quick reference
└── SCHEMA_DOCUMENTATION.md          # Data schema documentation
```

---

## ⚡ Quick Start (5 minutes)

### 1. **Clone/Download Package**

```bash
cd tradestat-ingestor
```

### 2. **Create Virtual Environment**

```bash
# Windows PowerShell
python -m venv venv
venv\Scripts\Activate.ps1

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. **Install Dependencies**

```bash
pip install -r DEPLOYMENT_requirements.txt
```

### 4. **Run Your First Scrape**

```bash
# Single year
python scrape_cli.py --hsn 09011112 --year 2024 --type export

# With change detection
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes

# View version history
python scrape_cli.py --hsn 09011112 --type export --changelog
```

### 5. **Find Your Data**

```
src/data/raw/commodity_wise_all_countries/export/09011112_2024.json
```

---

## 🔧 Usage Examples

### Single Year Export
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export
```

### Single Year Import
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type import
```

### Multiple Years
```bash
python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --type export
```

### Year Range
```bash
python scrape_cli.py --hsn 09011112 --years 2020-2024 --type export
```

### Consolidate Multiple Years into Single File
```bash
python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --type export --consolidate
```

### With Change Detection
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes
```

### View Changelog
```bash
python scrape_cli.py --hsn 09011112 --type export --changelog
```

---

## 📊 Output Structure

Each scrape creates a JSON file with:

```json
{
  "metadata": {
    "extraction": { ... },
    "data": { ... },
    "version": { ... },
    "lineage": { ... }
  },
  "parsed_data": {
    "commodity": { ... },
    "countries": [ ... ],
    "data_quality": { ... }
  },
  "change_detection": { ... },
  "data_manifest": { ... },
  "audit_trail": { ... }
}
```

**Files saved to:**
```
src/data/raw/{feature}/{type}/{hsn}_{year}.json
src/data/raw/{feature}/{type}/{hsn}_consolidated.json  (if --consolidate)
src/data/raw/.versions/{feature}_{type}_{hsn}_history.json  (version history)
```

---

## 🔍 Change Detection Features

The scraper automatically detects and tracks changes:

### Show Changes During Scrape
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes
```

Output:
```
[*] Change Detection Report:
    No changes detected (data identical to previous version)
```

### View Complete Changelog
```bash
python scrape_cli.py --hsn 09011112 --type export --changelog
```

Output:
```
Year: 2024
  Timestamp: 2026-01-29T08:03:45.840216
  Checksum: b164ae154a4d639325a492e5717ffd16
  Data Quality: 82.35% complete, VALID validation
```

**Change Detection Reports:**
- Countries added/removed/modified
- Value changes (USD, quantities, growth %)
- Data drift analysis (NO_CHANGE, MINIMAL, MODERATE, SIGNIFICANT, CRITICAL)
- MD5 checksum for integrity verification

---

## 📋 Required Arguments

| Argument | Values | Default | Required |
|----------|--------|---------|----------|
| `--hsn` | 8-digit code (e.g., 09011112) | - | **YES** |
| `--year` | Single year (2024) | - | One of: year/years/all-years |
| `--years` | Multiple (2022,2023,2024) or range (2020-2024) | - | One of: year/years/all-years |
| `--all-years` | Flag (no value needed) | - | One of: year/years/all-years |
| `--type` | export / import | export | No |
| `--feature` | Feature name | commodity_wise_all_countries | No |
| `--consolidate` | Flag to merge years | false | No |
| `--output` | Custom path | Auto (src/data/raw/...) | No |
| `--show-changes` | Flag for change detection | false | No |
| `--changelog` | Flag to view history | false | No |

---

## ✅ Key Features

✅ **Live Data Scraping** - Extracts from tradestat.commerce.gov.in  
✅ **Professional Metadata** - Complete data governance & audit trails  
✅ **Change Detection** - Automatically detects data modifications  
✅ **Version Control** - Maintains complete history with checksums  
✅ **Data Quality Metrics** - Extraction completeness & validation status  
✅ **Multi-Year Support** - 2018-2024 available (configurable)  
✅ **Consolidation** - Merge multiple years into single file  
✅ **Windows/Linux/Mac** - Cross-platform support  

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
```bash
# Solution: Ensure virtual environment is activated
# Windows:
venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate
```

### Issue: "Connection refused" or "Network error"
```
- Check internet connection
- Website might be down (https://tradestat.commerce.gov.in)
- Try again in a few moments
```

### Issue: "No data extracted" / "Empty countries list"
```
- Website structure may have changed
- Check SCHEMA_DOCUMENTATION.md for details
- Report issue to development team
```

### Issue: "Permission denied" on Windows
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `DEPLOYMENT_SETUP.md` | This guide |
| `CHANGE_DETECTION_README.md` | Detailed change detection docs |
| `CHANGE_DETECTION_QUICK_REF.md` | Quick reference (2-page) |
| `SCHEMA_DOCUMENTATION.md` | Complete data schema reference |
| `README.md` | Project overview |

---

## 🔐 Environment Configuration

### Optional: `.env` File

Create `.env` in project root if you need custom settings:

```env
# Base URL (if different from default)
TRADESTAT_BASE_URL=https://tradestat.commerce.gov.in

# Request timeout in seconds
REQUEST_TIMEOUT=60

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

**Note:** Most teams won't need this. Defaults work for 99% of use cases.

---

## 🚀 Team Workflow

### Recommended Setup

**1. First Run (Setup)**
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export
```

**2. Weekly Runs (Monitor Changes)**
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes
```

**3. Monthly Archive (Multi-Year)**
```bash
python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --type export --consolidate
```

**4. Quarterly Audit (View History)**
```bash
python scrape_cli.py --hsn 09011112 --type export --changelog
```

---

## 📞 Support & Issues

### Before Contacting Support

1. ✅ Verify HSN is 8 digits (e.g., `09011112`)
2. ✅ Check internet connection
3. ✅ Virtual environment is activated
4. ✅ Dependencies installed (`pip list`)
5. ✅ Review log output for specific error

### Common HSN Codes to Test

```
09011112 - Coffee Arabica Plantation
07019090 - Edible vegetables
15179090 - Vegetable oils
```

### Report Issues With

```
- Python version: python --version
- OS: Windows/Mac/Linux
- Error message (copy full output)
- HSN you were scraping
- What command you ran
```

---

## 🎯 Next Steps

1. ✅ Run quick start (section above)
2. ✅ Scrape sample data: `python scrape_cli.py --hsn 09011112 --year 2024 --type export`
3. ✅ Check output: `src/data/raw/commodity_wise_all_countries/export/09011112_2024.json`
4. ✅ Read: `CHANGE_DETECTION_QUICK_REF.md` for monitoring features
5. ✅ Share with team!

---

## 📄 File Cleanup Instructions

If you downloaded full repo, you can safely delete:

```
REMOVE:
- tests/                    # Test files
- examples/                 # Example files
- test_*.py                 # Test scripts
- check_*.py                # Debug scripts
- debug_table.py            # Debug script
- bootstrap_project.py      # Legacy setup
- check_queue.py            # Legacy
- submit_country_batch.py   # Legacy
- scripts/                  # Legacy scripts
- test_output/              # Test outputs
- venv/                     # If you use virtual env
- src/data/                 # Generated data (can regenerate)
- .git/                     # If not needed for version control

KEEP:
- src/tradestat_ingestor/   # Main package
- scrape_cli.py             # Entry point
- DEPLOYMENT_requirements.txt
- *.md files                # Documentation
- .env.example              # Config template
```

---

## 📦 Distribution

To share with team:

```bash
# Option 1: ZIP file
7z a tradestat-ingestor-v1.0.zip src/ scrape_cli.py *.md *.txt

# Option 2: Git clone
git clone <repo-url>

# Option 3: Docker (optional, advanced)
# See Dockerfile if available
```

---

**Version:** 1.2 (with Change Detection)  
**Last Updated:** 2026-01-29  
**Team:** Data Engineering  

