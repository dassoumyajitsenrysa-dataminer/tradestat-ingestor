"""
Parser for MEIDB Principal Commodity-wise All HSCode data.
"""

from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime
import re

MONTHS = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

VALUE_UNITS = {
    "usd": "US $ Million",
    "inr": "₹ Crore",
    "quantity": "Quantity in thousands"
}


def parse_meidb_principal_commodity_wise_all_hscode_html(
    html: str,
    commodity_code: str,
    commodity_name: str,
    month: int,
    year: int,
    trade_type: str,
    value_type: str,
    year_type: str
) -> Optional[Dict[str, Any]]:
    """
    Parse the HTML response for principal commodity wise all HSCode data.

    Args:
        html: Raw HTML response
        commodity_code: Principal commodity code (e.g., A1)
        commodity_name: Principal commodity name (e.g., TEA)
        month: Month (1-12)
        year: Year
        trade_type: "export" or "import"
        value_type: "usd", "inr", or "quantity"
        year_type: "financial" or "calendar"

    Returns:
        Parsed data dictionary or None if parsing fails
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        
        # Extract column headers
        column_headers = _extract_column_headers(soup)
        
        # Extract commodity details (HSCode wise breakdown)
        commodities = _extract_commodities(soup)
        
        # Extract total row
        total = _extract_total(soup)
        
        # Extract report date if available
        report_date = _extract_report_date(soup)
        
        return {
            "metadata": {
                "extraction": {
                    "scraped_at": datetime.now().isoformat(),
                    "feature": "meidb_principal_commodity_wise_all_hscode",
                    "principal_commodity_code": commodity_code,
                    "principal_commodity_name": commodity_name,
                    "month": month,
                    "month_name": MONTHS.get(month),
                    "year": year,
                    "period": f"{MONTHS.get(month)} {year}",
                    "trade_type": trade_type,
                    "value_type": value_type,
                    "value_unit": VALUE_UNITS.get(value_type.lower(), "US $ Million"),
                    "year_type": year_type,
                    "source_url": f"https://tradestat.commerce.gov.in/meidb/principal_commodity_wise_all_HSCode_{trade_type}",
                    "report_date": report_date,
                    "response_size_bytes": len(html),
                    "extraction_method": "HTTP_POST_with_CSRF"
                },
                "data": {
                    "data_source": "DGCI&S (Directorate General of Commercial Intelligence and Statistics)",
                    "data_provider": "Ministry of Commerce and Industry, Government of India",
                    "data_classification": "PUBLIC",
                    "data_category": "Trade_Statistics",
                    "temporal_granularity": "Monthly",
                    "geographic_coverage": "India",
                    "update_frequency": "Monthly"
                },
                "version": {
                    "schema_version": "2.0",
                    "scraper_version": "1.0",
                    "api_compatibility": "TRADESTAT_2025",
                    "last_schema_update": datetime.now().strftime("%Y-%m-%d")
                },
                "lineage": {
                    "data_source_url": f"https://tradestat.commerce.gov.in/meidb/principal_commodity_wise_all_HSCode_{trade_type}",
                    "extraction_point": "meidb_principal_commodity_wise_all_hscode",
                    "processing_chain": ["scrape_html", "parse_html", "extract_table", "validate_data"],
                    "transformations_applied": ["HTML_to_JSON", "Value_Normalization", "Missing_Data_Handling"]
                }
            },
            "principal_commodity": {
                "code": commodity_code,
                "name": commodity_name
            },
            "column_headers": column_headers,
            "commodities": commodities,
            "total": total,
            "data_quality": {
                "total_hscodes": len(commodities),
                "has_total": total is not None
            }
        }
    except Exception as e:
        logger.error(f"Error parsing principal commodity data: {e}")
        return None


def _extract_column_headers(soup: BeautifulSoup) -> List[str]:
    """Extract column headers from the table."""
    headers = []
    table = soup.find("table")
    if not table:
        return headers
    
    header_row = table.find("tr")
    if header_row:
        for th in header_row.find_all(["th", "td"]):
            headers.append(th.get_text(strip=True))
    return headers


def _extract_commodities(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract commodity rows from the table."""
    commodities = []
    table = soup.find("table")
    if not table:
        return commodities
    
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        
        sno_text = cells[0].get_text(strip=True)
        if not sno_text.isdigit():
            continue
        
        # Skip total rows
        row_text = row.get_text().lower()
        if "total" in row_text:
            continue
        
        hscode = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        description = cells[2].get_text(strip=True) if len(cells) > 2 else ""
        
        commodity = {
            "sno": int(sno_text),
            "hscode": hscode,
            "description": description,
            "month_prev_year": _parse_number(cells[3].get_text(strip=True)) if len(cells) > 3 else None,
            "month_curr_year": _parse_number(cells[4].get_text(strip=True)) if len(cells) > 4 else None,
            "month_yoy_growth_pct": _parse_number(cells[5].get_text(strip=True)) if len(cells) > 5 else None,
            "cumulative_prev_year": _parse_number(cells[6].get_text(strip=True)) if len(cells) > 6 else None,
            "cumulative_curr_year": _parse_number(cells[7].get_text(strip=True)) if len(cells) > 7 else None,
            "cumulative_yoy_growth_pct": _parse_number(cells[8].get_text(strip=True)) if len(cells) > 8 else None,
        }
        commodities.append(commodity)
    
    return commodities


def _extract_total(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """Extract the total row from the table."""
    table = soup.find("table")
    if not table:
        return None
    
    for row in table.find_all("tr"):
        row_text = row.get_text()
        if "Total" in row_text or "India's Total" in row_text:
            cells = row.find_all("td")
            if len(cells) >= 5:
                # Find the label cell
                label = ""
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if "Total" in text:
                        label = text
                        break
                
                if len(cells) >= 8:
                    return {
                        "label": label,
                        "month_prev_year": _parse_number(cells[3].get_text(strip=True)) if len(cells) > 3 else None,
                        "month_curr_year": _parse_number(cells[4].get_text(strip=True)) if len(cells) > 4 else None,
                        "month_yoy_growth_pct": _parse_number(cells[5].get_text(strip=True)) if len(cells) > 5 else None,
                        "cumulative_prev_year": _parse_number(cells[6].get_text(strip=True)) if len(cells) > 6 else None,
                        "cumulative_curr_year": _parse_number(cells[7].get_text(strip=True)) if len(cells) > 7 else None,
                        "cumulative_yoy_growth_pct": _parse_number(cells[8].get_text(strip=True)) if len(cells) > 8 else None,
                    }
    return None


def _extract_report_date(soup: BeautifulSoup) -> Optional[str]:
    """Extract the report date from the page."""
    text = soup.get_text()
    match = re.search(r"Report Dated?:?\s*(\d{2}\s+\w+\s+\d{4})", text)
    if match:
        return match.group(1)
    return None


def _parse_number(text: str) -> Optional[float]:
    """Parse a numeric string, handling empty values and formatting."""
    if not text or text.strip() in ["-", "NA", ""]:
        return None
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return None
