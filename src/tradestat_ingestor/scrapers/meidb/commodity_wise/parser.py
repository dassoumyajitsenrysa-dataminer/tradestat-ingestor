"""
Parser for MEIDB Commodity-wise monthly data tables.
Extracts structured data from HTML responses.
"""

import re
import hashlib
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime

# Month mapping
MONTHS = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


def parse_meidb_commodity_wise_html(
    html: str,
    hscode: str,
    month: int,
    year: int,
    trade_type: str = "export",
    value_type: str = "usd",
    year_type: str = "financial"
) -> Optional[Dict[str, Any]]:
    """
    Parse MEIDB monthly commodity-wise trade data from HTML response.

    Args:
        html: HTML response content
        hscode: HS code (or "all_Xdigit" for all commodities)
        month: Month (1-12)
        year: Year
        trade_type: "export" or "import"
        value_type: "usd", "inr", or "quantity"
        year_type: "financial" or "calendar"

    Returns:
        Parsed data dictionary with comprehensive metadata or None if parsing fails
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        extract_start = datetime.now()

        # Extract report date
        report_date = _extract_report_date(soup)

        # Extract table data
        commodities = _extract_commodities_data(soup, value_type)

        # Extract India's total
        india_total = _extract_india_total(soup, value_type)

        # Extract column headers
        column_headers = _extract_column_headers(soup)

        # Calculate data quality metrics
        total_records = len(commodities)
        # Check for complete data using the new field names
        records_with_data = sum(1 for c in commodities if c.get('month_curr_year') is not None)
        data_completeness = (records_with_data / total_records * 100) if total_records > 0 else 0
        extract_duration = (datetime.now() - extract_start).total_seconds()

        # Value type labels
        value_labels = {
            "usd": "US $ Million",
            "inr": "₹ Crore",
            "quantity": "Quantity"
        }

        # Determine digit level
        if hscode.startswith("all_"):
            digit_level = int(hscode.split("_")[1].replace("digit", ""))
        else:
            digit_level = len(hscode)

        # Build the parsed data for checksum
        parsed_data = {
            "commodities": commodities,
            "india_total": india_total,
        }
        checksum = hashlib.md5(str(parsed_data).encode()).hexdigest()

        month_name = MONTHS.get(month, str(month))

        return {
            "metadata": {
                "extraction": {
                    "scraped_at": datetime.now().isoformat(),
                    "feature": "meidb_commodity_wise",
                    "hscode": hscode,
                    "digit_level": digit_level,
                    "month": month,
                    "month_name": month_name,
                    "year": year,
                    "period": f"{month_name} {year}",
                    "trade_type": trade_type,
                    "value_type": value_type,
                    "value_unit": value_labels.get(value_type, "US $ Million"),
                    "year_type": year_type,
                    "source_url": f"https://tradestat.commerce.gov.in/meidb/commoditywise_{trade_type}",
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
                    "last_schema_update": "2026-02-04"
                },
                "lineage": {
                    "data_source_url": f"https://tradestat.commerce.gov.in/meidb/commoditywise_{trade_type}",
                    "extraction_point": "meidb_commodity_wise",
                    "processing_chain": ["scrape_html", "parse_html", "extract_table", "validate_data"],
                    "transformations_applied": ["HTML_to_JSON", "Value_Normalization", "Missing_Data_Handling"]
                }
            },
            "column_headers": column_headers,
            "commodities": commodities,
            "india_total": india_total,
            "data_quality": {
                "total_records": total_records,
                "records_with_complete_data": records_with_data,
                "records_with_missing_data": total_records - records_with_data,
                "extraction_completeness_percent": round(data_completeness, 2),
                "extraction_duration_seconds": round(extract_duration, 3),
                "validation_status": "VALID" if data_completeness >= 70 else "PARTIAL" if data_completeness >= 50 else "INCOMPLETE"
            },
            "schema": {
                "version": "2.0",
                "parser_version": "1.0",
                "last_updated": "2026-02-04",
                "fields": {
                    "commodities": [
                        "sno", "hscode", "commodity",
                        "month_prev_year", "month_curr_year", "month_yoy_growth_pct",
                        "cumulative_prev_year", "cumulative_curr_year", "cumulative_yoy_growth_pct"
                    ],
                    "india_total": [
                        "month_prev_year", "month_curr_year", "month_yoy_growth_pct",
                        "cumulative_prev_year", "cumulative_curr_year", "cumulative_yoy_growth_pct"
                    ]
                }
            },
            "processing": {
                "status": "SUCCESS" if total_records > 0 else "NO_DATA",
                "errors": [],
                "warnings": [],
                "processing_timestamp": datetime.now().isoformat(),
                "data_source": "tradestat.commerce.gov.in",
                "report_type": "meidb_commodity_wise",
                "extraction_method": "BeautifulSoup_HTML_Parser",
                "environment": "production"
            },
            "data_manifest": {
                "extraction_status": "SUCCESS" if total_records > 0 else "FAILED",
                "records_extracted": total_records,
                "data_completeness_percent": round(data_completeness, 2),
                "validation_status": "VALID" if data_completeness >= 70 else "PARTIAL" if data_completeness >= 50 else "INCOMPLETE",
                "checksum_md5": checksum,
                "retention_policy": "LONG_TERM_ARCHIVE",
                "reuse_conditions": "OPEN_DATA_CCBY4.0"
            },
            "audit_trail": {
                "operator": "automated_scraper",
                "execution_environment": "production",
                "scraper_configuration": {
                    "hscode": hscode,
                    "month": month,
                    "year": year,
                    "trade_type": trade_type,
                    "value_type": value_type,
                    "year_type": year_type,
                    "feature": "meidb_commodity_wise"
                }
            }
        }

    except Exception as e:
        logger.error(f"Error parsing MEIDB HTML for HS={hscode}, MONTH={month}/{year}: {e}")
        return None


def _extract_report_date(soup: BeautifulSoup) -> Optional[str]:
    """Extract report date from the page."""
    try:
        # Look for text like "Report Dated: 03 Feb 2026" or "Data last updated on: 21/01/2026"
        text = soup.get_text()
        match = re.search(r'Report Dated:\s*(\d{1,2}\s+\w+\s+\d{4})', text)
        if match:
            return match.group(1)
        match = re.search(r'Data last updated on:\s*(\d{1,2}/\d{1,2}/\d{4})', text)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def _extract_column_headers(soup: BeautifulSoup) -> List[str]:
    """Extract column headers from table."""
    headers = []
    try:
        table = soup.find("table")
        if table:
            header_row = table.find("tr")
            if header_row:
                for th in header_row.find_all(["th", "td"]):
                    headers.append(th.get_text(strip=True))
    except Exception:
        pass
    return headers


def _extract_commodities_data(soup: BeautifulSoup, value_type: str) -> List[Dict[str, Any]]:
    """Extract commodities data from the table.
    
    MEIDB Commodity-wise table has 9 columns:
    1. S. (Serial No)
    2. HS Code
    3. Commodity
    4. {PrevMonth}-{PrevYear} (R) - Previous year same month value (Revised)
    5. {CurrMonth}-{CurrYear} (F) - Current month value (Final)
    6. % Growth - Month-on-month growth
    7. Apr-{PrevMonth} {PrevYear} (R) - Cumulative previous year
    8. Apr-{CurrMonth} {CurrYear} (F) - Cumulative current year
    9. % Growth - Cumulative growth
    """
    commodities = []

    try:
        table = soup.find("table")
        if not table:
            logger.warning("No table found in HTML")
            return commodities

        rows = table.find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 6:
                continue

            # Skip totals row
            cell_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            if "Total" in cell_text or "India" in cell_text:
                continue

            try:
                sno = cells[0].get_text(strip=True)
                # Skip if sno is not a number (header or footer rows)
                if not sno.isdigit():
                    continue

                # MEIDB has 9 columns:
                # S., HS Code, Commodity, Month-PrevYear, Month-CurrYear, %Growth(YoY), Cumulative-PrevYear, Cumulative-CurrYear, %Growth(YoY)
                commodity_data = {
                    "sno": int(sno),
                    "hscode": cells[1].get_text(strip=True),
                    "commodity": cells[2].get_text(strip=True),
                    # Same month comparison (Year-over-Year)
                    "month_prev_year": _parse_number(cells[3].get_text(strip=True)) if len(cells) > 3 else None,
                    "month_curr_year": _parse_number(cells[4].get_text(strip=True)) if len(cells) > 4 else None,
                    "month_yoy_growth_pct": _parse_number(cells[5].get_text(strip=True)) if len(cells) > 5 else None,
                    # Cumulative Apr-Month comparison (Year-over-Year)
                    "cumulative_prev_year": _parse_number(cells[6].get_text(strip=True)) if len(cells) > 6 else None,
                    "cumulative_curr_year": _parse_number(cells[7].get_text(strip=True)) if len(cells) > 7 else None,
                    "cumulative_yoy_growth_pct": _parse_number(cells[8].get_text(strip=True)) if len(cells) > 8 else None,
                }
                commodities.append(commodity_data)
            except (IndexError, ValueError) as e:
                logger.debug(f"Skipping row due to parsing error: {e}")
                continue

    except Exception as e:
        logger.error(f"Error extracting commodities data: {e}")

    return commodities


def _extract_india_total(soup: BeautifulSoup, value_type: str) -> Optional[Dict[str, Any]]:
    """Extract India's total export/import row.
    
    The total row has the same 9 columns as commodity rows.
    """
    try:
        table = soup.find("table")
        if not table:
            return None

        rows = table.find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue

            # Look for India's Total row
            row_text = row.get_text()
            if "India's Total" in row_text or "India Total" in row_text:
                # Extract all numeric values from the row (columns 3-8)
                try:
                    return {
                        # Same month comparison (Year-over-Year)
                        "month_prev_year": _parse_number(cells[3].get_text(strip=True)) if len(cells) > 3 else None,
                        "month_curr_year": _parse_number(cells[4].get_text(strip=True)) if len(cells) > 4 else None,
                        "month_yoy_growth_pct": _parse_number(cells[5].get_text(strip=True)) if len(cells) > 5 else None,
                        # Cumulative Apr-Month comparison (Year-over-Year)
                        "cumulative_prev_year": _parse_number(cells[6].get_text(strip=True)) if len(cells) > 6 else None,
                        "cumulative_curr_year": _parse_number(cells[7].get_text(strip=True)) if len(cells) > 7 else None,
                        "cumulative_yoy_growth_pct": _parse_number(cells[8].get_text(strip=True)) if len(cells) > 8 else None,
                    }
                except (IndexError, ValueError):
                    pass
    except Exception as e:
        logger.error(f"Error extracting India total: {e}")

    return None


def _parse_number(text: str) -> Optional[float]:
    """Parse a number from text, handling commas and special characters."""
    if not text or text == "-" or text == "NA" or text == "N/A":
        return None
    try:
        # Remove commas and whitespace
        cleaned = text.replace(",", "").replace(" ", "").strip()
        return float(cleaned)
    except ValueError:
        return None


# Legacy function for backward compatibility
def parse_commodity_wise_html(html, trade_type, month, year, hs_level, value_type, year_type, comlev, comval=None):
    """
    Parse the HTML response for commodity-wise monthly data.
    Returns: list of dicts (one per row)
    """
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table')
    if not table:
        raise ValueError('No data table found in response')
    
    headers = [th.get_text(strip=True) for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr')[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all('td')]
        if not cells or len(cells) != len(headers):
            continue
        row = dict(zip(headers, cells))
        rows.append(row)
    return rows
