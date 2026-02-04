# EIDB Region-wise Scraper

## Overview

This scraper extracts **region-wise trade data** for a specific HS code from India's Export Import Data Bank (EIDB). It shows the breakdown by trading partner countries/regions for a given commodity.

### How It Works

1. **Session Bootstrap**: Establishes a session and retrieves CSRF token.
2. **Form Submission**: Submits request with HS code, year, and value type.
3. **HTML Parsing**: Parses the returned HTML table to extract country-wise breakdown.
4. **JSON Output**: Saves data as JSON with metadata.

### Data Source

- **Provider**: DGCI&S (Directorate General of Commercial Intelligence and Statistics)
- **Database**: EIDB (Export Import Data Bank) - Yearly Data
- **Coverage**: FY 2018-19 to FY 2025-26

---

## Installation

```bash
pip install requests beautifulsoup4 lxml loguru pydantic-settings
```

---

## Basic Usage

```bash
python scrape_region_wise.py --hscode <code> --year <year> --type <export|import>
```

---

## Scenarios

### 1. By Trade Type

**Export Destinations**
```bash
python scrape_region_wise.py --hscode 85 --year 2024 --type export
```

**Import Sources**
```bash
python scrape_region_wise.py --hscode 27 --year 2024 --type import
```

---

### 2. By HS Code Level

**2-digit (Chapter)**
```bash
python scrape_region_wise.py --hscode 85 --year 2024 --type export
```

**8-digit (Tariff Item)**
```bash
python scrape_region_wise.py --hscode 84713010 --year 2024 --type export
```

---

### 3. By Value Type

**US $ Million**
```bash
python scrape_region_wise.py --hscode 85 --year 2024 --type export --value-type usd
```

**Quantity (8-digit only)**
```bash
python scrape_region_wise.py --hscode 84713010 --year 2024 --type export --value-type quantity
```

---

## Output Structure

### File Location
```
data/
├── export/
│   ├── level_2/
│   │   └── 85_2024_usd.json
│   └── level_8/
│       └── 84713010_2024_usd.json
└── import/
    └── ...
```

### JSON Schema

```json
{
  "metadata": {
    "extraction": {
      "scraped_at": "2026-02-04T12:00:00",
      "feature": "eidb_region_wise",
      "hscode": "85",
      "commodity": "ELECTRICAL MACHINERY...",
      "year": 2024,
      "trade_type": "export"
    }
  },
  "countries": [
    {
      "sno": 1,
      "country": "U.S.A.",
      "value": 5678.90,
      "share_pct": 25.34,
      "growth_pct": 8.56
    }
  ],
  "total": {
    "total_value": 22400.50,
    "total_growth_pct": 12.34
  }
}
```

---

## Folder Structure

```
eidb/region_wise/
├── README.md
├── .env.example
├── scrape_region_wise.py
├── lib/
│   ├── __init__.py
│   ├── scraper.py
│   ├── parser.py
│   ├── session.py
│   └── storage.py
└── data/
    ├── export/
    │   ├── level_2/
    │   ├── level_4/
    │   ├── level_6/
    │   └── level_8/
    └── import/
        └── ...
```

---

## Notes

- Shows top trading partners for the specified commodity
- Useful for understanding geographic distribution of trade
- Quantity data only available for 8-digit HS codes
