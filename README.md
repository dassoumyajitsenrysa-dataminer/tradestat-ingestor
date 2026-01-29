# TradeStat Ingestor - Raw Data Scraper

A modular, site-specific scraper for `tradestat.commerce.gov.in` that extracts raw trade data.

## Overview

This project focuses on **scraping raw data only** - each feature has its own dedicated scraper with independent code paths and functions. No parsing or storage logic is included.

## Project Structure

```
src/tradestat_ingestor/
├── scrapers/              # Feature-specific scrapers
│   ├── commodity_wise_all_countries/
│   │   ├── export.py      # Export data scraper
│   │   └── import_scraper.py  # Import data scraper
│   └── [future features...]
├── core/
│   └── session.py         # HTTP session management
├── config/
│   └── settings.py        # Configuration
└── utils/
    ├── constants.py
    └── country_codes.py

examples/                  # Usage examples for each scraper
├── scrape_commodity_export.py
└── scrape_commodity_import.py
```

## Features

### Commodity-wise All Countries (`commodity_wise_all_countries`)

Scrapes trade data for specific HSN codes across all countries.

**Functions:**
- `scrape_commodity_export()` - Fetch export data for an HSN code
- `scrape_commodity_import()` - Fetch import data for an HSN code

## Quick Start

### Basic Usage

```python
from tradestat_ingestor.core.session import TradeStatSession
from tradestat_ingestor.scrapers.commodity_wise_all_countries import scrape_commodity_export
from tradestat_ingestor.config.settings import settings
from tradestat_ingestor.utils.constants import EXPORT_PATH

# Initialize session
session = TradeStatSession(base_url=settings.base_url, user_agent=settings.user_agent)
state = session.bootstrap(EXPORT_PATH)

# Scrape
html = scrape_commodity_export(
    session=session.session,
    base_url=settings.base_url,
    hsn="09011112",
    year="2024",
    state=state
)
```

See `examples/` folder for complete examples.

## Adding New Scrapers

To add a new feature scraper:

1. Create a new directory under `src/tradestat_ingestor/scrapers/`
2. Create separate `.py` files for each endpoint/function
3. Each scraper should be independent with its own session handling
4. Return raw responses (HTML/JSON) without parsing

Example structure for a new feature:
```
scrapers/new_feature/
├── __init__.py
├── scraper_function_1.py
└── scraper_function_2.py
```

## Requirements

See `requirements.txt` for dependencies.

## Configuration

Set environment variables in `.env`:
```
TRADESTAT_BASE_URL=https://tradestat.commerce.gov.in
USER_AGENT=your-user-agent
```
