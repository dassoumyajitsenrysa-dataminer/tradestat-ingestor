"""Parser module for EIDB Region-wise data."""

from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime


def parse_region_wise_response(
    html: str, hscode: str, year: str, trade_type: str, value_type: str
) -> Optional[Dict[str, Any]]:
    try:
        soup = BeautifulSoup(html, "lxml")
        countries = _extract_countries(soup)
        total = _extract_total(soup)
        commodity = _extract_commodity(soup)
        
        return {
            "metadata": {
                "extraction": {
                    "scraped_at": datetime.now().isoformat(),
                    "feature": "eidb_region_wise",
                    "hscode": hscode,
                    "digit_level": len(hscode),
                    "commodity": commodity,
                    "year": int(year),
                    "trade_type": trade_type,
                    "value_type": value_type,
                },
            },
            "countries": countries,
            "total": total,
            "data_quality": {"total_countries": len(countries)},
        }
    except Exception as e:
        logger.error(f"Error parsing region-wise: {e}")
        return None


def _extract_commodity(soup: BeautifulSoup) -> str:
    # Try to extract commodity name from page
    return ""


def _extract_countries(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    countries = []
    table = soup.find("table")
    if not table:
        return countries
    
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        sno = cells[0].get_text(strip=True)
        if not sno.isdigit():
            continue
        if "total" in cells[1].get_text(strip=True).lower():
            continue
        
        countries.append({
            "sno": int(sno),
            "country": cells[1].get_text(strip=True),
            "value": _parse_number(cells[2].get_text(strip=True)),
            "share_pct": _parse_number(cells[3].get_text(strip=True)),
            "growth_pct": _parse_number(cells[4].get_text(strip=True)) if len(cells) > 4 else None,
        })
    return countries


def _extract_total(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    table = soup.find("table")
    if not table:
        return None
    for row in table.find_all("tr"):
        if "Total" in row.get_text():
            cells = row.find_all("td")
            if len(cells) >= 3:
                return {
                    "total_value": _parse_number(cells[2].get_text(strip=True)),
                    "total_growth_pct": _parse_number(cells[4].get_text(strip=True)) if len(cells) > 4 else None,
                }
    return None


def _parse_number(text: str) -> Optional[float]:
    if not text or text in ["-", "NA"]:
        return None
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return None
