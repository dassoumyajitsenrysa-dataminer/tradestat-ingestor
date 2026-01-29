"""
Configuration for country-wise trade data scraping.
Handles endpoint paths and data directories for country-level trade statistics.
"""

from pathlib import Path

# Website URL endpoints
COUNTRY_TRADE_PATH = "/eidb/country_wise_ttrade"

# Local data storage paths
DATA_ROOT = Path(__file__).parent.parent.parent / "data"
COUNTRY_DATA_DIR = DATA_ROOT / "country_wise"

# Ensure directories exist
COUNTRY_DATA_DIR.mkdir(parents=True, exist_ok=True)
