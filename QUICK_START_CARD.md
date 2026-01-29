# 🚀 Quick Start Reference Card

## First Time Setup (< 5 minutes)

```bash
# 1. Extract package
unzip tradestat-ingestor-deployment.zip
cd tradestat-ingestor

# 2. Setup (choose one)
# Windows:
python -m venv venv && venv\Scripts\Activate.ps1 && pip install -r DEPLOYMENT_requirements.txt

# Mac/Linux:
python3 -m venv venv && source venv/bin/activate && pip install -r DEPLOYMENT_requirements.txt

# 3. Run
python scrape_cli.py --hsn 09011112 --year 2024 --type export

# Done! Check: src/data/raw/commodity_wise_all_countries/export/09011112_2024.json
```

---

## Commands Cheat Sheet

| Task | Command |
|------|---------|
| **Single Year** | `python scrape_cli.py --hsn 09011112 --year 2024 --type export` |
| **Multiple Years** | `python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --type export` |
| **Year Range** | `python scrape_cli.py --hsn 09011112 --years 2020-2024 --type export` |
| **Consolidate** | `python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --type export --consolidate` |
| **Track Changes** | `python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes` |
| **View History** | `python scrape_cli.py --hsn 09011112 --type export --changelog` |
| **Import Data** | `python scrape_cli.py --hsn 09011112 --year 2024 --type import` |

---

## Available Years
2024, 2023, 2022, 2021, 2020, 2019, 2018

---

## Output Location
```
src/data/raw/commodity_wise_all_countries/{type}/{hsn}_{year}.json
src/data/raw/commodity_wise_all_countries/{type}/{hsn}_consolidated.json  (if --consolidate)
```

---

## Example HSN Codes
- `09011112` - Coffee Arabica
- `07019090` - Edible Vegetables  
- `15179090` - Vegetable Oils

---

## Key Features
✅ Live scraping from Ministry website  
✅ Automatic change detection  
✅ Version history with checksums  
✅ Data quality metrics  
✅ Professional metadata & audit trails  
✅ Multi-year consolidation  

---

## What You Get (JSON)
- `metadata`: Extraction details + lineage
- `parsed_data`: Countries + trade values
- `change_detection`: What changed from last scrape
- `data_manifest`: Quality metrics + checksum
- `audit_trail`: Who, when, how it was scraped

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Activate venv: `venv\Scripts\Activate.ps1` (Windows) or `source venv/bin/activate` (Mac/Linux) |
| `Connection refused` | Check internet + website status |
| `Empty data` | Verify HSN is 8 digits; try: `09011112` |
| `Permission denied` | Windows: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |

---

## Documentation
| File | Use |
|------|-----|
| `TEAM_ONBOARDING.md` | 👉 **START HERE** |
| `DEPLOYMENT_SETUP.md` | Detailed setup guide |
| `CHANGE_DETECTION_QUICK_REF.md` | Change detection features |
| `CHANGE_DETECTION_README.md` | Advanced change tracking |
| `SCHEMA_DOCUMENTATION.md` | Data structure reference |

---

## Virtual Environment

```bash
# First time (one time only)
python -m venv venv

# Activate (every session)
# Windows:
venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# You should see: (venv) before your prompt

# Install dependencies (first time)
pip install -r DEPLOYMENT_requirements.txt

# Deactivate (when done)
deactivate
```

---

## Example Workflow

```bash
# Session 1: Setup
python -m venv venv
venv\Scripts\Activate.ps1  # Windows or source venv/bin/activate for Mac
pip install -r DEPLOYMENT_requirements.txt

# Session 2-N: Run scraper
venv\Scripts\Activate.ps1  # Windows or source venv/bin/activate for Mac
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes

# Check results
cat src/data/raw/commodity_wise_all_countries/export/09011112_2024.json
```

---

## Change Detection (NEW!)

```bash
# Show changes during scrape
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes

# View version history
python scrape_cli.py --hsn 09011112 --type export --changelog

# Possible outputs:
# ✓ "No changes detected" = data same as last scrape
# • "Data Drift: MINIMAL" = small natural variation (<5%)
# ⚠ "Data Drift: SIGNIFICANT" = notable change (review needed)
# ! "Data Drift: CRITICAL" = major change (investigate)
```

---

## JSON Keys Quick Ref

```json
{
  "metadata": {
    "extraction": {
      "scraped_at": "ISO 8601 timestamp",
      "feature": "commodity_wise_all_countries",
      "hsn_code": "09011112",
      "financial_year": "2024",
      "trade_type": "export"
    },
    "version": {
      "schema_version": "2.0",
      "scraper_version": "1.2",
      "change_detection_enabled": true
    }
  },
  "parsed_data": {
    "countries": [
      {
        "country": "GERMANY",
        "values_usd": {
          "y2023_2024": 11.5,      // Previous year
          "y2024_2025": 12.07,     // Current year
          "pct_growth": 4.96       // Growth %
        }
      }
    ]
  },
  "change_detection": {
    "has_changes": false,
    "data_drift": "NO_CHANGE"
  },
  "data_manifest": {
    "checksum_md5": "hash for verification",
    "validation_status": "VALID",
    "data_completeness": 82.35
  }
}
```

---

## Common Questions

**Q: Where do I put my HSN code?**  
A: `--hsn 09011112` (use 8-digit code from https://tradestat.commerce.gov.in)

**Q: How do I consolidate years?**  
A: `python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --type export --consolidate`

**Q: How do I know if data changed?**  
A: `python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes`

**Q: Can I scrape import data?**  
A: Yes! Use `--type import` instead of `--type export`

**Q: Where's my output?**  
A: `src/data/raw/commodity_wise_all_countries/{type}/{hsn}_{year}.json`

**Q: How long does it take?**  
A: Usually 0.5-2 seconds per year

---

## Support
1. Check `TEAM_ONBOARDING.md` first
2. Review documentation files
3. Verify HSN code format (8 digits)
4. Check internet connection
5. Try example: `09011112`

---

**Print this card and keep it handy!** 📌

Version 1.2 | Updated: 2026-01-29

