# EIDB Commodity x Country Timeseries Scraper

Scrapes **yearly timeseries** trade data from India's Export Import Data Bank (EIDB) for a specific commodity (HS code) and country combination across multiple years.

## Overview

This scraper fetches historical trade data for a specific HS code and country, allowing analysis of trade trends over time.

## URL Endpoints

| Trade Type | URL |
|------------|-----|
| Export | `https://tradestat.commerce.gov.in/eidb/commodity_country_timeseries_export` |
| Import | `https://tradestat.commerce.gov.in/eidb/commodity_country_timeseries_import` |

## Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| `trade_type` | Export or Import | `export`, `import` |
| `hscode` | HS code | 2, 4, 6, or 8 digit code |
| `country_code` | Country code | Numeric code (e.g., `423` for USA) |
| `from_year` | Start year | `2018` - `2025` |
| `to_year` | End year | `2018` - `2025` |
| `value_type` | Value unit | `usd`, `inr`, `quantity` (8-digit only) |

## Data Structure

### Output Fields

| Field | Description | Example |
|-------|-------------|---------|
| `year` | Financial year | `2024` |
| `value` | Trade value | `1234.56` |
| `share_pct` | Share of total trade (%) | `2.34` |
| `growth_pct` | Year-over-year growth (%) | `15.67` |

### Metadata

| Field | Description |
|-------|-------------|
| `hscode` | HS code queried |
| `commodity` | Commodity description |
| `country_code` | Country code |
| `country_name` | Country name |
| `from_year` | Start of time range |
| `to_year` | End of time range |

## Usage

### As a Module

```python
from tradestat_ingestor.scrapers.eidb.commodity_x_country_timeseries import (
    scrape_commodity_country_timeseries,
    parse_timeseries_html
)
from tradestat_ingestor.core.session import TradeStatSession

# Initialize session
session = TradeStatSession(
    base_url="https://tradestat.commerce.gov.in",
    user_agent="Mozilla/5.0..."
)
state = session.bootstrap("/eidb/commodity_country_timeseries_export")

# Scrape data
html = scrape_commodity_country_timeseries(
    session=session.session,
    base_url="https://tradestat.commerce.gov.in",
    hscode="84713010",
    country_code="423",
    from_year="2020",
    to_year="2025",
    trade_type="export",
    value_type="usd",
    state=state
)

# Parse data
data = parse_timeseries_html(html, hscode="84713010", country_code="423", ...)
```

### CLI Usage

```bash
# Export timeseries for HS 84713010 to USA (423)
python scrape_commodity_x_country_timeseries.py \
    --type export \
    --hscode 84713010 \
    --country 423 \
    --from-year 2020 \
    --to-year 2025 \
    --value-type usd

# Import timeseries
python scrape_commodity_x_country_timeseries.py \
    --type import \
    --hscode 27090000 \
    --country 523 \
    --from-year 2018 \
    --to-year 2025
```

## Output Location

```
src/data/raw/eidb/commodity_x_country_timeseries/
├── export/
│   └── hs84713010_423_U_S_A_2020-2025_usd.json
└── import/
    └── hs27090000_523_SAUDI_ARABIA_2018-2025_usd.json
```

## File Structure

```
commodity_x_country_timeseries/
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

See `utils/country_codes.py` for the complete list.

## Notes

- Data availability: FY 2018-19 onwards
- Quantity data only available for 8-digit HS codes
- Timeseries provides year-by-year breakdown for trend analysis
