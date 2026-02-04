# MEIDB Commodity-wise Scraper

## Overview

This scraper extracts **monthly commodity-wise trade data** from India's Monthly Export Import Data Bank (MEIDB). It provides year-over-year comparison for a specific month and cumulative data from April to the selected month.

### How It Works

1. **Session Bootstrap**: Establishes a session and retrieves CSRF token.
2. **Form Submission**: Submits request with HS code, month, year, and value type.
3. **HTML Parsing**: Parses the returned HTML table with YoY comparison data.
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
python scrape_meidb_commodity_wise.py --hscode <code> --month <1-12> --year <year> --type <export|import>
```

---

## Scenarios

### 1. By HS Code Level

**2-digit (Chapter)**
```bash
python scrape_meidb_commodity_wise.py --hscode 85 --month 11 --year 2025 --type export
```

**8-digit (Tariff Item)**
```bash
python scrape_meidb_commodity_wise.py --hscode 84713010 --month 11 --year 2025 --type export
```

---

### 2. By Value Type

**US $ Million (default)**
```bash
python scrape_meidb_commodity_wise.py --hscode 85 --month 11 --year 2025 --type export --value-type usd
```

**Quantity (8-digit only)**
```bash
python scrape_meidb_commodity_wise.py --hscode 84713010 --month 11 --year 2025 --type export --value-type quantity
```

---

### 3. By Year Type

**Financial Year (default)**
```bash
python scrape_meidb_commodity_wise.py --hscode 85 --month 11 --year 2025 --type export --year-type financial
```

**Calendar Year**
```bash
python scrape_meidb_commodity_wise.py --hscode 85 --month 11 --year 2025 --type export --year-type calendar
```

---

### 4. All Commodities at a Digit Level

```bash
python scrape_meidb_commodity_wise.py --all --digit-level 2 --month 11 --year 2025 --type export
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
      "feature": "meidb_commodity_wise",
      "hscode": "85",
      "month": 11,
      "month_name": "November",
      "year": 2025,
      "trade_type": "export",
      "value_type": "usd",
      "year_type": "financial"
    }
  },
  "commodities": [
    {
      "sno": 1,
      "hscode": "85",
      "commodity": "ELECTRICAL MACHINERY...",
      "month_prev_year": 3914.27,
      "month_curr_year": 5270.89,
      "month_yoy_growth_pct": 34.66,
      "cumulative_prev_year": 25869.39,
      "cumulative_curr_year": 34931.94,
      "cumulative_yoy_growth_pct": 35.03
    }
  ],
  "india_total": {
    "month_prev_year": 31942.52,
    "month_curr_year": 38106.59,
    "month_yoy_growth_pct": 19.30,
    "cumulative_prev_year": 284603.50,
    "cumulative_curr_year": 291728.61,
    "cumulative_yoy_growth_pct": 2.50
  }
}
```

---

## Understanding the Data

### Year-over-Year Comparison

| Field | Description |
|-------|-------------|
| `month_prev_year` | Same month, previous year (e.g., Nov-2024) |
| `month_curr_year` | Same month, current year (e.g., Nov-2025) |
| `month_yoy_growth_pct` | Year-over-year growth for that month |
| `cumulative_prev_year` | Apr-Month, previous year |
| `cumulative_curr_year` | Apr-Month, current year |
| `cumulative_yoy_growth_pct` | Cumulative YoY growth |

### Data Status
- **(R)** = Revised Final
- **(F)** = Final

---

## Folder Structure

```
meidb/commodity_wise/
├── README.md
├── .env.example
├── scrape_meidb_commodity_wise.py
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

## Notes

- Data availability: Jan 2018 to Nov 2025
- Revised Final up to March 2025
- Quantity data only for 8-digit HS codes
