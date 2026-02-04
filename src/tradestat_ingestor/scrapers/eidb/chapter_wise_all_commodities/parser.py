"""
Parser for Chapter-wise TradeStat HTML responses.
Extracts trade data from HTML tables.
"""

from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from typing import Optional

# IST is UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))


def parse_chapter_wise_response(
    html: str,
    trade_type: str,
    year: str,
    hs_code: str,
    hs_level: str,
    value_type: str
) -> dict:
    """
    Parse the HTML response and extract chapter-wise trade data.
    
    Args:
        html: Raw HTML response
        trade_type: "export" or "import"
        year: Year code
        hs_code: HS code used in request
        hs_level: HS level (2, 4, 6, 8)
        value_type: "usd", "inr", or "qty"
        
    Returns:
        Dictionary with metadata and parsed data
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Find the data table
    table = soup.find('table', {'class': 'table'})
    
    if not table:
        tables = soup.find_all('table')
        for t in tables:
            if t.find('tr'):
                table = t
                break
    
    records = []
    total_record = None
    target_record = None
    
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                record = parse_row(cells, value_type, hs_level)
                if record:
                    # Check if this is a total row
                    desc = record.get("commodity", "").lower()
                    if "total" in desc or "india's total" in desc:
                        total_record = record
                    else:
                        records.append(record)
                        # Check if this is the exact HS code we want
                        record_hs = str(record.get("hs_code", "")).strip()
                        if hs_code != "all" and record_hs == hs_code:
                            target_record = record
    
    # If user requested a specific HS code, return only that record
    exact_match_found = True
    if hs_code != "all":
        if target_record:
            records = [target_record]
        else:
            # No exact match found - return empty and set flag
            exact_match_found = False
            records = []
    
    # Build metadata
    value_unit = get_value_unit(value_type)
    fiscal_year = f"{year}-{int(year)+1}"
    
    result = {
        "metadata": {
            "source": {
                "name": "TradeStat - Department of Commerce, India",
                "url": f"https://tradestat.commerce.gov.in/eidb/chapter_wise_all_commodities_{trade_type}",
                "database": "EIDB (Export Import Data Bank)"
            },
            "extraction": {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "timestamp_ist": datetime.now(IST).isoformat(),
                "tool": "chapter_wise_all_commodities_scraper",
                "version": "1.0.0"
            },
            "query_parameters": {
                "trade_type": trade_type,
                "year": year,
                "fiscal_year": fiscal_year,
                "hs_code": hs_code,
                "hs_level": hs_level,
                "value_type": value_type,
                "value_unit": value_unit
            },
            "data_info": {
                "record_count": len(records),
                "exact_match_found": exact_match_found,
                "value_unit": value_unit,
                "notes": [
                    "India's Imports/Exports include re-imports/re-exports",
                    "Trade figures in US$ are addition of monthly US$ figures",
                    "Fiscal year runs from April to March",
                    "* ITC HS Code of the Commodity is either dropped or re-allocated"
                ],
                "warning": None if exact_match_found else f"HS code '{hs_code}' not found in database"
            }
        },
        "data": {
            "commodities": records,
            "total": total_record
        }
    }
    
    return result


def get_value_unit(value_type: str) -> str:
    """Get the value unit description."""
    if value_type == "usd":
        return "US $ Million"
    elif value_type == "inr":
        return "₹ Crore"
    else:
        return "Quantity (in thousands)"


def parse_row(cells: list, value_type: str, hs_level: str) -> Optional[dict]:
    """
    Parse a single table row.
    
    Expected columns: S.No | HSCode | Commodity | PrevYear | %Share | CurrYear | %Share | %Growth | [HS digit options]
    
    Args:
        cells: List of td elements
        value_type: "usd", "inr", or "qty"
        hs_level: HS level for context
        
    Returns:
        Dictionary with row data or None if invalid
    """
    try:
        if len(cells) < 3:
            return None
        
        # Get first cell text
        first_cell_text = cells[0].get_text(strip=True)
        
        # Skip header-like rows
        if not first_cell_text:
            return None
        if first_cell_text.lower() in ['s.no', 'sno', 'sl.no', '#', 'report dated']:
            return None
        
        # Skip if first cell contains "hscode" (header row)
        if 'hscode' in first_cell_text.lower():
            return None
        
        record = {}
        
        # Table structure: S.No | HSCode | Commodity | PrevYear | %Share | CurrYear | %Share | %Growth
        if len(cells) >= 8:
            record["serial_no"] = parse_numeric(first_cell_text)
            record["hs_code"] = cells[1].get_text(strip=True)
            record["commodity"] = cells[2].get_text(strip=True)
            record["prev_year_value"] = parse_numeric(cells[3].get_text(strip=True))
            record["prev_year_share"] = parse_numeric(cells[4].get_text(strip=True))
            record["curr_year_value"] = parse_numeric(cells[5].get_text(strip=True))
            record["curr_year_share"] = parse_numeric(cells[6].get_text(strip=True))
            record["percentage_growth"] = parse_numeric(cells[7].get_text(strip=True))
        elif len(cells) >= 6:
            # Simpler structure without S.No
            record["hs_code"] = cells[0].get_text(strip=True)
            record["commodity"] = cells[1].get_text(strip=True)
            record["prev_year_value"] = parse_numeric(cells[2].get_text(strip=True))
            record["prev_year_share"] = parse_numeric(cells[3].get_text(strip=True))
            record["curr_year_value"] = parse_numeric(cells[4].get_text(strip=True))
            record["curr_year_share"] = parse_numeric(cells[5].get_text(strip=True))
        elif len(cells) >= 3:
            # Total row or minimal structure
            # Check if it's a total row (spans multiple columns)
            combined_text = " ".join(c.get_text(strip=True) for c in cells[:3])
            if "total" in combined_text.lower():
                record["commodity"] = combined_text.strip()
                # Find numeric values
                for cell in cells:
                    val = parse_numeric(cell.get_text(strip=True))
                    if val is not None and val > 1000:  # Likely a total value
                        if "prev_year_value" not in record:
                            record["prev_year_value"] = val
                        elif "curr_year_value" not in record:
                            record["curr_year_value"] = val
            else:
                return None
        
        record["value_unit"] = get_value_unit(value_type)
        record["hs_level"] = hs_level
        
        return record
        
    except Exception as e:
        print(f"Error parsing row: {e}")
        return None


def parse_numeric(value: str) -> Optional[float]:
    """Parse a numeric value from string."""
    if not value:
        return None
    
    cleaned = value.replace(',', '').replace('%', '').replace('$', '').replace('₹', '').strip()
    
    # Remove non-breaking spaces
    cleaned = cleaned.replace('\xa0', ' ').strip()
    
    # Handle special cases
    if cleaned in ['-', 'NA', 'N/A', '', 'null', 'Null', 'No Result Found']:
        return None
    
    # Remove any leading numbers with spaces (like "1  " from "1  Asia")
    parts = cleaned.split()
    if len(parts) > 1 and parts[0].isdigit():
        # This might be a serial number prefix, skip it
        pass
    
    try:
        return float(cleaned)
    except ValueError:
        return None
