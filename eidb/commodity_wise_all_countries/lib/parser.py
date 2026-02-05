"""
Parser for commodity-wise all countries trade data.
Extracts structured data from HTML responses.
"""

import re
import hashlib
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime


def parse_commodity_html(html: str, hsn: str, year: str) -> Optional[Dict[str, Any]]:
    """
    Parse commodity trade data from HTML response.
    
    Args:
        html: HTML response content
        hsn: HSN code
        year: Financial year
        
    Returns:
        Parsed data dictionary with metadata or None if parsing fails
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        extract_start = datetime.now()
        
        # Extract all components
        metadata = _extract_metadata(soup, hsn, year)
        commodity = _extract_commodity_info(soup, hsn)
        countries = _extract_countries_data(soup)
        totals = _extract_totals(soup)
        report_date = _extract_report_date(soup)
        
        # Calculate data quality metrics
        total_countries = len(countries)
        countries_with_data = sum(1 for c in countries if c.get('values_usd', {}).get('y2024_2025') is not None)
        data_completeness = (countries_with_data / total_countries * 100) if total_countries > 0 else 0
        extract_duration = (datetime.now() - extract_start).total_seconds()
        
        # Checksum
        parsed_data = {"countries": countries, "totals": totals}
        checksum = hashlib.md5(str(parsed_data).encode()).hexdigest()
        
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
                "validation_status": "VALID" if data_completeness >= 70 else "PARTIAL" if data_completeness >= 50 else "INCOMPLETE",
                "checksum_md5": checksum,
            },
            "schema": {
                "version": "2.0",
                "parser_version": "1.1",
                "last_updated": "2026-02-03",
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
            }
        }
    
    except Exception as e:
        print(f"[!] Error parsing HTML for HSN={hsn}, YEAR={year}: {e}")
        return None


def _extract_metadata(soup: BeautifulSoup, hsn: str, year: str) -> Dict[str, Any]:
    """Extract metadata from HTML."""
    return {
        "scraped_at": datetime.now().isoformat(),
        "source_url": "https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_export",
        "hsn_code": hsn,
        "financial_year": year,
        "fiscal_year_range": f"{year}-{int(year)+1}",
        "data_source": "DGCI&S (Directorate General of Commercial Intelligence and Statistics)",
        "data_provider": "Ministry of Commerce and Industry, Government of India",
    }


def _extract_commodity_info(soup: BeautifulSoup, hsn: str) -> Dict[str, Any]:
    """Extract commodity information from HTML."""
    description = ""
    unit = ""
    
    try:
        text_content = soup.get_text()
        
        # Pattern: Commodity: HSN_CODE DESCRIPTION Unit: UNIT
        pattern = rf"Commodity:\s*{hsn}\s+(.*?)\s+Unit:\s*(\w+)"
        match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
        
        if match:
            description = match.group(1).strip().split('\n')[0]
            unit = match.group(2).strip()
        
        # Alternative pattern
        if not description:
            for line in text_content.split('\n'):
                if hsn in line and 'Unit' in line:
                    parts = line.split('Unit:')
                    if len(parts) > 1:
                        description = parts[0].replace(hsn, '').replace('Commodity:', '').strip()
                        unit = parts[1].strip().split()[0]
                    break
    except Exception:
        pass
    
    return {
        "hsn_code": hsn,
        "description": description or "N/A",
        "unit": unit or "N/A",
    }


def _extract_report_date(soup: BeautifulSoup) -> Optional[str]:
    """Extract report date from HTML."""
    try:
        text = soup.get_text()
        pattern = r"Report Dated:\s*(\d{1,2}\s+\w+\s+\d{4})"
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        # Alternative date pattern
        pattern = r"(\d{1,2}\s+\w+\s+\d{4})|(\d{1,2}-\w+-\d{4})"
        match = re.search(pattern, text)
        return match.group(0) if match else None
    except Exception:
        return None


def _extract_countries_data(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract countries data from HTML table."""
    countries = []
    
    try:
        # Find the main data table
        table = soup.find("table", {"id": "example1"})
        if not table:
            # Try alternative table selection
            table = soup.find("table", class_="table")
        
        if not table:
            print("[!] Could not find data table")
            return countries
        
        tbody = table.find("tbody")
        if not tbody:
            return countries
        
        rows = tbody.find_all("tr")
        
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 8:
                continue
            
            try:
                sno_text = cols[0].get_text(strip=True)
                country_name = cols[1].get_text(strip=True)
                
                # Stop at total rows
                if country_name.upper() in ["TOTAL", "INDIA'S TOTAL", "% SHARE", ""]:
                    break
                
                # Extract values
                usd_2023_24 = _parse_numeric(cols[2].get_text(strip=True))
                usd_2024_25 = _parse_numeric(cols[3].get_text(strip=True))
                usd_growth = _parse_numeric(cols[4].get_text(strip=True))
                qty_2023_24 = _parse_numeric(cols[5].get_text(strip=True))
                qty_2024_25 = _parse_numeric(cols[6].get_text(strip=True))
                qty_growth = _parse_numeric(cols[7].get_text(strip=True))
                
                try:
                    sno = int(sno_text)
                except (ValueError, TypeError):
                    sno = len(countries) + 1
                
                countries.append({
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
                })
            except (IndexError, AttributeError):
                continue
    except Exception as e:
        print(f"[!] Error extracting countries data: {e}")
    
    return countries


def _extract_totals(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract totals data from HTML footer."""
    totals = {
        "total": {"values_usd": {"y2023_2024": None, "y2024_2025": None, "pct_growth": None}},
        "india_total": {"values_usd": {"y2023_2024": None, "y2024_2025": None, "pct_growth": None}},
        "pct_share": {"y2023_2024": None, "y2024_2025": None}
    }
    
    try:
        table = soup.find("table", {"id": "example1"})
        if not table:
            return totals
        
        tfoot = table.find("tfoot")
        if not tfoot:
            return totals
        
        for row in tfoot.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            
            row_label = (cols[0].get_text(strip=True) + " " + cols[1].get_text(strip=True)).upper()
            
            if "TOTAL" in row_label and "INDIA" not in row_label:
                if len(cols) >= 5:
                    totals["total"]["values_usd"]["y2023_2024"] = _parse_numeric(cols[2].get_text(strip=True))
                    totals["total"]["values_usd"]["y2024_2025"] = _parse_numeric(cols[3].get_text(strip=True))
                    totals["total"]["values_usd"]["pct_growth"] = _parse_numeric(cols[4].get_text(strip=True))
            elif "INDIA" in row_label and "TOTAL" in row_label:
                if len(cols) >= 5:
                    totals["india_total"]["values_usd"]["y2023_2024"] = _parse_numeric(cols[2].get_text(strip=True))
                    totals["india_total"]["values_usd"]["y2024_2025"] = _parse_numeric(cols[3].get_text(strip=True))
                    totals["india_total"]["values_usd"]["pct_growth"] = _parse_numeric(cols[4].get_text(strip=True))
            elif "SHARE" in row_label:
                if len(cols) >= 4:
                    totals["pct_share"]["y2023_2024"] = _parse_numeric(cols[2].get_text(strip=True))
                    totals["pct_share"]["y2024_2025"] = _parse_numeric(cols[3].get_text(strip=True))
    except Exception:
        pass
    
    return totals


def _parse_numeric(text: str) -> Optional[float]:
    """Parse numeric value from text."""
    if not text or text.strip() in ['-', 'N/A', '']:
        return None
    try:
        cleaned = text.strip().replace(',', '').replace(' ', '')
        return float(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None
