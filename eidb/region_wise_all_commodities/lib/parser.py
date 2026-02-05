"""Parser for EIDB Region-wise All Commodities data."""

from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime


def parse_region_commodities_response(
    html: str, country_code: str, country_name: str, year: str, digit_level: int, trade_type: str, value_type: str
) -> Optional[Dict[str, Any]]:
    try:
        soup = BeautifulSoup(html, "lxml")
        commodities = _extract_commodities(soup)
        total = _extract_total(soup)
        
        return {
            "metadata": {
                "extraction": {
                    "scraped_at": datetime.now().isoformat(),
                    "feature": "eidb_region_wise_all_commodities",
                    "country_code": country_code,
                    "country_name": country_name,
                    "year": int(year),
                    "digit_level": digit_level,
                    "trade_type": trade_type,
                    "value_type": value_type,
                },
            },
            "commodities": commodities,
            "total": total,
            "data_quality": {"total_commodities": len(commodities)},
        }
    except Exception as e:
        logger.error(f"Error parsing: {e}")
        return None


def _extract_commodities(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    commodities = []
    table = soup.find("table")
    if not table:
        return commodities
    
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        sno = cells[0].get_text(strip=True)
        if not sno.isdigit():
            continue
        if "total" in cells[1].get_text(strip=True).lower():
            continue
        
        commodities.append({
            "sno": int(sno),
            "hscode": cells[1].get_text(strip=True),
            "commodity": cells[2].get_text(strip=True),
            "value": _parse_number(cells[3].get_text(strip=True)),
            "share_pct": _parse_number(cells[4].get_text(strip=True)) if len(cells) > 4 else None,
            "growth_pct": _parse_number(cells[5].get_text(strip=True)) if len(cells) > 5 else None,
        })
    return commodities


def _extract_total(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    table = soup.find("table")
    if not table:
        return None
    for row in table.find_all("tr"):
        if "Total" in row.get_text():
            cells = row.find_all("td")
            if len(cells) >= 4:
                return {"total_value": _parse_number(cells[3].get_text(strip=True))}
    return None


def _parse_number(text: str) -> Optional[float]:
    if not text or text in ["-", "NA"]:
        return None
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return None
