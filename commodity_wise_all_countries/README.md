# Commodity-wise All Countries Scraper

## Overview

This scraper extracts **country-wise trade data** for specific commodities from India's official trade statistics portal ([tradestat.commerce.gov.in](https://tradestat.commerce.gov.in)). For any given HSN code, it fetches export/import values for all trading partner countries, including USD values, quantities, and year-over-year growth rates.

### How It Works

1. **Session Bootstrap**: Establishes a session with the TradeStat portal and retrieves a CSRF token for authentication.
2. **Form Submission**: Submits a POST request with HSN code, year, and trade type parameters.
3. **HTML Parsing**: Parses the returned HTML table to extract country-wise trade data.
4. **JSON Output**: Saves structured data with comprehensive metadata, data quality metrics, and audit trail.

### Data Source

- **Provider**: DGCI&S (Directorate General of Commercial Intelligence and Statistics), Kolkata
- **Ministry**: Ministry of Commerce and Industry, Government of India
- **Coverage**: 2017-2018 to 2025-2026 (financial years)
- **Update Frequency**: Monthly

---

## Installation

```bash
pip install requests beautifulsoup4 lxml python-dotenv
```

---

## Basic Usage
```bash
python scrape_all_countries.py --hsn <8-digit-code> --year <year> --type <export|import>
```

---

## Scenarios

### 1. Single Year Export
```bash
python scrape_all_countries.py --hsn 27101944 --year 2024 --type export
```

### 2. Single Year Import
```bash
python scrape_all_countries.py --hsn 27101944 --year 2024 --type import
```

### 3. Multiple Years
```bash
python scrape_all_countries.py --hsn 27101944 --years 2022,2023,2024 --type export
```

### 4. All Available Years
```bash
python scrape_all_countries.py --hsn 27101944 --all-years --type export
```

### 5. Consolidate Multiple Years into Single File
```bash
python scrape_all_countries.py --hsn 27101944 --all-years --type export --consolidate
```

---

## Output Location
```
data/
├── export/
│   ├── 27101944_2024.json
│   ├── 27101944_2023.json
│   ├── 27101944_consolidated.json
│   └── ...
└── import/
    ├── 27101944_2024.json
    └── ...
```

---

## Available Options

| Option | Values | Description |
|--------|--------|-------------|
| `--hsn` | 8-digit code | HSN code to scrape (required) |
| `--year` | 2018-2024 | Single year |
| `--years` | comma-separated | Multiple years |
| `--all-years` | flag | All available years (2018-2024) |
| `--type` | export, import | Trade type (default: export) |
| `--consolidate` | flag | Merge all years into single JSON |
| `--output` | path | Custom output directory |

---

## Sample Output

```json
{
  "metadata": {
    "scraped_at": "2026-02-03T10:30:00",
    "source_url": "https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_export",
    "hsn_code": "27101944",
    "financial_year": "2024"
  },
  "commodity": {
    "hsn_code": "27101944",
    "description": "HIGH SPEED DIESEL",
    "unit": "KGS"
  },
  "countries": [
    {
      "sno": 1,
      "country": "U ARAB EMTS",
      "values_usd": {
        "y2023_2024": 5765.94,
        "y2024_2025": 4285.48,
        "pct_growth": -25.67
      },
      "values_quantity": {
        "y2023_2024": 9876543.21,
        "y2024_2025": 7654321.00,
        "pct_growth": -22.50
      }
    }
  ],
  "totals": {
    "total": {
      "values_usd": { "y2023_2024": 12345.67, "y2024_2025": 9876.54 }
    },
    "india_total": {
      "values_usd": { "y2023_2024": 437072.03, "y2024_2025": 437704.58 }
    },
    "pct_share": { "y2023_2024": 2.82, "y2024_2025": 2.26 }
  },
  "data_quality": {
    "total_countries_count": 45,
    "countries_with_complete_data": 42,
    "extraction_completeness_percent": 93.33,
    "validation_status": "VALID"
  }
}
```

---

## File Structure

```
commodity_wise_all_countries/
├── README.md                  # This file
├── scrape_all_countries.py    # CLI entry point
├── .env.example               # Environment config template
└── lib/
    ├── __init__.py
    ├── scraper.py             # HTTP scraping logic
    ├── parser.py              # HTML parsing logic
    ├── consolidator.py        # Multi-year consolidation
    └── session.py             # Session management
```
