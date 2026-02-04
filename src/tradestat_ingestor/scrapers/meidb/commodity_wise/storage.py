"""
Storage utilities for MEIDB commodity-wise monthly data.
Handles saving scraped data to JSON files.
"""

import json
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from datetime import datetime

# Month abbreviations for filenames
MONTH_ABBR = {
    1: "jan", 2: "feb", 3: "mar", 4: "apr",
    5: "may", 6: "jun", 7: "jul", 8: "aug",
    9: "sep", 10: "oct", 11: "nov", 12: "dec"
}


def get_output_dir(trade_type: str = "export", digit_level: int = None) -> Path:
    """Get the output directory for MEIDB commodity-wise data.
    
    Args:
        trade_type: "export" or "import"
        digit_level: HS code digit level (2, 4, 6, 8) for subdirectory organization
    
    Returns:
        Path to the output directory
    """
    data_root = Path(__file__).parent.parent.parent.parent.parent / "data"
    output_dir = data_root / "raw" / "meidb" / "commodity_wise" / trade_type
    
    # Add level subdirectory if digit_level is provided
    if digit_level is not None:
        output_dir = output_dir / f"level_{digit_level}"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_meidb_commodity_wise_data(
    data: Dict[str, Any],
    hscode: str,
    month: int,
    year: int,
    trade_type: str = "export",
    value_type: str = "usd"
) -> Path:
    """
    Save MEIDB monthly commodity-wise data to a JSON file.
    Files are organized by digit level: level_2/, level_4/, level_6/, level_8/

    Args:
        data: Parsed data dictionary
        hscode: HS code
        month: Month (1-12)
        year: Year
        trade_type: "export" or "import"
        value_type: "usd", "inr", or "quantity"

    Returns:
        Path to the saved file
    """
    # Determine digit level from HS code length
    digit_level = len(hscode)
    output_dir = get_output_dir(trade_type, digit_level)

    # Filename: {hscode}_{month}_{year}_{value_type}.json
    month_abbr = MONTH_ABBR.get(month, f"{month:02d}")
    filename = f"{hscode}_{month_abbr}_{year}_{value_type}.json"
    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.success(f"Saved MEIDB commodity-wise data to: {filepath}")
    return filepath


def save_meidb_all_commodities_data(
    data: Dict[str, Any],
    digit_level: int,
    month: int,
    year: int,
    trade_type: str = "export",
    value_type: str = "usd"
) -> Path:
    """
    Save all commodities data at a digit level to a JSON file.
    Files are organized by digit level: level_2/, level_4/, level_6/, level_8/

    Args:
        data: Parsed data dictionary
        digit_level: HS code digit level (2, 4, 6, 8)
        month: Month (1-12)
        year: Year
        trade_type: "export" or "import"
        value_type: "usd", "inr", or "quantity"

    Returns:
        Path to the saved file
    """
    output_dir = get_output_dir(trade_type, digit_level)

    # Filename: all_{digit_level}digit_{month}_{year}_{value_type}.json
    month_abbr = MONTH_ABBR.get(month, f"{month:02d}")
    filename = f"all_{digit_level}digit_{month_abbr}_{year}_{value_type}.json"
    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.success(f"Saved MEIDB all commodities data to: {filepath}")
    return filepath
