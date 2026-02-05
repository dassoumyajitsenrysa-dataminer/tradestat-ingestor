"""Parser for MEIDB Commodity-wise data."""

from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime

MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
          7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}


def parse_commodity_response(
    html: str, hscode: str, month: int, year: int, trade_type: str, value_type: str, year_type: str
) -> Optional[Dict[str, Any]]:
    try:
        soup = BeautifulSoup(html, "lxml")
        commodities = _extract_commodities(soup)
        india_total = _extract_india_total(soup)
        
        return {
            "metadata": {
                "extraction": {
                    "scraped_at": datetime.now().isoformat(),
                    "feature": "meidb_commodity_wise",
                    "hscode": hscode,
                    "digit_level": len(hscode),
                    "month": month,
                    "month_name": MONTHS.get(month),
                    "year": year,
                    "trade_type": trade_type,
                    "value_type": value_type,
                    "year_type": year_type,
                },
            },
            "commodities": commodities,
            "india_total": india_total,
            "data_quality": {"total_records": len(commodities)},
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
        if len(cells) < 6:
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
            "month_prev_year": _parse_number(cells[3].get_text(strip=True)),
            "month_curr_year": _parse_number(cells[4].get_text(strip=True)),
            "month_yoy_growth_pct": _parse_number(cells[5].get_text(strip=True)),
            "cumulative_prev_year": _parse_number(cells[6].get_text(strip=True)) if len(cells) > 6 else None,
            "cumulative_curr_year": _parse_number(cells[7].get_text(strip=True)) if len(cells) > 7 else None,
            "cumulative_yoy_growth_pct": _parse_number(cells[8].get_text(strip=True)) if len(cells) > 8 else None,
        })
    return commodities


def _extract_india_total(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    table = soup.find("table")
    if not table:
        return None
    for row in table.find_all("tr"):
        if "India" in row.get_text() and "Total" in row.get_text():
            cells = row.find_all("td")
            if len(cells) >= 6:
                return {
                    "month_prev_year": _parse_number(cells[3].get_text(strip=True)),
                    "month_curr_year": _parse_number(cells[4].get_text(strip=True)),
                    "month_yoy_growth_pct": _parse_number(cells[5].get_text(strip=True)),
                    "cumulative_prev_year": _parse_number(cells[6].get_text(strip=True)) if len(cells) > 6 else None,
                    "cumulative_curr_year": _parse_number(cells[7].get_text(strip=True)) if len(cells) > 7 else None,
                    "cumulative_yoy_growth_pct": _parse_number(cells[8].get_text(strip=True)) if len(cells) > 8 else None,
                }
    return None


def _parse_number(text: str) -> Optional[float]:
    if not text or text in ["-", "NA"]:
        return None
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return None
