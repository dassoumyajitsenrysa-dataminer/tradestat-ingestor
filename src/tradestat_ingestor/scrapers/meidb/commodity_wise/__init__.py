"""
MEIDB Commodity-wise scraper (Monthly data).
Fetches monthly export and import commodity data with value/growth information.
"""

from .scraper import (
    scrape_meidb_commodity_wise,
    scrape_meidb_commodity_wise_all,
    fetch_commodity_wise_data,
    COMMODITY_WISE_EXPORT_PATH,
    COMMODITY_WISE_IMPORT_PATH,
    EXPORT_URL,
    IMPORT_URL,
    MONTHS
)
from .parser import (
    parse_meidb_commodity_wise_html,
    parse_commodity_wise_html
)
from .storage import (
    save_meidb_commodity_wise_data,
    save_meidb_all_commodities_data,
    get_output_dir
)

__all__ = [
    # New API
    "scrape_meidb_commodity_wise",
    "scrape_meidb_commodity_wise_all",
    "parse_meidb_commodity_wise_html",
    "save_meidb_commodity_wise_data",
    "save_meidb_all_commodities_data",
    "get_output_dir",
    "COMMODITY_WISE_EXPORT_PATH",
    "COMMODITY_WISE_IMPORT_PATH",
    "MONTHS",
    # Legacy API
    "fetch_commodity_wise_data",
    "parse_commodity_wise_html",
    "EXPORT_URL",
    "IMPORT_URL"
]
