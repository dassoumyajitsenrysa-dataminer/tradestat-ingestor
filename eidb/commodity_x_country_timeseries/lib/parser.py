"""Parser module for EIDB Commodity x Country Timeseries data."""

from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime


def parse_timeseries_response(
    html: str,
    hscode: str,
    country_code: str,
    country_name: str,
    from_year: str,
    to_year: str,
    trade_type: str,
    value_type: str
) -> Optional[Dict[str, Any]]:
    """Parse timeseries HTML response."""
    try:
        soup = BeautifulSoup(html, "lxml")
        timeseries = _extract_timeseries(soup)
        
        return {
            "metadata": {
                "extraction": {
                    "scraped_at": datetime.now().isoformat(),
                    "feature": "eidb_commodity_x_country_timeseries",
                    "hscode": hscode,
                    "country_code": country_code,
                    "country_name": country_name,
                    "from_year": int(from_year),
                    "to_year": int(to_year),
                    "trade_type": trade_type,
                    "value_type": value_type,
                },
            },
            "timeseries": timeseries,
            "data_quality": {
                "total_years": len(timeseries),
            },
        }
    except Exception as e:
        logger.error(f"Error parsing timeseries: {e}")
        return None


def _extract_timeseries(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract timeseries data from HTML table."""
    timeseries = []
    table = soup.find("table")
    if not table:
        return timeseries
    
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        
        year_text = cells[0].get_text(strip=True)
        if not year_text.isdigit():
            continue
        
        timeseries.append({
            "year": int(year_text),
            "value": _parse_number(cells[1].get_text(strip=True)),
            "growth_pct": _parse_number(cells[2].get_text(strip=True)) if len(cells) > 2 else None,
        })
    
    return timeseries


def _parse_number(text: str) -> Optional[float]:
    """Parse a number from text."""
    if not text or text in ["-", "NA"]:
        return None
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return None
