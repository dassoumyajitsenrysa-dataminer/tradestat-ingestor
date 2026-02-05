"""
Parser module for EIDB Chapter-wise All Commodities data.
Handles HTML parsing and data extraction.
"""

import re
import hashlib
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime


def parse_chapter_wise_response(
    html: str,
    year: str,
    digit_level: int,
    trade_type: str,
    value_type: str
) -> Optional[Dict[str, Any]]:
    """
    Parse chapter-wise all commodities HTML response.
    
    Args:
        html: HTML response content
        year: Financial year
        digit_level: HS code level (2, 4, 6, 8)
        trade_type: "export" or "import"
        value_type: "usd" or "inr"
        
    Returns:
        Parsed data dictionary or None if parsing fails
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        extract_start = datetime.now()
        
        # Extract commodities
        commodities = _extract_commodities(soup)
        
        # Extract India's total
        india_total = _extract_india_total(soup)
        
        # Calculate metrics
        total_records = len(commodities)
        records_with_data = sum(1 for c in commodities if c.get('value') is not None)
        completeness = (records_with_data / total_records * 100) if total_records > 0 else 0
        
        # Value labels
        value_labels = {"usd": "US $ Million", "inr": "₹ Crore"}
        
        # Build result
        parsed_data = {"commodities": commodities, "india_total": india_total}
        checksum = hashlib.md5(str(parsed_data).encode()).hexdigest()
        
        return {
            "metadata": {
                "extraction": {
                    "scraped_at": datetime.now().isoformat(),
                    "feature": "eidb_chapter_wise_all_commodities",
                    "year": int(year),
                    "digit_level": digit_level,
                    "trade_type": trade_type,
                    "value_type": value_type,
                    "value_unit": value_labels.get(value_type, "US $ Million"),
                    "source_url": f"https://tradestat.commerce.gov.in/eidb/chapter_wise_{trade_type}",
                },
                "data": {
                    "data_source": "DGCI&S",
                    "data_provider": "Ministry of Commerce and Industry, Government of India",
                    "temporal_granularity": "Yearly",
                },
            },
            "commodities": commodities,
            "india_total": india_total,
            "data_quality": {
                "total_records": total_records,
                "records_with_complete_data": records_with_data,
                "completeness_percent": round(completeness, 2),
            },
        }
    except Exception as e:
        logger.error(f"Error parsing chapter-wise response: {e}")
        return None


def _extract_commodities(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract commodities from HTML table."""
    commodities = []
    table = soup.find("table")
    if not table:
        return commodities
    
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        
        sno = cells[0].get_text(strip=True)
        if not sno.isdigit():
            continue
        
        # Skip total rows
        if "total" in cells[1].get_text(strip=True).lower():
            continue
        
        commodities.append({
            "sno": int(sno),
            "hscode": cells[1].get_text(strip=True),
            "commodity": cells[2].get_text(strip=True),
            "value": _parse_number(cells[3].get_text(strip=True)),
            "share_pct": _parse_number(cells[4].get_text(strip=True)),
            "growth_pct": _parse_number(cells[5].get_text(strip=True)) if len(cells) > 5 else None,
        })
    
    return commodities


def _extract_india_total(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """Extract India's total from the table."""
    table = soup.find("table")
    if not table:
        return None
    
    for row in table.find_all("tr"):
        if "India" in row.get_text() and "Total" in row.get_text():
            cells = row.find_all("td")
            if len(cells) >= 4:
                return {
                    "total_value": _parse_number(cells[3].get_text(strip=True)) if len(cells) > 3 else None,
                    "total_growth_pct": _parse_number(cells[5].get_text(strip=True)) if len(cells) > 5 else None,
                }
    return None


def _parse_number(text: str) -> Optional[float]:
    """Parse a number from text."""
    if not text or text in ["-", "NA", "N/A"]:
        return None
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return None
