"""Parser for MEIDB Commodity-wise All Countries data."""

from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime

MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
          7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}


def parse_commodity_countries_response(
    html: str, hscode: str, month: int, year: int, trade_type: str, value_type: str, year_type: str
) -> Optional[Dict[str, Any]]:
    try:
        soup = BeautifulSoup(html, "lxml")
        countries = _extract_countries(soup)
        total = _extract_total(soup)
        
        return {
            "metadata": {
                "extraction": {
                    "scraped_at": datetime.now().isoformat(),
                    "feature": "meidb_commodity_wise_all_countries",
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
            "countries": countries,
            "total": total,
            "data_quality": {"total_countries": len(countries)},
        }
    except Exception as e:
        logger.error(f"Error parsing: {e}")
        return None


def _extract_countries(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    countries = []
    table = soup.find("table")
    if not table:
        return countries
    
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        sno = cells[0].get_text(strip=True)
        if not sno.isdigit():
            continue
        if "total" in cells[1].get_text(strip=True).lower():
            continue
        
        countries.append({
            "sno": int(sno),
            "country": cells[1].get_text(strip=True),
            "month_prev_year": _parse_number(cells[2].get_text(strip=True)),
            "month_curr_year": _parse_number(cells[3].get_text(strip=True)),
            "month_yoy_growth_pct": _parse_number(cells[4].get_text(strip=True)),
            "cumulative_prev_year": _parse_number(cells[5].get_text(strip=True)) if len(cells) > 5 else None,
            "cumulative_curr_year": _parse_number(cells[6].get_text(strip=True)) if len(cells) > 6 else None,
            "cumulative_yoy_growth_pct": _parse_number(cells[7].get_text(strip=True)) if len(cells) > 7 else None,
        })
    return countries


def _extract_total(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    table = soup.find("table")
    if not table:
        return None
    for row in table.find_all("tr"):
        text = row.get_text()
        if "Total" in text:
            cells = row.find_all("td")
            if len(cells) >= 5:
                return {
                    "month_prev_year": _parse_number(cells[2].get_text(strip=True)) if len(cells) > 2 else None,
                    "month_curr_year": _parse_number(cells[3].get_text(strip=True)) if len(cells) > 3 else None,
                    "month_yoy_growth_pct": _parse_number(cells[4].get_text(strip=True)) if len(cells) > 4 else None,
                    "cumulative_prev_year": _parse_number(cells[5].get_text(strip=True)) if len(cells) > 5 else None,
                    "cumulative_curr_year": _parse_number(cells[6].get_text(strip=True)) if len(cells) > 6 else None,
                    "cumulative_yoy_growth_pct": _parse_number(cells[7].get_text(strip=True)) if len(cells) > 7 else None,
                }
    return None


def _parse_number(text: str) -> Optional[float]:
    if not text or text in ["-", "NA"]:
        return None
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return None
