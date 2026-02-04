"""
Parser for commodity-wise trade data.
Extracts structured data from HTML responses.
"""

import re
import json
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger


def parse_commodity_html(html: str, hsn: str, year: str) -> Optional[Dict[str, Any]]:
    """
    Parse commodity trade data from HTML response with comprehensive metadata.
    
    Args:
        html: HTML response content
        hsn: HSN code
        year: Financial year
        
    Returns:
        Parsed data dictionary with professional metadata or None if parsing fails
    """
    from datetime import datetime
    
    try:
        soup = BeautifulSoup(html, "lxml")
        
        # Track extraction statistics
        extract_start = datetime.now()
        
        # Extract metadata
        metadata = _extract_metadata(soup, hsn, year)
        if not metadata:
            return None
        
        # Extract commodity info
        commodity = _extract_commodity_info(soup, hsn)
        
        # Extract countries data
        countries = _extract_countries_data(soup)
        
        # Extract totals
        totals = _extract_totals(soup)
        
        # Extract report date
        report_date = _extract_report_date(soup)
        
        # Calculate data quality metrics
        total_countries = len(countries)
        countries_with_data = sum(1 for c in countries if c.get('values_usd', {}).get('y2024_2025') is not None)
        data_completeness = (countries_with_data / total_countries * 100) if total_countries > 0 else 0
        
        extract_duration = (datetime.now() - extract_start).total_seconds()
        
        return {
            "metadata": metadata,
            "commodity": commodity,
            "report_date": report_date,
            "countries": countries,
            "totals": totals,
            "data_quality": {
                "extraction_completeness_percent": round(data_completeness, 2),
                "total_countries_count": total_countries,
                "countries_with_complete_data": countries_with_data,
                "countries_with_missing_data": total_countries - countries_with_data,
                "extraction_duration_seconds": round(extract_duration, 3),
                "validation_status": "VALID" if data_completeness >= 70 else "PARTIAL" if data_completeness >= 50 else "INCOMPLETE"
            },
            "schema": {
                "version": "2.0",
                "parser_version": "1.1",
                "last_updated": "2026-01-29",
                "fields": {
                    "countries": ["sno", "country", "values_usd", "values_quantity"],
                    "values": ["y2023_2024", "y2024_2025", "pct_growth"],
                    "totals": ["total", "india_total", "pct_share"]
                }
            },
            "processing": {
                "status": "SUCCESS",
                "errors": [],
                "warnings": [],
                "processing_timestamp": datetime.now().isoformat(),
                "data_source": "tradestat.commerce.gov.in",
                "extraction_method": "BeautifulSoup_HTML_Parser",
                "environment": "production"
            }
        }
    
    except Exception as e:
        logger.error(f"Error parsing HTML for HSN={hsn}, YEAR={year}: {e}")
        return None


def _extract_metadata(soup: BeautifulSoup, hsn: str, year: str) -> Dict[str, Any]:
    """Extract metadata from HTML."""
    from datetime import datetime
    
    return {
        "scraped_at": datetime.now().isoformat(),
        "source_url": "https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_export",
        "hsn_code": hsn,
        "financial_year": year,
        "schema_version": "1.0",
        "data_availability": "2017-2018 to 2025-2026 (Apr-Aug)",
        "last_updated": "2025-10-21 13:40:42",
    }


def _extract_commodity_info(soup: BeautifulSoup, hsn: str) -> Dict[str, Any]:
    """Extract commodity information from HTML."""
    description = ""
    unit = ""
    
    try:
        # Look for commodity info - usually in a paragraph or specific element
        text_content = soup.get_text()
        
        # Pattern: HSN_CODE DESCRIPTION Unit:UNIT
        pattern = rf"Commodity:\s*{hsn}\s+(.*?)\s+Unit:\s*(\w+)"
        match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
        
        if match:
            description = match.group(1).strip().split('\n')[0]  # Get first line
            unit = match.group(2).strip()
        
        # Alternative: look for in all text
        if not description:
            for line in text_content.split('\n'):
                if hsn in line and 'Unit' in line:
                    parts = line.split('Unit:')
                    if len(parts) > 1:
                        description = parts[0].replace(hsn, '').strip()
                        unit = parts[1].strip().split()[0]
                    break
    
    except Exception as e:
        logger.warning(f"Error extracting commodity info: {e}")
    
    return {
        "hsn_code": hsn,
        "description": description or "N/A",
        "unit": unit or "N/A",
    }


def _extract_report_date(soup: BeautifulSoup) -> Optional[str]:
    """Extract report date from HTML."""
    try:
        text = soup.get_text()
        # Look for date pattern like "27 Jan 2026" or "27-Jan-2026"
        pattern = r"(\d{1,2}\s+\w+\s+\d{4})|(\d{1,2}-\w+-\d{4})"
        match = re.search(pattern, text)
        return match.group(0) if match else None
    except Exception as e:
        logger.warning(f"Error extracting report date: {e}")
        return None


