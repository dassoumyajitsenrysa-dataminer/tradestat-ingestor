"""
Parser for Commodity x Country-wise TradeStat HTML responses.
Extracts time series trade data from HTML tables.
"""

from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from typing import Optional, List
import re

# IST is UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))


def parse_commodity_country_response(
    html: str,
    trade_type: str,
    hs_code: str,
    year: str,
    country_code: str,
    country_name: str,
    value_type: str
) -> dict:
    """
    Parse the HTML response and extract commodity x country trade data.
    
    The table shows time series data:
    - Row 1: Values by year
    - Row 2: %Growth
    - Row 3: Total export/import of commodity
    - Row 4: %Growth
    - Row 5: %Share of country
    - Row 6: Total export/import to country
    - Row 7: %Growth
    - Row 8: %Share of commodity
    
    Args:
        html: Raw HTML response
        trade_type: "export" or "import"
        hs_code: HS code used in request
        year: Year code (determines 5-year range)
        country_code: Country code
        country_name: Country name
        value_type: "usd" or "inr"
        
    Returns:
        Dictionary with metadata and parsed data
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Find the data table
    table = soup.find('table', {'class': 'table'})
    
    # Extract header info from first row
    commodity_description = ""
    unit = ""
    
    if table:
        first_row = table.find('tr')
        if first_row:
            first_td = first_row.find('td')
            if first_td:
                text = first_td.get_text()
                # Extract description
                desc_match = re.search(r'Description:\s*([^|]+)', text)
                if desc_match:
                    commodity_description = desc_match.group(1).strip()
                # Extract unit
                unit_match = re.search(r'Unit:\s*([^|]+)', text)
                if unit_match:
                    unit = unit_match.group(1).strip()
    
    # Extract years from header row
    years = []
    time_series = {}
    
    if table:
        rows = table.find_all('tr')
        
        # Find header row with years
        for row in rows:
            ths = row.find_all('th')
            if len(ths) >= 3:
                for th in ths:
                    year_text = th.get_text(strip=True)
                    # Match year pattern like "2019 - 2020"
                    if re.match(r'\d{4}\s*-\s*\d{4}', year_text):
                        years.append(year_text.replace(' ', ''))
                break
        
        # Parse data rows
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                # Get row label (second cell)
                label_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                
                # Skip header info row
                if "Country:" in label_text or "HSCODE:" in label_text:
                    continue
                
                # Map label to key
                key = None
                if "Values in" in label_text:
                    key = "values"
                elif "%Growth" in label_text:
                    # Determine which growth row based on previous key
                    if "values" in time_series and "values_growth" not in time_series:
                        key = "values_growth"
                    elif "total_commodity" in time_series and "total_commodity_growth" not in time_series:
                        key = "total_commodity_growth"
                    elif "total_country" in time_series and "total_country_growth" not in time_series:
                        key = "total_country_growth"
                elif "Total export of commodity" in label_text or "Total import of commodity" in label_text:
                    key = "total_commodity"
                elif "Total export to country" in label_text or "Total import from country" in label_text:
                    key = "total_country"
                elif "%Share of country" in label_text:
                    key = "country_share"
                elif "%Share of commodity" in label_text:
                    key = "commodity_share"
                
                if key:
                    values = []
                    # Extract values from year columns (skip first two cells: S.No and Label)
                    for i in range(2, len(cells)):
                        val = parse_numeric(cells[i].get_text(strip=True))
                        values.append(val)
                    
                    time_series[key] = values
    
    # Build yearly data structure
    yearly_data = []
    for i, yr in enumerate(years):
        year_record = {"year": yr}
        
        for key, values in time_series.items():
            if i < len(values):
                year_record[key] = values[i]
        
        yearly_data.append(year_record)
    
    # Build metadata
    value_unit = "US $ Million" if value_type == "usd" else "₹ Crore"
    fiscal_year = f"{year}-{int(year)+1}"
    hs_level = str(len(hs_code)) if hs_code else "0"
    
    result = {
        "metadata": {
            "source": {
                "name": "TradeStat - Department of Commerce, India",
                "url": f"https://tradestat.commerce.gov.in/eidb/commodityx_countries_wise_{trade_type}",
                "database": "EIDB (Export Import Data Bank)"
            },
            "extraction": {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "timestamp_ist": datetime.now(IST).isoformat(),
                "tool": "commodity_x_country_scraper",
                "version": "1.0.0"
            },
            "query_parameters": {
                "trade_type": trade_type,
                "hs_code": hs_code,
                "hs_level": hs_level,
                "selected_year": year,
                "fiscal_year": fiscal_year,
                "country_code": country_code,
                "country_name": country_name,
                "value_type": value_type,
                "value_unit": value_unit
            },
            "data_info": {
                "commodity_description": commodity_description,
                "unit": unit,
                "years_covered": years,
                "record_count": len(yearly_data),
                "value_unit": value_unit,
                "notes": [
                    "India's Imports/Exports include re-imports/re-exports",
                    "Trade figures in US$ are addition of monthly US$ figures",
                    "Fiscal year runs from April to March",
                    "* ITC HS Code of the Commodity is either dropped or re-allocated"
                ]
            }
        },
        "data": {
            "commodity": {
                "hs_code": hs_code,
                "description": commodity_description,
                "unit": unit
            },
            "country": {
                "code": country_code,
                "name": country_name
            },
            "time_series": yearly_data,
            "summary": {
                "values": time_series.get("values", []),
                "values_growth": time_series.get("values_growth", []),
                "total_commodity": time_series.get("total_commodity", []),
                "total_commodity_growth": time_series.get("total_commodity_growth", []),
                "country_share": time_series.get("country_share", []),
                "total_country": time_series.get("total_country", []),
                "total_country_growth": time_series.get("total_country_growth", []),
                "commodity_share": time_series.get("commodity_share", [])
            }
        }
    }
    
    return result


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
    
    try:
        return float(cleaned)
    except ValueError:
        return None
