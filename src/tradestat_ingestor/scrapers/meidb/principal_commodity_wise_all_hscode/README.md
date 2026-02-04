# MEIDB Principal Commodity-wise All HSCode Scraper

This scraper fetches all HSCode breakdowns for a given principal commodity from the MEIDB (Monthly Export-Import Data Bank) on the Government of India's TradeStat portal.

## Overview

The Principal Commodity-wise All HSCode report provides:
- All HS codes that belong to a principal commodity category
- Monthly comparison data (current vs previous year)
- Cumulative financial/calendar year data
- Year-over-year growth percentages

## Usage

```python
from tradestat_ingestor.scrapers.meidb.principal_commodity_wise_all_hscode import (
    scrape_meidb_principal_commodity_wise_all_hscode,
    parse_meidb_principal_commodity_wise_all_hscode_html,
    save_meidb_principal_commodity_wise_all_hscode_data,
    PRINCIPAL_COMMODITIES,
    get_commodity_name,
)
from tradestat_ingestor.core.session import create_session, bootstrap_session

# Create session
session = create_session()
state = bootstrap_session(session, base_url, "/meidb/principal_commodity_wise_all_HSCode_export")

# Scrape TEA (A1) export data for November 2025
html = scrape_meidb_principal_commodity_wise_all_hscode(
    session=session,
    base_url="https://tradestat.commerce.gov.in",
    commodity_code="A1",
    month=11,
    year=2025,
    trade_type="export",
    value_type="usd",
    year_type="financial",
    state=state
)

# Parse the response
data = parse_meidb_principal_commodity_wise_all_hscode_html(
    html=html,
    commodity_code="A1",
    commodity_name="TEA",
    month=11,
    year=2025,
    trade_type="export",
    value_type="usd",
    year_type="financial"
)

# Save the data
output_path = save_meidb_principal_commodity_wise_all_hscode_data(
    data=data,
    base_dir="src/data/raw",
    trade_type="export",
    commodity_code="A1",
    month=11,
    year=2025,
    value_type="usd"
)
```

## Principal Commodity Codes

Some commonly used codes:

| Code | Name |
|------|------|
| A1 | TEA |
| A2 | COFFEE |
| B1 | SPICES |
| E7 | MARINE PRODUCTS |
| L3 | IRON AND STEEL |
| N4 | ELECTRIC MACHINERY AND EQUIPMENT |
| O5 | MOTOR VEHICLE/CARS |
| P4 | TELECOM INSTRUMENTS |
| S6 | PETROLEUM PRODUCTS |

Use `PRINCIPAL_COMMODITIES` dictionary to see the complete list.

## Output Format

Data is saved as JSON with the following structure:

```json
{
  "metadata": {
    "extraction": {
      "scraped_at": "2026-02-04T...",
      "feature": "meidb_principal_commodity_wise_all_hscode",
      "principal_commodity_code": "A1",
      "principal_commodity_name": "TEA",
      "month": 11,
      "year": 2025,
      "trade_type": "export",
      "value_type": "usd"
    }
  },
  "principal_commodity": {
    "code": "A1",
    "name": "TEA"
  },
  "commodities": [
    {
      "sno": 1,
      "hscode": "09021010",
      "description": "TEA GREEN IN PACKETS NT EXCDNG 25 GRAMS",
      "month_prev_year": 0.09,
      "month_curr_year": 0.18,
      "month_yoy_growth_pct": 92.59,
      "cumulative_prev_year": 1.70,
      "cumulative_curr_year": 1.49,
      "cumulative_yoy_growth_pct": -12.49
    }
  ],
  "total": {
    "label": "India's Total Export of TEA",
    "month_prev_year": 78.27,
    "month_curr_year": 91.66,
    "cumulative_prev_year": 604.41,
    "cumulative_curr_year": 697.43
  }
}
```

## Data Source

- **Portal**: https://tradestat.commerce.gov.in
- **Database**: MEIDB (Monthly Export-Import Data Bank)
- **Provider**: Ministry of Commerce and Industry, Government of India
- **Original Source**: DGCI&S, Kolkata
