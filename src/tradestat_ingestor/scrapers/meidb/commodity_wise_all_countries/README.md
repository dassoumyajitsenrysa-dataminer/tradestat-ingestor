# MEIDB Commodity-wise All Countries Scraper

Scrapes **monthly** trade data from India's Monthly Export Import Data Bank (MEIDB) for a specific commodity showing breakdown by all trading partner countries.

## Overview

This scraper fetches monthly trade data for a specific HS code, showing the value and growth for each country that India trades with. Useful for understanding geographic distribution of trade for a commodity on a monthly basis.

## URL Endpoints

| Trade Type | URL |
|------------|-----|
| Export | `https://tradestat.commerce.gov.in/meidb/commodity_wise_all_countries_export` |
| Import | `https://tradestat.commerce.gov.in/meidb/commodity_wise_all_countries_import` |

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

### Output Fields

| Field | Description | Example |
|-------|-------------|---------|
| `sno` | Serial number | `1` |
| `country` | Country name | `U.S.A.` |
| `month_prev_year` | Same month, previous year value | `523.45` |
| `month_curr_year` | Same month, current year value | `678.90` |
| `month_yoy_growth_pct` | Month YoY growth (%) | `29.71` |
| `cumulative_prev_year` | Apr-Month, previous year | `4567.89` |
| `cumulative_curr_year` | Apr-Month, current year | `5678.90` |
| `cumulative_yoy_growth_pct` | Cumulative YoY growth (%) | `24.32` |

### Metadata

| Field | Description |
|-------|-------------|
| `hscode` | HS code queried |
| `commodity` | Commodity description |
| `month` | Month number |
| `month_name` | Month name |
| `year` | Year |
| `total_countries` | Number of trading partners |

## Usage

### As a Module

```python
from tradestat_ingestor.scrapers.meidb.commodity_wise_all_countries import (
    scrape_meidb_commodity_wise_all_countries,
    parse_meidb_commodity_wise_all_countries_html
)
from tradestat_ingestor.core.session import TradeStatSession

# Initialize session
session = TradeStatSession(
    base_url="https://tradestat.commerce.gov.in",
    user_agent="Mozilla/5.0..."
)
state = session.bootstrap("/meidb/commodity_wise_all_countries_export")

# Scrape data
html = scrape_meidb_commodity_wise_all_countries(
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
data = parse_meidb_commodity_wise_all_countries_html(
    html, hscode="85", month=11, year=2025,
    trade_type="export", value_type="usd", year_type="financial"
)
```

### CLI Usage

```bash
# Export for HS 85 to all countries, November 2025
python scrape_meidb_commodity_wise_all_countries.py \
    --type export \
    --hscode 85 \
    --month 11 \
    --year 2025 \
    --value-type usd \
    --year-type financial

# Import at 8-digit level with quantity
python scrape_meidb_commodity_wise_all_countries.py \
    --type import \
    --hscode 27090000 \
    --month 11 \
    --year 2025 \
    --value-type quantity

# Calendar year option
python scrape_meidb_commodity_wise_all_countries.py \
    --type export \
    --hscode 8471 \
    --month 6 \
    --year 2025 \
    --year-type calendar
```

## Output Location

```
src/data/raw/meidb/commodity_wise_all_countries/
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
commodity_wise_all_countries/
├── __init__.py      # Module exports
├── scraper.py       # HTTP request handling
├── parser.py        # HTML parsing logic
├── storage.py       # Data persistence
└── README.md        # This documentation
```

## Understanding the Data

### Year-over-Year Comparison by Country

For each country, the data shows:
- **{Month}-{PrevYear} (R)** → `month_prev_year`: Trade value same month last year
- **{Month}-{CurrYear} (F)** → `month_curr_year`: Trade value current month
- **% Growth** → `month_yoy_growth_pct`: Year-over-year growth for that month

### Cumulative by Country

- **Apr-{Month} {PrevYear} (R)** → `cumulative_prev_year`: Cumulative trade, last FY
- **Apr-{Month} {CurrYear} (F)** → `cumulative_curr_year`: Cumulative trade, current FY
- **% Growth** → `cumulative_yoy_growth_pct`: Cumulative YoY growth

## Use Cases

1. **Market Analysis**: Identify top destination/source countries for a commodity
2. **Trend Tracking**: Monitor monthly changes in trade with specific countries
3. **Diversification Study**: Analyze concentration of trade across countries
4. **Growth Opportunities**: Find fast-growing markets for exports

## Notes

- Data availability: January 2018 to November 2025
- Revised Final data available up to March 2025
- Final data available up to November 2025
- Quantity data only available for 8-digit HS codes
- Shows all countries with any trade value (may include many small values)
