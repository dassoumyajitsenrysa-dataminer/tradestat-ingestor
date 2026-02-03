"""
Parser for commodity-wise trade data.
Extracts structured data from HTML responses.
"""

import re
import hashlib
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime


def parse_commodity_wise_html(
    html: str, 
    hscode: str, 
    year: str,
    trade_type: str = "export",
    value_type: str = "usd"
) -> Optional[Dict[str, Any]]:
    """
    Parse commodity-wise trade data from HTML response.
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        extract_start = datetime.now()
        
        report_date = _extract_report_date(soup)
        commodities = _extract_commodities_data(soup)
        india_total = _extract_india_total(soup)
        year_columns = _extract_year_columns(soup)
        
        total_records = len(commodities)
        records_with_data = sum(1 for c in commodities if c.get('curr_year_value') is not None)
        data_completeness = (records_with_data / total_records * 100) if total_records > 0 else 0
        extract_duration = (datetime.now() - extract_start).total_seconds()
        
        value_labels = {
            "usd": "US $ Million",
            "inr": "₹ Crore",
            "quantity": "Quantity (in thousands)"
        }
        
        parsed_data = {"commodities": commodities, "india_total": india_total}
        checksum = hashlib.md5(str(parsed_data).encode()).hexdigest()
        
        return {
            "metadata": {
                "extraction": {
                    "scraped_at": datetime.now().isoformat(),
                    "feature": "commodity_wise",
                    "hscode": hscode,
                    "digit_level": len(hscode) if not hscode.startswith("all_") else int(hscode.split("_")[1].replace("digit", "")),
                    "financial_year": year,
                    "fiscal_year_range": f"{year}-{int(year)+1}",
                    "trade_type": trade_type,
                    "value_type": value_type,
                    "value_unit": value_labels.get(value_type, "US $ Million"),
                    "source_url": f"https://tradestat.commerce.gov.in/eidb/commodity_wise_{trade_type}",
                    "report_date": report_date,
                    "response_size_bytes": len(html),
                },
                "data": {
                    "data_source": "DGCI&S (Directorate General of Commercial Intelligence and Statistics)",
                    "data_provider": "Ministry of Commerce and Industry, Government of India",
                    "data_classification": "PUBLIC",
                    "temporal_granularity": "Annual (Financial Year: Apr-Mar)",
                    "geographic_coverage": "India",
                }
            },
            "year_columns": year_columns,
            "commodities": commodities,
            "india_total": india_total,
            "data_quality": {
                "total_records": total_records,
                "records_with_complete_data": records_with_data,
                "extraction_completeness_percent": round(data_completeness, 2),
                "extraction_duration_seconds": round(extract_duration, 3),
                "validation_status": "VALID" if data_completeness >= 70 else "PARTIAL" if data_completeness >= 50 else "INCOMPLETE",
                "checksum_md5": checksum,
            }
        }
    
    except Exception as e:
        print(f"[!] Parsing error: {e}")
        return None


def _extract_report_date(soup: BeautifulSoup) -> Optional[str]:
    try:
        text = soup.get_text()
        match = re.search(r'Report Dated:\s*(\d{1,2}\s+\w+\s+\d{4})', text)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def _extract_year_columns(soup: BeautifulSoup) -> Dict[str, str]:
    year_columns = {}
    try:
        table = soup.find("table")
        if table:
            headers = table.find_all("th")
            for th in headers:
                text = th.get_text(strip=True)
                if re.match(r'\d{4}\s*-\s*\d{4}', text):
                    if "prev_year" not in year_columns:
                        year_columns["prev_year"] = text
                    else:
                        year_columns["curr_year"] = text
    except Exception:
        pass
    return year_columns


def _extract_commodities_data(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    commodities = []
    try:
        table = soup.find("table")
        if not table:
            return commodities
            
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 7:
                continue
                
            cell_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            if "Total" in cell_text or "India" in cell_text:
                continue
            
            try:
                sno = cells[0].get_text(strip=True)
                if not sno.isdigit():
                    continue
                    
                commodities.append({
                    "sno": int(sno),
                    "hscode": cells[1].get_text(strip=True),
                    "commodity": cells[2].get_text(strip=True),
                    "prev_year_value": _parse_number(cells[3].get_text(strip=True)),
                    "prev_year_share_pct": _parse_number(cells[4].get_text(strip=True)),
                    "curr_year_value": _parse_number(cells[5].get_text(strip=True)),
                    "curr_year_share_pct": _parse_number(cells[6].get_text(strip=True)),
                    "growth_pct": _parse_number(cells[7].get_text(strip=True)) if len(cells) > 7 else None,
                })
            except (IndexError, ValueError):
                continue
    except Exception:
        pass
    return commodities


def _extract_india_total(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    try:
        table = soup.find("table")
        if not table:
            return None
            
        for row in table.find_all("tr"):
            row_text = row.get_text()
            if "India's Total" in row_text or "India Total" in row_text:
                cells = row.find_all("td")
                values = [_parse_number(c.get_text(strip=True)) for c in cells]
                values = [v for v in values if v is not None]
                if len(values) >= 2:
                    return {
                        "prev_year_value": values[0],
                        "curr_year_value": values[1],
                        "growth_pct": values[2] if len(values) > 2 else None
                    }
    except Exception:
        pass
    return None


def _parse_number(text: str) -> Optional[float]:
    if not text or text in ["-", "NA", "N/A"]:
        return None
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return None
