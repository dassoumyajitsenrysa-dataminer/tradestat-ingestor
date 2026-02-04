# EIDB Chapter-wise All Commodities Scraper

Scrapes **yearly** trade data from India's Export Import Data Bank (EIDB) for all commodities at the chapter level (2-digit HS codes).

## Overview

This scraper fetches aggregated trade statistics for all HS chapters in a given financial year, providing a high-level view of India's trade composition.

## URL Endpoints

| Trade Type | URL |
|------------|-----|
| Export | `https://tradestat.commerce.gov.in/eidb/chapter_wise_export` |
| Import | `https://tradestat.commerce.gov.in/eidb/chapter_wise_import` |

## Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| `trade_type` | Export or Import | `export`, `import` |
| `year` | Financial year | `2018` - `2025` (represents FY 2018-19 to 2025-26) |
| `value_type` | Value unit | `usd` (US $ Million), `inr` (₹ Crore) |

## Data Structure

### Output Fields

| Field | Description | Example |
|-------|-------------|---------|
| `sno` | Serial number | `1` |
| `hscode` | 2-digit HS chapter code | `01` |
| `commodity` | Chapter description | `LIVE ANIMALS` |
| `value` | Trade value | `245.67` |
| `share_pct` | Share of total trade (%) | `0.05` |
| `growth_pct` | Year-over-year growth (%) | `12.34` |

### India Total

| Field | Description |
|-------|-------------|
| `total_value` | Total trade value |
| `total_growth_pct` | Overall YoY growth |

## Usage

### As a Module

```python
from tradestat_ingestor.scrapers.eidb.chapter_wise_all_commodities import (
    scrape_chapter_wise_all_commodities,
    parse_chapter_wise_html
)
from tradestat_ingestor.core.session import TradeStatSession

# Initialize session
session = TradeStatSession(
    base_url="https://tradestat.commerce.gov.in",
    user_agent="Mozilla/5.0..."
)
state = session.bootstrap("/eidb/chapter_wise_export")

# Scrape data
html = scrape_chapter_wise_all_commodities(
    session=session.session,
    base_url="https://tradestat.commerce.gov.in",
    year="2024",
    trade_type="export",
    value_type="usd",
    state=state
)

# Parse data
data = parse_chapter_wise_html(html, year="2024", trade_type="export", value_type="usd")
```

### CLI Usage

```bash
# Export data for FY 2024-25
python scrape_chapter_wise_all_commodities.py --type export --year 2024 --value-type usd

# Import data
python scrape_chapter_wise_all_commodities.py --type import --year 2024 --value-type usd
```

## Output Location

```
src/data/raw/eidb/chapter_wise_all_commodities/
├── export/
│   ├── 2024_usd.json
│   └── 2024_inr.json
└── import/
    ├── 2024_usd.json
    └── 2024_inr.json
```

## File Structure

```
chapter_wise_all_commodities/
├── __init__.py      # Module exports
├── scraper.py       # HTTP request handling
├── parser.py        # HTML parsing logic
├── storage.py       # Data persistence
└── README.md        # This documentation
```

## Notes

- Data availability: January 2018 onwards
- Financial year runs April to March (e.g., FY 2024-25 = April 2024 to March 2025)
- Values marked (R) are Revised Final, (F) are Final/Provisional
