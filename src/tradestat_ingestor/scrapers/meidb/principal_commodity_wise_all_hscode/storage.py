"""
Storage for MEIDB Principal Commodity-wise All HSCode data.
"""

import json
import os
from typing import Dict, Any
from loguru import logger
from datetime import datetime

MONTH_ABBR = {
    1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
    7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"
}


def get_output_path(base_dir: str, trade_type: str, commodity_code: str, month: int, year: int, value_type: str) -> str:
    """
    Generate the output file path for the scraped data.
    
    Args:
        base_dir: Base directory for output
        trade_type: "export" or "import"
        commodity_code: Principal commodity code (e.g., A1)
        month: Month (1-12)
        year: Year
        value_type: "usd", "inr", or "quantity"
    
    Returns:
        Full path to the output file
    """
    output_dir = os.path.join(base_dir, "meidb", "principal_commodity_wise_all_hscode", trade_type.lower())
    month_abbr = MONTH_ABBR.get(month, str(month))
    filename = f"{commodity_code.lower()}_{month_abbr}_{year}_{value_type}.json"
    return os.path.join(output_dir, filename)


def save_meidb_principal_commodity_wise_all_hscode_data(
    data: Dict[str, Any],
    base_dir: str,
    trade_type: str,
    commodity_code: str,
    month: int,
    year: int,
    value_type: str
) -> str:
    """
    Save the scraped data to a JSON file.
    
    Args:
        data: Parsed data dictionary
        base_dir: Base directory for output
        trade_type: "export" or "import"
        commodity_code: Principal commodity code
        month: Month (1-12)
        year: Year
        value_type: "usd", "inr", or "quantity"
    
    Returns:
        Path to the saved file
    """
    output_path = get_output_path(base_dir, trade_type, commodity_code, month, year, value_type)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Add storage metadata
    data["storage"] = {
        "saved_at": datetime.now().isoformat(),
        "file_path": output_path
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Saved principal commodity data to: {output_path}")
    return output_path
