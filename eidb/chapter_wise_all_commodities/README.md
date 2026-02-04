# EIDB Chapter-wise All Commodities Scraper

## Overview

This scraper extracts **chapter-wise trade data** for all commodities from India's Export Import Data Bank (EIDB) on [tradestat.commerce.gov.in](https://tradestat.commerce.gov.in). It fetches aggregated trade statistics for all HS chapters (2-digit codes) in a given financial year.

### How It Works

1. **Session Bootstrap**: Establishes a session with the TradeStat portal and retrieves a CSRF token for authentication.
2. **Form Submission**: Submits a POST request with parameters like year, digit level, trade type, and value unit.
3. **HTML Parsing**: Parses the returned HTML table using BeautifulSoup to extract structured data.
4. **JSON Output**: Saves the extracted data as JSON with comprehensive metadata.

### Data Source

- **Provider**: DGCI&S (Directorate General of Commercial Intelligence and Statistics), Kolkata
- **Ministry**: Ministry of Commerce and Industry, Government of India
- **Database**: EIDB (Export Import Data Bank) - Yearly Data
- **Coverage**: FY 2018-19 to FY 2025-26
- **Update Frequency**: Monthly

---

## Installation

```bash
pip install requests beautifulsoup4 lxml loguru pydantic-settings
```

---

## Basic Usage

```bash
python scrape_chapter_wise_all_commodities.py --year <year> --type <export|import>
```

---

## Scenarios

### 1. By Trade Type

**Export Data**
```bash
python scrape_chapter_wise_all_commodities.py --year 2024 --type export
```

**Import Data**
```bash
python scrape_chapter_wise_all_commodities.py --year 2024 --type import
```

---

### 2. By HS Code Digit Level

**2-digit (Chapter) - Default**
```bash
python scrape_chapter_wise_all_commodities.py --year 2024 --type export --digit-level 2
```

**4-digit (Heading)**
```bash
python scrape_chapter_wise_all_commodities.py --year 2024 --type export --digit-level 4
```

**6-digit (Sub-heading)**
```bash
python scrape_chapter_wise_all_commodities.py --year 2024 --type export --digit-level 6
```

**8-digit (Tariff Item)**
```bash
python scrape_chapter_wise_all_commodities.py --year 2024 --type export --digit-level 8
```

---

### 3. By Value Type

**US $ Million (default)**
```bash
python scrape_chapter_wise_all_commodities.py --year 2024 --type export --value-type usd
```

**Indian Rupees (₹ Crore)**
```bash
python scrape_chapter_wise_all_commodities.py --year 2024 --type export --value-type inr
```

---

## Output Structure

### File Location
```
data/
├── export/
│   ├── 2024_2digit_usd.json
│   └── 2024_4digit_usd.json
└── import/
    ├── 2024_2digit_usd.json
    └── 2024_4digit_usd.json
```

### JSON Schema

```json
{
  "metadata": {
    "extraction": {
      "scraped_at": "2026-02-04T12:00:00",
      "feature": "eidb_chapter_wise_all_commodities",
      "year": 2024,
      "digit_level": 2,
      "trade_type": "export",
      "value_type": "usd"
    }
  },
  "commodities": [
    {
      "sno": 1,
      "hscode": "01",
      "commodity": "LIVE ANIMALS",
      "value": 245.67,
      "share_pct": 0.05,
      "growth_pct": 12.34
    }
  ],
  "india_total": {
    "total_value": 451234.56,
    "total_growth_pct": 5.67
  }
}
```

---

## Folder Structure

```
eidb/chapter_wise_all_commodities/
├── README.md                           # This file
├── .env.example                        # Environment variables template
├── scrape_chapter_wise_all_commodities.py  # Main CLI script
├── lib/
│   ├── __init__.py                     # Module exports
│   ├── scraper.py                      # HTTP request handling
│   ├── parser.py                       # HTML parsing logic
│   ├── session.py                      # Session management
│   └── storage.py                      # Data persistence
└── data/
    ├── export/                         # Export data output
    └── import/                         # Import data output
```

---

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
BASE_URL=https://tradestat.commerce.gov.in
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

---

## Notes

- Data availability: FY 2018-19 onwards
- Financial year runs April to March (e.g., FY 2024-25 = April 2024 to March 2025)
- Values marked (P) are Provisional, others are Final
