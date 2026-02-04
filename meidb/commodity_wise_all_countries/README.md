# MEIDB Commodity-wise All Countries Scraper

## Overview

This scraper extracts **monthly commodity-wise trade data by country** from India's Monthly Export Import Data Bank (MEIDB). It shows the breakdown by trading partner countries for a specific HS code.

### How It Works

1. **Session Bootstrap**: Establishes a session and retrieves CSRF token.
2. **Form Submission**: Submits request with HS code, month, year, and parameters.
3. **HTML Parsing**: Parses the returned HTML table with country-wise YoY comparison.
4. **JSON Output**: Saves data as JSON with metadata.

### Data Source

- **Provider**: DGCI&S (Directorate General of Commercial Intelligence and Statistics)
- **Database**: MEIDB (Monthly Export Import Data Bank)
- **Coverage**: January 2018 to November 2025
- **Update Frequency**: Monthly

---

## Installation

```bash
pip install requests beautifulsoup4 lxml loguru pydantic-settings
```

---

## Basic Usage

```bash
python scrape_meidb_commodity_wise_all_countries.py --hscode <code> --month <1-12> --year <year> --type <export|import>
```

---

## Scenarios

### 1. By HS Code Level

**2-digit (Chapter)**
```bash
python scrape_meidb_commodity_wise_all_countries.py --hscode 85 --month 11 --year 2025 --type export
```

**8-digit (Tariff Item)**
```bash
python scrape_meidb_commodity_wise_all_countries.py --hscode 84713010 --month 11 --year 2025 --type export
```

---

### 2. By Value Type

**US $ Million (default)**
```bash
python scrape_meidb_commodity_wise_all_countries.py --hscode 85 --month 11 --year 2025 --type export --value-type usd
```

**Quantity (8-digit only)**
```bash
python scrape_meidb_commodity_wise_all_countries.py --hscode 84713010 --month 11 --year 2025 --type export --value-type quantity
```

---

### 3. By Year Type

**Financial Year (default)**
```bash
python scrape_meidb_commodity_wise_all_countries.py --hscode 85 --month 11 --year 2025 --type export --year-type financial
```

**Calendar Year**
```bash
python scrape_meidb_commodity_wise_all_countries.py --hscode 85 --month 11 --year 2025 --type export --year-type calendar
```

---

## Output Structure

### File Location
```
data/
├── export/
│   ├── level_2/
│   │   └── 85_nov_2025_usd.json
│   └── level_8/
│       └── 84713010_nov_2025_usd.json
└── import/
    └── ...
```

### JSON Schema

```json
{
  "metadata": {
    "extraction": {
      "scraped_at": "2026-02-04T12:00:00",
      "feature": "meidb_commodity_wise_all_countries",
      "hscode": "85",
      "month": 11,
      "year": 2025,
      "trade_type": "export"
    }
  },
  "countries": [
    {
      "sno": 1,
      "country": "U.S.A.",
      "month_prev_year": 523.45,
      "month_curr_year": 678.90,
      "month_yoy_growth_pct": 29.71,
      "cumulative_prev_year": 4567.89,
      "cumulative_curr_year": 5678.90,
      "cumulative_yoy_growth_pct": 24.32
    }
  ],
  "total": {
    "month_prev_year": 3914.27,
    "month_curr_year": 5270.89,
    "month_yoy_growth_pct": 34.66
  }
}
```

---

## Understanding the Data

### Year-over-Year Comparison by Country

| Field | Description |
|-------|-------------|
| `month_prev_year` | Same month, previous year |
| `month_curr_year` | Same month, current year |
| `month_yoy_growth_pct` | YoY growth for that month |
| `cumulative_prev_year` | Apr-Month, previous year |
| `cumulative_curr_year` | Apr-Month, current year |
| `cumulative_yoy_growth_pct` | Cumulative YoY growth |

---

## Folder Structure

```
meidb/commodity_wise_all_countries/
├── README.md
├── .env.example
├── scrape_meidb_commodity_wise_all_countries.py
├── lib/
│   ├── __init__.py
│   ├── scraper.py
│   ├── parser.py
│   ├── session.py
│   └── storage.py
└── data/
    ├── export/
    └── import/
```

---

## Use Cases

1. **Market Analysis**: Identify top destination/source countries
2. **Trend Tracking**: Monitor monthly changes by country
3. **Diversification Study**: Analyze trade concentration
4. **Growth Opportunities**: Find fast-growing markets

---

## Notes

- Data availability: Jan 2018 to Nov 2025
- Quantity data only for 8-digit HS codes
- Shows all countries with trade value
