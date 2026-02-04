# EIDB Region-wise Scraper

Scrapes **yearly** trade data from India's Export Import Data Bank (EIDB) for a specific HS code broken down by region/country.

## Overview

This scraper fetches trade data for a specific commodity showing the breakdown by trading partner countries/regions for a given financial year.

## URL Endpoints

| Trade Type | URL |
|------------|-----|
| Export | `https://tradestat.commerce.gov.in/eidb/region_wise_export` |
| Import | `https://tradestat.commerce.gov.in/eidb/region_wise_import` |

## Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| `trade_type` | Export or Import | `export`, `import` |
| `hscode` | HS code | 2, 4, 6, or 8 digit code |
| `year` | Financial year | `2018` - `2025` |
| `value_type` | Value unit | `usd`, `inr`, `quantity` (8-digit only) |

## Data Structure

### Output Fields

| Field | Description | Example |
|-------|-------------|---------|
| `sno` | Serial number | `1` |
| `country_code` | Country/region code | `423` |
| `country` | Country/region name | `U.S.A.` |
| `value` | Trade value | `5678.90` |
| `share_pct` | Share of commodity trade (%) | `25.34` |
| `growth_pct` | Year-over-year growth (%) | `8.56` |

### Metadata

| Field | Description |
|-------|-------------|
| `hscode` | HS code queried |
| `commodity` | Commodity description |
| `year` | Financial year |
| `total_countries` | Number of trading partners |

## Usage

### As a Module

```python
from tradestat_ingestor.scrapers.eidb.region_wise import (
    scrape_region_wise,
    parse_region_wise_html
)
from tradestat_ingestor.core.session import TradeStatSession

# Initialize session
session = TradeStatSession(
    base_url="https://tradestat.commerce.gov.in",
    user_agent="Mozilla/5.0..."
)
state = session.bootstrap("/eidb/region_wise_export")

# Scrape data
html = scrape_region_wise(
    session=session.session,
    base_url="https://tradestat.commerce.gov.in",
    hscode="84713010",
    year="2024",
    trade_type="export",
    value_type="usd",
    state=state
)

# Parse data
data = parse_region_wise_html(html, hscode="84713010", year="2024", ...)
```

### CLI Usage

```bash
# Export by region for HS 84713010
python scrape_region_wise.py --type export --hscode 84713010 --year 2024 --value-type usd

# Import by region for HS 27090000
python scrape_region_wise.py --type import --hscode 27090000 --year 2024 --value-type usd
```

## Output Location

```
src/data/raw/eidb/region_wise/
├── export/
│   ├── level_2/
│   │   └── 85_2024_usd.json
│   ├── level_4/
│   │   └── 8471_2024_usd.json
│   ├── level_6/
│   │   └── 847130_2024_usd.json
│   └── level_8/
│       └── 84713010_2024_usd.json
└── import/
    └── ...
```

## File Structure

```
region_wise/
├── __init__.py      # Module exports
├── scraper.py       # HTTP request handling
├── parser.py        # HTML parsing logic
├── storage.py       # Data persistence
└── README.md        # This documentation
```

## Notes

- Data availability: FY 2018-19 onwards
- Quantity data only available for 8-digit HS codes
- Shows top trading partners for the specified commodity
- Useful for understanding geographic distribution of trade
