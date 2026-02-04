# EIDB Commodity x Country Timeseries Scraper

## Overview

This scraper extracts **commodity x country timeseries trade data** from India's Export Import Data Bank (EIDB). It fetches historical trade data for a specific HS code and country combination across multiple years.

### How It Works

1. **Session Bootstrap**: Establishes a session with the TradeStat portal and retrieves a CSRF token.
2. **Form Submission**: Submits a POST request with HS code, country code, year range, and value type.
3. **HTML Parsing**: Parses the returned HTML table to extract time series data.
4. **JSON Output**: Saves the extracted data as JSON with comprehensive metadata.

### Data Source

- **Provider**: DGCI&S (Directorate General of Commercial Intelligence and Statistics)
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
python scrape_commodity_x_country_timeseries.py --hscode <code> --country <code> --from-year <year> --to-year <year> --type <export|import>
```

---

## Scenarios

### 1. Single Country Timeseries

**Export to USA (423)**
```bash
python scrape_commodity_x_country_timeseries.py --hscode 84713010 --country 423 --from-year 2020 --to-year 2025 --type export
```

**Import from China (306)**
```bash
python scrape_commodity_x_country_timeseries.py --hscode 27090000 --country 306 --from-year 2018 --to-year 2025 --type import
```

---

### 2. Different HS Code Levels

**2-digit (Chapter)**
```bash
python scrape_commodity_x_country_timeseries.py --hscode 85 --country 423 --from-year 2020 --to-year 2025 --type export
```

**8-digit (Tariff Item)**
```bash
python scrape_commodity_x_country_timeseries.py --hscode 84713010 --country 423 --from-year 2020 --to-year 2025 --type export
```

---

### 3. By Value Type

**US $ Million (default)**
```bash
python scrape_commodity_x_country_timeseries.py --hscode 84713010 --country 423 --from-year 2020 --to-year 2025 --type export --value-type usd
```

**Quantity (8-digit only)**
```bash
python scrape_commodity_x_country_timeseries.py --hscode 84713010 --country 423 --from-year 2020 --to-year 2025 --type export --value-type quantity
```

---

## Output Structure

### File Location
```
data/
├── export/
│   └── hs84713010_423_USA_2020-2025_usd.json
└── import/
    └── hs27090000_306_CHINA_2018-2025_usd.json
```

### JSON Schema

```json
{
  "metadata": {
    "extraction": {
      "scraped_at": "2026-02-04T12:00:00",
      "feature": "eidb_commodity_x_country_timeseries",
      "hscode": "84713010",
      "country_code": "423",
      "country_name": "U.S.A.",
      "from_year": 2020,
      "to_year": 2025,
      "trade_type": "export"
    }
  },
  "timeseries": [
    {
      "year": 2020,
      "value": 123.45,
      "growth_pct": null
    },
    {
      "year": 2021,
      "value": 145.67,
      "growth_pct": 18.0
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
| 523 | Saudi Arabia |
| 413 | South Korea |
| 331 | United Kingdom |

---

## Folder Structure

```
eidb/commodity_x_country_timeseries/
├── README.md
├── .env.example
├── scrape_commodity_x_country_timeseries.py
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

- Data availability: FY 2018-19 onwards
- Quantity data only available for 8-digit HS codes
- Provides year-by-year breakdown for trend analysis
