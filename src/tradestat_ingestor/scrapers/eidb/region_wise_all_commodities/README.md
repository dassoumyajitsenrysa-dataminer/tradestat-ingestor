# EIDB Region-wise All Commodities Scraper

Scrapes **yearly** trade data from India's Export Import Data Bank (EIDB) for all commodities with a specific country/region.

## Overview

This scraper fetches trade data showing all commodities traded with a specific country/region for a given financial year. Useful for understanding the trade basket with a particular trading partner.

## URL Endpoints

| Trade Type | URL |
|------------|-----|
| Export | `https://tradestat.commerce.gov.in/eidb/region_wise_all_commodities_export` |
| Import | `https://tradestat.commerce.gov.in/eidb/region_wise_all_commodities_import` |

## Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| `trade_type` | Export or Import | `export`, `import` |
| `country_code` | Country/region code | Numeric code (e.g., `423` for USA) |
| `year` | Financial year | `2018` - `2025` |
| `digit_level` | HS code level | `2`, `4`, `6`, `8` |
| `value_type` | Value unit | `usd`, `inr`, `quantity` (8-digit only) |

## Data Structure

### Output Fields

| Field | Description | Example |
|-------|-------------|---------|
| `sno` | Serial number | `1` |
| `hscode` | HS code | `85` |
| `commodity` | Commodity description | `ELECTRICAL MACHINERY...` |
| `value` | Trade value | `12345.67` |
| `share_pct` | Share of bilateral trade (%) | `18.45` |
| `growth_pct` | Year-over-year growth (%) | `22.34` |

### Metadata

| Field | Description |
|-------|-------------|
| `country_code` | Country code |
| `country_name` | Country name |
| `year` | Financial year |
| `digit_level` | HS code level |
| `total_commodities` | Number of commodities traded |

## Usage

### As a Module

```python
from tradestat_ingestor.scrapers.eidb.region_wise_all_commodities import (
    scrape_region_wise_all_commodities,
    parse_region_wise_all_commodities_html
)
from tradestat_ingestor.core.session import TradeStatSession

# Initialize session
session = TradeStatSession(
    base_url="https://tradestat.commerce.gov.in",
    user_agent="Mozilla/5.0..."
)
state = session.bootstrap("/eidb/region_wise_all_commodities_export")

# Scrape data
html = scrape_region_wise_all_commodities(
    session=session.session,
    base_url="https://tradestat.commerce.gov.in",
    country_code="423",
    year="2024",
    digit_level=2,
    trade_type="export",
    value_type="usd",
    state=state
)

# Parse data
data = parse_region_wise_all_commodities_html(html, country_code="423", ...)
```

### CLI Usage

```bash
# All commodities exported to USA at 2-digit level
python scrape_region_wise_all_commodities.py \
    --type export \
    --country 423 \
    --year 2024 \
    --digit-level 2 \
    --value-type usd

# All commodities imported from China at 4-digit level
python scrape_region_wise_all_commodities.py \
    --type import \
    --country 306 \
    --year 2024 \
    --digit-level 4
```

## Output Location

```
src/data/raw/eidb/region_wise_all_commodities/
├── export/
│   ├── level_2/
│   │   └── 423_USA_2024_usd.json
│   ├── level_4/
│   │   └── 423_USA_2024_usd.json
│   └── ...
└── import/
    └── ...
```

## File Structure

```
region_wise_all_commodities/
├── __init__.py      # Module exports
├── scraper.py       # HTTP request handling
├── parser.py        # HTML parsing logic
├── storage.py       # Data persistence
└── README.md        # This documentation
```

## Country Codes

Common country codes:
| Code | Country |
|------|---------|
| 423 | U.S.A. |
| 306 | China |
| 412 | Japan |
| 314 | Germany |
| 526 | U.A.E. |
| 523 | Saudi Arabia |

See `utils/country_codes.py` for the complete list.

## Notes

- Data availability: FY 2018-19 onwards
- Quantity data only available at 8-digit level
- Useful for analyzing trade composition with a specific country
- Can identify key export/import items for bilateral trade analysis
