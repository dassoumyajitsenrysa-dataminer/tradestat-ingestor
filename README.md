# TradeStat Ingestor

A modular scraper for India's trade statistics from `tradestat.commerce.gov.in`. Extracts data from EIDB (Export-Import Data Bank) and MEIDB (Monthly Export-Import Data Bank).

## Project Structure

```
tradestat-ingestor/
├── src/
│   ├── tradestat_ingestor/
│   │   ├── scrapers/
│   │   │   ├── eidb/                              # Annual trade data scrapers
│   │   │   │   ├── chapter_wise_all_commodities/
│   │   │   │   ├── commodity_wise/
│   │   │   │   ├── commodity_wise_all_countries/
│   │   │   │   ├── commodity_x_country_timeseries/
│   │   │   │   ├── country_wise/
│   │   │   │   ├── region_wise/
│   │   │   │   └── region_wise_all_commodities/
│   │   │   │
│   │   │   └── meidb/                             # Monthly trade data scrapers
│   │   │       ├── commodity_wise/
│   │   │       ├── commodity_wise_all_countries/
│   │   │       └── principal_commodity_wise_all_hscode/
│   │   │
│   │   ├── core/                                  # Core utilities
│   │   │   └── session.py                         # HTTP session with CSRF handling
│   │   ├── config/
│   │   │   └── settings.py                        # Configuration
│   │   └── utils/
│   │       └── constants.py
│   │
│   └── data/raw/                                  # Scraped data output
│       ├── eidb/
│       └── meidb/
│
├── eidb/                                          # Legacy standalone scrapers
├── meidb/
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Available Scrapers

### EIDB (Annual Data: 2018-2024)

| Scraper | Description | CLI |
|---------|-------------|-----|
| `chapter_wise_all_commodities` | All commodities under an HS chapter | `scrape_chapter_wise_all_commodities.py` |
| `commodity_wise` | Trade data for specific HS codes | `scrape_commodity_wise.py` |
| `commodity_wise_all_countries` | HS code trade across all countries | `scrape_cli.py` |
| `commodity_x_country_timeseries` | HS code × country time series | `scrape_commodity_x_country_timeseries.py` |
| `country_wise` | Trade data by country | `scrape_country_wise.py` |
| `region_wise` | Trade data by region | `scrape_region_wise.py` |
| `region_wise_all_commodities` | All commodities for a region | `scrape_region_wise_all_commodities.py` |

### MEIDB (Monthly Data: Jan 2018 - Nov 2025)

| Scraper | Description | CLI |
|---------|-------------|-----|
| `commodity_wise` | Monthly commodity trade data | `scrape_meidb_commodity_wise.py` |
| `commodity_wise_all_countries` | Monthly HS code across all countries | `scrape_meidb_commodity_wise_all_countries.py` |
| `principal_commodity_wise_all_hscode` | All HS codes under a principal commodity | `scrape_meidb_principal_commodity.py` |

## Quick Start

### Running a Scraper

Each scraper folder contains a CLI script. Navigate to the scraper folder and run:

```bash
# EIDB: Country-wise export data
cd src/tradestat_ingestor/scrapers/eidb/country_wise
python scrape_country_wise.py --year 2024 --type export --country usa

# MEIDB: Principal commodity (TEA) export data
cd src/tradestat_ingestor/scrapers/meidb/principal_commodity_wise_all_hscode
python scrape_meidb_principal_commodity.py --type export --commodity A1 --month 11 --year 2025

# List available options
python scrape_meidb_principal_commodity.py --list-commodities
```

### Using as a Library

```python
from tradestat_ingestor.core.session import TradeStatSession
from tradestat_ingestor.scrapers.meidb.principal_commodity_wise_all_hscode import (
    scrape_meidb_principal_commodity_wise_all_hscode,
    parse_meidb_principal_commodity_wise_all_hscode_html,
    save_meidb_principal_commodity_wise_all_hscode_data,
    PRINCIPAL_COMMODITIES,
)

# Initialize session
session = TradeStatSession(
    base_url="https://tradestat.commerce.gov.in",
    user_agent="Mozilla/5.0"
)
state = session.bootstrap("/meidb/principal_commodity_wise_all_HSCode_export")

# Scrape TEA (A1) export data
html = scrape_meidb_principal_commodity_wise_all_hscode(
    session=session.session,
    base_url="https://tradestat.commerce.gov.in",
    commodity_code="A1",
    month=11,
    year=2025,
    trade_type="export",
    state=state
)

# Parse and save
data = parse_meidb_principal_commodity_wise_all_hscode_html(
    html, "A1", "TEA", 11, 2025, "export", "usd", "financial"
)
save_meidb_principal_commodity_wise_all_hscode_data(
    data, "src/data/raw", "export", "A1", 11, 2025, "usd"
)
```

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd tradestat-ingestor

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

## Configuration

Set environment variables in `.env`:

```env
TRADESTAT_BASE_URL=https://tradestat.commerce.gov.in
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

## Data Output

Scraped data is saved as JSON files in `src/data/raw/`:

```
src/data/raw/
├── eidb/
│   ├── country_wise/export/
│   ├── commodity_wise/export/
│   └── ...
└── meidb/
    ├── commodity_wise/export/
    ├── principal_commodity_wise_all_hscode/export/
    └── ...
```

## Data Source

- **Portal**: https://tradestat.commerce.gov.in
- **Provider**: Ministry of Commerce and Industry, Government of India
- **Original Source**: DGCI&S, Kolkata
