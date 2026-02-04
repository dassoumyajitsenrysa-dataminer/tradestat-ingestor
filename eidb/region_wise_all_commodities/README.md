# EIDB Region-wise All Commodities Scraper

## Overview

This scraper extracts **region-wise all commodities trade data** from India's Export Import Data Bank (EIDB). It shows all commodities traded with a specific country/region.

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
python scrape_region_wise_all_commodities.py --country <code> --year <year> --type <export|import> --digit-level <2|4|6|8>
```

---

## Scenarios

### 1. By Trade Type

**Exports to USA**
```bash
python scrape_region_wise_all_commodities.py --country 423 --year 2024 --type export --digit-level 2
```

**Imports from China**
```bash
python scrape_region_wise_all_commodities.py --country 306 --year 2024 --type import --digit-level 2
```

---

### 2. By HS Code Level

**2-digit (Chapter)**
```bash
python scrape_region_wise_all_commodities.py --country 423 --year 2024 --type export --digit-level 2
```

**4-digit (Heading)**
```bash
python scrape_region_wise_all_commodities.py --country 423 --year 2024 --type export --digit-level 4
```

---

## Output Structure

### File Location
```
data/
├── export/
│   ├── level_2/
│   │   └── 423_USA_2024_usd.json
│   └── level_4/
│       └── 423_USA_2024_usd.json
└── import/
    └── ...
```

### JSON Schema

```json
{
  "metadata": {
    "extraction": {
      "scraped_at": "2026-02-04T12:00:00",
      "feature": "eidb_region_wise_all_commodities",
      "country_code": "423",
      "country_name": "U.S.A.",
      "year": 2024,
      "digit_level": 2,
      "trade_type": "export"
    }
  },
  "commodities": [
    {
      "sno": 1,
      "hscode": "85",
      "commodity": "ELECTRICAL MACHINERY...",
      "value": 12345.67,
      "share_pct": 18.45,
      "growth_pct": 22.34
    }
  ]
}
```

---

## Common Country Codes

| Code | Country |
|------|---------|
| 423 | U.S.A. |
| 306 | China |
| 412 | Japan |
| 314 | Germany |
| 526 | U.A.E. |

---

## Folder Structure

```
eidb/region_wise_all_commodities/
├── README.md
├── .env.example
├── scrape_region_wise_all_commodities.py
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

- Useful for analyzing trade composition with a specific country
- Can identify key export/import items for bilateral trade analysis