def _extract_countries_data(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract countries data from HTML table."""
    countries = []
    
    try:
        # Find the main data table with id="example1"
        table = soup.find("table", {"id": "example1"})
        
        if not table:
            logger.warning("Could not find data table with id='example1'")
            return countries
        
        # Get all body rows (skip header rows)
        tbody = table.find("tbody")
        if not tbody:
            logger.warning("Could not find tbody in table")
            return tbody
        
        rows = tbody.find_all("tr")
        
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 8:  # Need at least 8 columns
                continue
            
            # Column structure:
            # 0: S.No
            # 1: Country name
            # 2-4: USD values (2023-24, 2024-25, %Growth)
            # 5-7: Quantity values (2023-24, 2024-25, %Growth)
            
            try:
                sno_text = cols[0].get_text(strip=True)
                country_name = cols[1].get_text(strip=True)
                
                # Stop if we hit total row
                if country_name.upper() in ["TOTAL", "INDIA'S TOTAL", "% SHARE", ""]:
                    break
                
                # Extract USD values
                usd_2023_24 = _parse_numeric(cols[2].get_text(strip=True))
                usd_2024_25 = _parse_numeric(cols[3].get_text(strip=True))
                usd_growth = _parse_numeric(cols[4].get_text(strip=True))
                
                # Extract Quantity values
                qty_2023_24 = _parse_numeric(cols[5].get_text(strip=True))
                qty_2024_25 = _parse_numeric(cols[6].get_text(strip=True))
                qty_growth = _parse_numeric(cols[7].get_text(strip=True))
                
                try:
                    sno = int(sno_text)
                except (ValueError, TypeError):
                    sno = len(countries) + 1
                
                country_data = {
                    "sno": sno,
                    "country": country_name,
                    "values_usd": {
                        "y2023_2024": usd_2023_24,
                        "y2024_2025": usd_2024_25,
                        "pct_growth": usd_growth,
                    },
                    "values_quantity": {
                        "y2023_2024": qty_2023_24,
                        "y2024_2025": qty_2024_25,
                        "pct_growth": qty_growth,
                    }
                }
                
                countries.append(country_data)
            
            except (IndexError, AttributeError) as e:
                logger.debug(f"Error processing row: {e}")
                continue
    
    except Exception as e:
        logger.warning(f"Error extracting countries data: {e}")
    
    return countries


def _parse_numeric(text: str) -> Optional[float]:
    """Parse numeric value from text, handling empty/dash cases."""
    if not text or text.strip() in ['-', 'N/A', '']:
        return None
    try:
        # Remove commas and whitespace
        cleaned = text.strip().replace(',', '').replace(' ', '')
        return float(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None


def _extract_totals(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract totals data from HTML footer."""
    totals = {
        "total": {
            "values_usd": {
                "y2023_2024": None,
                "y2024_2025": None,
                "pct_growth": None,
            }
        },
        "india_total": {
            "values_usd": {
                "y2023_2024": None,
                "y2024_2025": None,
                "pct_growth": None,
            }
        },
        "pct_share": {
            "y2023_2024": None,
            "y2024_2025": None,
        }
    }
    
    try:
        table = soup.find("table", {"id": "example1"})
        if not table:
            return totals
        
        tfoot = table.find("tfoot")
        if not tfoot:
            return totals
        
        # Process each row in footer
        rows = tfoot.find_all("tr")
        
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            
            row_label = cols[0].get_text(strip=True).upper() + " " + cols[1].get_text(strip=True).upper()
            
            # Extract Total row
            if "TOTAL" in row_label and "INDIA" not in row_label:
                if len(cols) >= 5:
                    totals["total"]["values_usd"]["y2023_2024"] = _parse_numeric(cols[2].get_text(strip=True))
                    totals["total"]["values_usd"]["y2024_2025"] = _parse_numeric(cols[3].get_text(strip=True))
                    totals["total"]["values_usd"]["pct_growth"] = _parse_numeric(cols[4].get_text(strip=True))
            
            # Extract India's Total row
            elif "INDIA" in row_label and "TOTAL" in row_label:
                if len(cols) >= 5:
                    totals["india_total"]["values_usd"]["y2023_2024"] = _parse_numeric(cols[2].get_text(strip=True))
                    totals["india_total"]["values_usd"]["y2024_2025"] = _parse_numeric(cols[3].get_text(strip=True))
                    totals["india_total"]["values_usd"]["pct_growth"] = _parse_numeric(cols[4].get_text(strip=True))
            
            # Extract % Share row
            elif "SHARE" in row_label:
                if len(cols) >= 4:
                    totals["pct_share"]["y2023_2024"] = _parse_numeric(cols[2].get_text(strip=True))
                    totals["pct_share"]["y2024_2025"] = _parse_numeric(cols[3].get_text(strip=True))
    
    except Exception as e:
        logger.warning(f"Error extracting totals: {e}")
    
    return totals

