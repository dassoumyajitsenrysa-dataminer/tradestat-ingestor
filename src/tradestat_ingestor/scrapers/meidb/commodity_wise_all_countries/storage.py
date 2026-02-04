"""
Storage utilities for MEIDB commodity-wise all countries data.
Handles saving parsed data to JSON files with proper directory structure.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

# Month short names for filenames
MONTH_SHORT = {
    1: "jan", 2: "feb", 3: "mar", 4: "apr",
    5: "may", 6: "jun", 7: "jul", 8: "aug",
    9: "sep", 10: "oct", 11: "nov", 12: "dec"
}


def get_output_path(
    base_dir: str,
    hscode: str,
    month: int,
    year: int,
    trade_type: str = "export",
    value_type: str = "usd",
    year_type: str = "financial"
) -> Path:
    """
    Generate output path for the JSON file.
    
    Structure: base_dir/meidb/commodity_wise_all_countries/{trade_type}/level_{digit}/{hscode}_{month}_{year}_{value_type}.json
    
    Example: src/data/raw/meidb/commodity_wise_all_countries/export/level_8/85171300_nov_2025_usd.json
    """
    digit_level = len(hscode)
    month_short = MONTH_SHORT.get(month, str(month).zfill(2))
    
    # Include year_type in filename if not financial (default)
    if year_type.lower() == "calendar":
        filename = f"{hscode}_{month_short}_{year}_{value_type}_cal.json"
    else:
        filename = f"{hscode}_{month_short}_{year}_{value_type}.json"
    
    output_path = Path(base_dir) / "meidb" / "commodity_wise_all_countries" / trade_type / f"level_{digit_level}" / filename
    
    return output_path


def save_meidb_commodity_wise_all_countries_data(
    data: Dict[str, Any],
    base_dir: str,
    hscode: str,
    month: int,
    year: int,
    trade_type: str = "export",
    value_type: str = "usd",
    year_type: str = "financial"
) -> Optional[str]:
    """
    Save parsed MEIDB commodity-wise all countries data to a JSON file.
    
    Args:
        data: Parsed data dictionary
        base_dir: Base directory for output files
        hscode: HS code
        month: Month (1-12)
        year: Year
        trade_type: "export" or "import"
        value_type: "usd", "inr", or "quantity"
        year_type: "financial" or "calendar"
        
    Returns:
        Path to saved file, or None if save failed
    """
    try:
        output_path = get_output_path(
            base_dir, hscode, month, year, trade_type, value_type, year_type
        )
        
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save JSON with pretty formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.success(f"Saved MEIDB commodity-wise all countries data to: {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Failed to save data: {e}")
        return None
