"""
Storage module for EIDB Region-wise data.
Handles saving parsed data to JSON files with proper directory structure.
"""

import json
import os
from typing import Dict, Any
from loguru import logger
from datetime import datetime


def get_output_path(
    base_dir: str,
    trade_type: str,
    hscode: str,
    year: str,
    value_type: str
) -> str:
    """
    Generate the output file path for region-wise data.

    Args:
        base_dir: Base directory for data storage
        trade_type: "export" or "import"
        hscode: HS code
        year: Financial year
        value_type: "usd", "inr", "quantity"

    Returns:
        Full path to the output JSON file
    """
    # Determine digit level
    digit_level = len(hscode)
    
    # Build path: base_dir/eidb/region_wise/{trade_type}/level_{digit}/{hscode}_{year}_{value_type}.json
    output_dir = os.path.join(
        base_dir,
        "eidb",
        "region_wise",
        trade_type.lower(),
        f"level_{digit_level}"
    )
    
    filename = f"{hscode}_{year}_{value_type.lower()}.json"
    return os.path.join(output_dir, filename)


def save_region_wise_data(
    data: Dict[str, Any],
    base_dir: str,
    trade_type: str,
    hscode: str,
    year: str,
    value_type: str
) -> str:
    """
    Save region-wise data to a JSON file.

    Args:
        data: Parsed data dictionary
        base_dir: Base directory for data storage
        trade_type: "export" or "import"
        hscode: HS code
        year: Financial year
        value_type: "usd", "inr", "quantity"

    Returns:
        Path to the saved file
    """
    output_path = get_output_path(base_dir, trade_type, hscode, year, value_type)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Add storage metadata
    data["storage"] = {
        "saved_at": datetime.now().isoformat(),
        "file_path": output_path,
        "format": "JSON",
        "encoding": "UTF-8"
    }
    
    # Write JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Saved region-wise data to: {output_path}")
    return output_path
