"""
Parser for Country-wise TradeStat HTML responses.
Extracts trade data from HTML tables.
"""

from datetime import datetime, timezone
from bs4 import BeautifulSoup
from typing import Optional


def parse_country_wise_response(
    html: str,
    trade_type: str,
    year: str,
    country_code: str,
    country_name: str,
    value_type: str
) -> dict:
    """
    Parse the HTML response and extract trade data.
    """
    soup = BeautifulSoup(html, 'lxml')
    
    table = soup.find('table', {'class': 'table'})
    
    if not table:
        tables = soup.find_all('table')
        for t in tables:
            if t.find('tbody'):
                table = t
                break
    
    records = []
    
    if table:
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    record = parse_row(cells, value_type)
                    if record:
                        records.append(record)
    
    value_unit = "US $ Million" if value_type == "usd" else "₹ Crore"
    fiscal_year = f"{year}-{int(year)+1}"
    
    result = {
        "metadata": {
            "source": {
                "name": "TradeStat - Department of Commerce, India",
                "url": f"https://tradestat.commerce.gov.in/eidb/country_wise_{trade_type}",
                "database": "EIDB (Export Import Data Bank)"
            },
            "extraction": {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "tool": "country_wise_scraper",
                "version": "1.0.0"
            },
            "query_parameters": {
                "trade_type": trade_type,
                "year": year,
                "fiscal_year": fiscal_year,
                "country_code": country_code,
                "country_name": country_name,
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
        "data": records
    }
    
    return result


def parse_row(cells: list, value_type: str) -> Optional[dict]:
    """Parse a single table row."""
    try:
        if len(cells) < 3:
            return None
        
        first_cell_text = cells[0].get_text(strip=True)
        if not first_cell_text or first_cell_text.lower() in ['s.no', 'sno', 'sl.no', '#']:
            return None
        
        record = {}
        
        sno_text = cells[0].get_text(strip=True)
        if sno_text.isdigit():
            record["serial_no"] = int(sno_text)
        else:
            record["serial_no"] = None
        
        if len(cells) > 1:
            record["country"] = cells[1].get_text(strip=True)
        
        if len(cells) > 2:
            value_text = cells[2].get_text(strip=True)
            record["value"] = parse_numeric(value_text)
            record["value_unit"] = "US $ Million" if value_type == "usd" else "₹ Crore"
        
        if len(cells) > 3:
            share_text = cells[3].get_text(strip=True)
            record["percentage_share"] = parse_numeric(share_text)
        
        if len(cells) > 4:
            growth_text = cells[4].get_text(strip=True)
            record["percentage_growth"] = parse_numeric(growth_text)
        
        return record
        
    except Exception as e:
        print(f"Error parsing row: {e}")
        return None


def parse_numeric(value: str) -> Optional[float]:
    """Parse a numeric value from string."""
    if not value:
        return None
    
    cleaned = value.replace(',', '').replace('%', '').replace('$', '').replace('₹', '').strip()
    
    if cleaned in ['-', 'NA', 'N/A', '', 'null', 'Null']:
        return None
    
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_all_countries_table(html: str, trade_type: str, year: str, value_type: str) -> dict:
    """Parse HTML when fetching data for all countries at once."""
    soup = BeautifulSoup(html, 'lxml')
    
    table = soup.find('table', {'class': 'table'})
    
    if not table:
        tables = soup.find_all('table')
        for t in tables:
            if t.find('tbody'):
                table = t
                break
    
    records = []
    total_record = None
    
    if table:
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    record = parse_row(cells, value_type)
                    if record:
                        country = record.get("country", "").lower()
                        if "total" in country or "grand total" in country:
                            total_record = record
                        else:
                            records.append(record)
    
    value_unit = "US $ Million" if value_type == "usd" else "₹ Crore"
    fiscal_year = f"{year}-{int(year)+1}"
    
    result = {
        "metadata": {
            "source": {
                "name": "TradeStat - Department of Commerce, India",
                "url": f"https://tradestat.commerce.gov.in/eidb/country_wise_{trade_type}",
                "database": "EIDB (Export Import Data Bank)"
            },
            "extraction": {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "tool": "country_wise_scraper",
                "version": "1.0.0"
            },
            "query_parameters": {
                "trade_type": trade_type,
                "year": year,
                "fiscal_year": fiscal_year,
                "country_filter": "all",
                "value_type": value_type,
                "value_unit": value_unit
            },
            "data_info": {
                "country_count": len(records),
                "value_unit": value_unit,
                "notes": [
                    "India's Imports/Exports include re-imports/re-exports",
                    "Trade figures in US$ are addition of monthly US$ figures",
                    "Fiscal year runs from April to March"
                ]
            }
        },
        "data": {
            "countries": records,
            "total": total_record
        }
    }
    
    return result
