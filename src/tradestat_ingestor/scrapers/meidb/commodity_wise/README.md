# MEIDB Commodity-wise Scraper

Scrapes **monthly** trade data from India's Monthly Export Import Data Bank (MEIDB) for commodities at various HS code levels.

## Overview

This scraper fetches monthly commodity trade statistics, providing year-over-year comparison for a specific month and cumulative data from April to the selected month.

## URL Endpoints

| Trade Type | URL |
|------------|-----|
| Export | `https://tradestat.commerce.gov.in/meidb/commoditywise_export` |
| Import | `https://tradestat.commerce.gov.in/meidb/commoditywise_import` |

## Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| `trade_type` | Export or Import | `export`, `import` |
| `hscode` | HS code | 2, 4, 6, or 8 digit code |
| `month` | Month | `1` - `12` (January to December) |
| `year` | Year | `2018` - `2025` |
| `value_type` | Value unit | `usd` (US $ Million), `inr` (₹ Crore), `quantity` (8-digit only) |
| `year_type` | Year type | `financial` (Apr-Mar), `calendar` (Jan-Dec) |

## Data Structure

### Output Fields (Year-over-Year Comparison)

| Field | Description | Example |
|-------|-------------|---------|
| `sno` | Serial number | `1` |
| `hscode` | HS code | `85` |
| `commodity` | Commodity description | `ELECTRICAL MACHINERY...` |
| `month_prev_year` | Same month, previous year value | `3914.27` |
| `month_curr_year` | Same month, current year value | `5270.89` |
| `month_yoy_growth_pct` | Month YoY growth (%) | `34.66` |
| `cumulative_prev_year` | Apr-Month, previous year | `25869.39` |
| `cumulative_curr_year` | Apr-Month, current year | `34931.94` |
| `cumulative_yoy_growth_pct` | Cumulative YoY growth (%) | `35.03` |

### India Total

Same fields as above for India's total trade.

## Usage

### As a Module

```python
from tradestat_ingestor.scrapers.meidb.commodity_wise import (
    scrape_meidb_commodity_wise,
    parse_meidb_commodity_wise_html
)
from tradestat_ingestor.core.session import TradeStatSession

# Initialize session
session = TradeStatSession(
    base_url="https://tradestat.commerce.gov.in",
    user_agent="Mozilla/5.0..."
)
state = session.bootstrap("/meidb/commoditywise_export")

# Scrape data
html = scrape_meidb_commodity_wise(
    session=session.session,
    base_url="https://tradestat.commerce.gov.in",
    hscode="85",
    month=11,
    year=2025,
    trade_type="export",
    value_type="usd",
    year_type="financial",
    state=state
)

# Parse data
data = parse_meidb_commodity_wise_html(
    html, hscode="85", month=11, year=2025,
    trade_type="export", value_type="usd", year_type="financial"
)
```

### CLI Usage

```bash
# Export for HS 85, November 2025, Financial Year
python scrape_meidb_commodity_wise.py \
    --type export \
    --hscode 85 \
    --month 11 \
    --year 2025 \
    --value-type usd \
    --year-type financial

# Import for 8-digit code with quantity
python scrape_meidb_commodity_wise.py \
    --type import \
    --hscode 84713010 \
    --month 11 \
    --year 2025 \
    --value-type quantity

# All 4-digit commodities
python scrape_meidb_commodity_wise.py \
    --type export \
    --all \
    --digit-level 4 \
    --month 11 \
    --year 2025
```

## Output Location

```
src/data/raw/meidb/commodity_wise/
├── export/
│   ├── level_2/
│   │   └── 85_nov_2025_usd.json
│   ├── level_4/
│   │   └── 8471_nov_2025_usd.json
│   ├── level_6/
│   │   └── 847130_nov_2025_usd.json
│   └── level_8/
│       └── 84713010_nov_2025_usd.json
└── import/
    └── ...
```

## File Structure

```
commodity_wise/
├── __init__.py      # Module exports
├── scraper.py       # HTTP request handling
├── parser.py        # HTML parsing logic
├── storage.py       # Data persistence
└── README.md        # This documentation
```

## Understanding the Data

### Year-over-Year Comparison

The MEIDB provides YoY comparison:
- **Nov-2024 (R)** → `month_prev_year`: Same month last year (Revised)
- **Nov-2025 (F)** → `month_curr_year`: Current month this year (Final)
- **% Growth** → `month_yoy_growth_pct`: Year-over-year growth

### Cumulative Comparison

- **Apr-Nov 2024 (R)** → `cumulative_prev_year`: Apr to current month, last year
- **Apr-Nov 2025 (F)** → `cumulative_curr_year`: Apr to current month, this year
- **% Growth** → `cumulative_yoy_growth_pct`: Cumulative YoY growth

### Data Status Indicators
- **(R)** = Revised Final - Finalized historical data
- **(F)** = Final - Current period data (may be updated)

## Notes

- Data availability: January 2018 to November 2025
- Revised Final data available up to March 2025
- Final data available up to November 2025
- Quantity data only available for 8-digit HS codes
- Financial year runs April to March
