from bs4 import BeautifulSoup
from typing import Dict, List, Any
from loguru import logger
import json
import re
from datetime import datetime


def parse_commodity_from_html(html: str, hsn: str = None, year: str = None) -> Dict[str, Any]:
    """
    Parse trade data from HTML response.
    Extracts commodity info and country-wise trade data with metadata.
    """
    soup = BeautifulSoup(html, "lxml")
    
    # Extract commodity information
    commodity_text = soup.find("p", string=re.compile(r"Commodity:"))
    if commodity_text:
        text = commodity_text.get_text()
        # Parse: "Commodity:09011112  COFFEE ARABICA PLANTATION`B`  Unit:KGS"
        match = re.search(r"Commodity:(\d+)\s+(.*?)\s+Unit:(\w+)", text)
        if match:
            hsn_code = match.group(1)
            description = match.group(2).strip()
            unit = match.group(3)
        else:
            hsn_code = description = unit = None
    else:
        hsn_code = description = unit = None
    
    # Extract table data
    table = soup.find("table", {"id": "example1"})
    if not table:
        logger.error("Could not find data table")
        return {}
    
    data = {
        "metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_export",
            "hsn_code": hsn_code or hsn,
            "financial_year": year,
            "schema_version": "1.0",
        },
        "commodity": {
            "hsn_code": hsn_code,
            "description": description,
            "unit": unit,
        },
        "report_date": None,
        "countries": [],
        "totals": {},
    }
    
    # Extract report date and data availability info
    report_date_text = soup.find("b", string=re.compile(r"Report Dated:"))
    if report_date_text:
        match = re.search(r"Report Dated: (.+?)\|", report_date_text.get_text())
        if match:
            data["report_date"] = match.group(1).strip()
    
    # Extract data availability from header
    header_text = soup.find("p", string=re.compile(r"Data available"))
    if header_text:
        text = header_text.get_text()
        match = re.search(r"Data available (.+?)\s+Last data updated", text)
        if match:
            data["metadata"]["data_availability"] = match.group(1).strip()
        match = re.search(r"Last data updated on (.+?)$", text)
        if match:
            data["metadata"]["last_updated"] = match.group(1).strip()
    
    # Parse table rows
    tbody = table.find("tbody")
    if tbody:
        for tr in tbody.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) >= 8:
                try:
                    row = {
                        "sno": int(_clean_text(cells[0].get_text())),
                        "country": _clean_text(cells[1].get_text()),
                        "values_usd": {
                            "y2023_2024": _to_float(cells[2].get_text()),
                            "y2024_2025": _to_float(cells[3].get_text()),
                            "pct_growth": _to_float(cells[4].get_text()),
                        },
                        "values_quantity": {
                            "y2023_2024": _to_int(cells[5].get_text()),
                            "y2024_2025": _to_int(cells[6].get_text()),
                            "pct_growth": _to_float(cells[7].get_text()),
                        },
                    }
                    data["countries"].append(row)
                except (ValueError, IndexError) as e:
                    logger.debug(f"Skipping row due to parse error: {e}")
                    continue
    
    # Parse footer (totals)
    tfoot = table.find("tfoot")
    if tfoot:
        for tr in tfoot.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) >= 2:
                label = _clean_text(cells[0].get_text() + cells[1].get_text()).replace("Total", "").replace("India's", "").strip()
                
                if "Total" in _clean_text(cells[0].get_text() + cells[1].get_text()) and "India's" not in _clean_text(cells[0].get_text() + cells[1].get_text()):
                    data["totals"]["total"] = {
                        "values_usd": {
                            "y2023_2024": _to_float(cells[2].get_text()),
                            "y2024_2025": _to_float(cells[3].get_text()),
                            "pct_growth": _to_float(cells[4].get_text()),
                        }
                    }
                elif "India's" in _clean_text(cells[0].get_text() + cells[1].get_text()):
                    data["totals"]["india_total"] = {
                        "values_usd": {
                            "y2023_2024": _to_float(cells[2].get_text()),
                            "y2024_2025": _to_float(cells[3].get_text()),
                            "pct_growth": _to_float(cells[4].get_text()),
                        }
                    }
                elif "Share" in _clean_text(cells[0].get_text() + cells[1].get_text()):
                    data["totals"]["pct_share"] = {
                        "y2023_2024": _to_float(cells[2].get_text()),
                        "y2024_2025": _to_float(cells[3].get_text()),
                    }
    
    logger.info(f"Parsed {len(data['countries'])} countries from table")
    return data


def _clean_text(text: str) -> str:
    """Clean whitespace from text."""
    return " ".join(text.split()).strip()


def _to_float(text: str) -> float | None:
    """Convert text to float, handling empty strings."""
    text = _clean_text(text)
    if not text:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def _to_int(text: str) -> int | None:
    """Convert text to int, handling empty strings."""
    text = _clean_text(text)
    if not text:
        return None
    try:
        return int(text.replace(",", ""))
    except ValueError:
        return None
