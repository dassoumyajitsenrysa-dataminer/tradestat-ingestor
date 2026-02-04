# Country-wise Trade Data Scraper

Standalone scraper for fetching **Country-wise Export/Import** data from India's TradeStat portal.

## Overview

This scraper extracts country-wise trade data from:
- **Export**: https://tradestat.commerce.gov.in/eidb/country_wise_export
- **Import**: https://tradestat.commerce.gov.in/eidb/country_wise_import

## Features

- ✅ Export and Import data support
- ✅ All ~240 countries available
- ✅ Filter by specific country (with aliases: usa, uk, china, etc.)
- ✅ Multiple years (2018-2024)
- ✅ Value types: USD (US $ Million) or INR (₹ Crore)
- ✅ Comprehensive metadata in JSON output
- ✅ Command-line interface

## Installation

```bash
# Install dependencies
pip install requests beautifulsoup4 lxml
```

## Quick Start

```bash
# Get all countries export data for 2024-2025
python scrape_country_wise.py --year 2024 --type export

# Get USA export data
python scrape_country_wise.py --year 2024 --type export --country usa

# Get China import data in INR
python scrape_country_wise.py --year 2024 --type import --country china --value-type inr

# Get USA data for multiple years
python scrape_country_wise.py --years 2024 2023 2022 --type export --country usa

# Get all available years for a country
python scrape_country_wise.py --all-years --type export --country usa

# List all country codes
python scrape_country_wise.py --list-countries
```

## Command Reference

| Option | Description |
|--------|-------------|
| `--year YEAR` | Single year (e.g., 2024 for FY 2024-2025) |
| `--years YEAR [YEAR ...]` | Multiple years |
| `--all-years` | All available years (2018-2024) |
| `--type {export,import}` | Trade type (default: export) |
| `--value-type {usd,inr}` | Value unit (default: usd) |
| `--country NAME/CODE` | Filter by country (supports aliases) |
| `--output DIR` | Output directory |
| `--list-countries` | Show all country codes |
| `--delay SECONDS` | Delay between requests (default: 1.0) |

## Country Aliases

You can use common aliases instead of official names:

| Alias | Country |
|-------|---------|
| usa, us, america | U S A |
| uk, britain | U K |
| uae, emirates | U ARAB EMTS |
| china | CHINA P RP |
| germany | GERMANY |
| japan | JAPAN |
| france | FRANCE |
| korea, south korea | KOREA RP |
| saudi, saudi arabia | SAUDI ARAB |
| bangladesh | BANGLADESH PR |
| nepal | NEPAL |
| sri lanka | SRI LANKA DSR |
| pakistan | PAKISTAN IR |

## Output Structure

```
data/raw/country_wise/
├── export/
│   ├── all_countries_2024-2025_usd.json
│   └── by_country/
│       ├── U_S_A_2024-2025_usd.json
│       ├── CHINA_P_RP_2024-2025_usd.json
│       └── ...
└── import/
    ├── all_countries_2024-2025_usd.json
    └── by_country/
        └── ...
```

## JSON Output Format

```json
{
  "metadata": {
    "source": {
      "name": "TradeStat - Department of Commerce, India",
      "url": "https://tradestat.commerce.gov.in/eidb/country_wise_export",
      "database": "EIDB (Export Import Data Bank)"
    },
    "extraction": {
      "timestamp_utc": "2026-02-03T02:30:00+00:00",
      "tool": "country_wise_scraper",
      "version": "1.0.0"
    },
    "query_parameters": {
      "trade_type": "export",
      "year": "2024",
      "fiscal_year": "2024-2025",
      "country_code": "423",
      "country_name": "U S A",
      "value_type": "usd",
      "value_unit": "US $ Million"
    },
    "data_info": {
      "record_count": 1,
      "value_unit": "US $ Million"
    }
  },
  "data": [
    {
      "serial_no": 1,
      "country": "U S A",
      "value": 85234.56,
      "value_unit": "US $ Million",
      "percentage_share": 17.5,
      "percentage_growth": 12.3
    }
  ]
}
```

## Use Cases

### 1. Track Trade with USA Over Time
```bash
python scrape_country_wise.py --all-years --type export --country usa
python scrape_country_wise.py --all-years --type import --country usa
```

### 2. Compare Top Trading Partners
```bash
python scrape_country_wise.py --year 2024 --type export
# Analyze the all_countries JSON to rank by value
```

### 3. Get Data in INR
```bash
python scrape_country_wise.py --year 2024 --type export --country china --value-type inr
```

## Notes

- Data is available from 2017-2018 to 2025-2026 (Apr-Aug for latest)
- Fiscal year runs April to March (e.g., 2024-2025 = Apr 2024 to Mar 2025)
- Trade figures include re-imports/re-exports
- US$ figures are sum of monthly USD values

## License

MIT
