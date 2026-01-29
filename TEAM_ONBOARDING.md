# TradeSTAT Ingestor - Team Onboarding Guide

## Welcome! 👋

This guide will get you scraping trade data in **5 minutes**.

---

## Step 1: Extract the Package

```bash
# Download and extract the package
unzip tradestat-ingestor-deployment.zip
cd tradestat-ingestor
```

---

## Step 2: Setup Environment (First Time Only)

### Windows PowerShell

```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r DEPLOYMENT_requirements.txt
```

### macOS/Linux

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r DEPLOYMENT_requirements.txt
```

---

## Step 3: Run Your First Scrape ⚡

```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export
```

✅ **Done!** Your data is in: `src/data/raw/commodity_wise_all_countries/export/09011112_2024.json`

---

## Common Commands

### Single Year
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export
```

### Multiple Years
```bash
python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --type export
```

### Year Range
```bash
python scrape_cli.py --hsn 09011112 --years 2020-2024 --type export
```

### Consolidate Years (Single File)
```bash
python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --type export --consolidate
```

### Monitor Data Changes
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export --show-changes
```

### View Version History
```bash
python scrape_cli.py --hsn 09011112 --type export --changelog
```

---

## 📊 What You Get

Each scrape creates a JSON file with:

```json
{
  "metadata": {
    "extraction": {
      "scraped_at": "2026-01-29T08:03:45.822188",
      "feature": "commodity_wise_all_countries",
      "hsn_code": "09011112",
      "financial_year": "2024",
      "trade_type": "export",
      "response_size_bytes": 87067
    },
    "data": {
      "data_source": "DGCI&S",
      "data_provider": "Ministry of Commerce and Industry",
      "data_classification": "PUBLIC"
    },
    "version": {
      "schema_version": "2.0",
      "scraper_version": "1.2",
      "change_detection_enabled": true
    }
  },
  "parsed_data": {
    "commodity": {
      "hsn_code": "09011112",
      "description": "COFFEE ARABICA PLANTATION B"
    },
    "countries": [
      {
        "country": "GERMANY",
        "values_usd": {
          "y2023_2024": 11.5,
          "y2024_2025": 12.07,
          "pct_growth": 4.96
        },
        "values_quantity": {
          "y2023_2024": 2100000.0,
          "y2024_2025": 2150000.0,
          "pct_growth": 2.38
        }
      }
      // ... more countries
    ]
  },
  "change_detection": {
    "has_changes": false,
    "data_drift": "NO_CHANGE",
    "change_metrics": {
      "total_changes": 0,
      "percent_change": 0.0
    }
  }
}
```

---

## 🔍 Understanding Your Data

### Metadata Section
- **extraction**: When and how data was scraped
- **data**: Data source and classification
- **version**: Schema and scraper version info
- **lineage**: Data processing trail

### Parsed Data Section
- **commodity**: Product information
- **countries**: Trade data per country
  - `y2023_2024`: Previous financial year value
  - `y2024_2025`: Current financial year value
  - `pct_growth`: Percentage change

### Change Detection
- **has_changes**: Boolean - did data change from previous scrape?
- **data_drift**: Level of change (NO_CHANGE, MINIMAL, MODERATE, SIGNIFICANT, CRITICAL)
- **change_metrics**: Detailed change statistics

---

## 🚨 Quick Troubleshooting

### "ModuleNotFoundError"
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate
```

### "Connection refused"
- Check your internet connection
- Website might be temporarily down
- Try again in a few moments

### "No data extracted"
- HSN code might be invalid (must be 8 digits)
- Try: `python scrape_cli.py --hsn 09011112 --year 2024 --type export`

### "Permission denied" on Windows
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📚 Learn More

| Document | Topic |
|----------|-------|
| `DEPLOYMENT_SETUP.md` | Full setup guide |
| `CHANGE_DETECTION_QUICK_REF.md` | Change detection features (2 pages) |
| `CHANGE_DETECTION_README.md` | Detailed change detection docs |
| `SCHEMA_DOCUMENTATION.md` | Complete data schema reference |

---

## 🎯 Your First Week

### Day 1: Setup
- [ ] Extract package
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Run: `python scrape_cli.py --hsn 09011112 --year 2024 --type export`

### Day 2-3: Explore Data
- [ ] Open generated JSON file
- [ ] Review metadata section
- [ ] Check parsed_data countries list
- [ ] Understand data structure

### Day 4-5: Monitor Changes
- [ ] Run with `--show-changes` flag
- [ ] Try multiple years with `--consolidate`
- [ ] View changelog with `--changelog`

### Week 2: Integrate
- [ ] Identify HSN codes you need
- [ ] Create scraping schedule
- [ ] Setup data processing pipeline
- [ ] Share with team

---

## 💾 Virtual Environment Tips

### Activate (Each Session)
```bash
# Windows
venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

### Check It's Active
```bash
# You should see (venv) at start of terminal line
(venv) C:\Users\you\tradestat-ingestor>
```

### Deactivate (If Needed)
```bash
deactivate
```

---

## 🔐 Configuration (Optional)

Most teams don't need this, but you can create `.env` file:

```env
TRADESTAT_BASE_URL=https://tradestat.commerce.gov.in
REQUEST_TIMEOUT=60
LOG_LEVEL=INFO
```

---

## 📞 Need Help?

1. Check the documentation files
2. Review error messages (they're detailed)
3. Verify you're using correct HSN format (8 digits)
4. Check internet connection
5. Contact your team lead

---

## 🎉 Success Checklist

- ✅ Virtual environment created
- ✅ Dependencies installed
- ✅ First scrape completed
- ✅ Data file generated
- ✅ JSON structure understood
- ✅ Ready to share with team!

---

**Next:** Read `DEPLOYMENT_SETUP.md` for advanced usage  
**Questions?** Check `CHANGE_DETECTION_QUICK_REF.md` for common features

Happy scraping! 🚀

