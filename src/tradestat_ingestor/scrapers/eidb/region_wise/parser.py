"""
Parser for Region-wise TradeStat HTML responses.
Extracts trade data from HTML tables.
"""

from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from typing import Optional

# IST is UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))


def parse_region_wise_response(
    html: str,
    trade_type: str,
    year: str,
    region_code: str,
    region_name: str,
    value_type: str
) -> dict:
    """
    Parse the HTML response and extract region-wise trade data.
    
    Args:
        html: Raw HTML response
        trade_type: "export" or "import"
        year: Year code
        region_code: Region code used in request
        region_name: Region name
        value_type: "usd" or "inr"
        
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
    
    if table:
        # Get all rows - may or may not have tbody
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                record = parse_row(cells, value_type)
                if record:
                    # Check if this is a total row
                    region = record.get("region", "").lower()
                    if "total" in region or "india's total" in region:
                        total_record = record
                    else:
                        records.append(record)
    
    # Build metadata
    value_unit = "US $ Million" if value_type == "usd" else "₹ Crore"
    fiscal_year = f"{year}-{int(year)+1}"
    
    result = {
        "metadata": {
            "source": {
                "name": "TradeStat - Department of Commerce, India",
                "url": f"https://tradestat.commerce.gov.in/eidb/region_wise_{trade_type}",
                "database": "EIDB (Export Import Data Bank)"
            },
            "extraction": {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "timestamp_ist": datetime.now(IST).isoformat(),
                "tool": "region_wise_scraper",
                "version": "1.0.0"
            },
            "query_parameters": {
                "trade_type": trade_type,
                "year": year,
                "fiscal_year": fiscal_year,
                "region_code": region_code,
                "region_name": region_name,
                "value_type": value_type,
                "value_unit": value_unit
            },
            "data_info": {
                "record_count": len(records),
                "value_unit": value_unit,
                "notes": [
                    "India's Imports/Exports include re-imports/re-exports",
                    "Trade figures in US$ are addition of monthly US$ figures",
                    "Fiscal year runs from April to March"
                ]
            }
        },
        "data": {
            "regions": records,
            "total": total_record
        }
    }
    
    return result


def parse_row(cells: list, value_type: str) -> Optional[dict]:
    """
    Parse a single table row.
    
    Args:
        cells: List of td elements
        value_type: "usd" or "inr"
        
    Returns:
        Dictionary with row data or None if invalid
    """
    try:
        if len(cells) < 2:
            return None
        
        # Skip header-like rows or empty rows
        first_cell_text = cells[0].get_text(strip=True)
        if not first_cell_text or first_cell_text.lower() in ['s.no', 'sno', 'sl.no', '#', 'report dated']:
            return None
        
        # Skip rows that are just headers
        if 'region' in first_cell_text.lower() and '%share' in cells[-1].get_text(strip=True).lower():
            return None
        
        record = {}
        
        # Region name (first column)
        record["region"] = first_cell_text.strip()
        
        # The table structure varies - it may have:
        # Region | PrevYear | %Share | CurrYear | %Share | %Growth
        # or just: Region | Value | %Share | %Growth
        
        if len(cells) >= 6:
            # Full structure with two years
            record["prev_year_value"] = parse_numeric(cells[1].get_text(strip=True))
            record["prev_year_share"] = parse_numeric(cells[2].get_text(strip=True))
            record["curr_year_value"] = parse_numeric(cells[3].get_text(strip=True))
            record["curr_year_share"] = parse_numeric(cells[4].get_text(strip=True))
            record["percentage_growth"] = parse_numeric(cells[5].get_text(strip=True))
        elif len(cells) >= 4:
            # Simpler structure
            record["value"] = parse_numeric(cells[1].get_text(strip=True))
            record["percentage_share"] = parse_numeric(cells[2].get_text(strip=True))
            record["percentage_growth"] = parse_numeric(cells[3].get_text(strip=True))
        elif len(cells) >= 2:
            record["value"] = parse_numeric(cells[1].get_text(strip=True))
        
        record["value_unit"] = "US $ Million" if value_type == "usd" else "₹ Crore"
        
        return record
        
    except Exception as e:
        print(f"Error parsing row: {e}")
        return None


def parse_numeric(value: str) -> Optional[float]:
    """
    Parse a numeric value from string.
    """
    if not value:
        return None
    
    cleaned = value.replace(',', '').replace('%', '').replace('$', '').replace('₹', '').strip()
    
    if cleaned in ['-', 'NA', 'N/A', '', 'null', 'Null', 'No Result Found']:
        return None
    
    try:
        return float(cleaned)
    except ValueError:
        return None
