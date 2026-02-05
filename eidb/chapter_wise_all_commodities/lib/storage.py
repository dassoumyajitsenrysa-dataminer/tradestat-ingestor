"""
Storage module for EIDB Chapter-wise All Commodities data.
Handles saving parsed data to JSON files.
"""

import json
import os
from typing import Dict, Any
from loguru import logger
from datetime import datetime


def get_output_path(
    base_dir: str,
    trade_type: str,
    year: str,
    digit_level: int,
    value_type: str
) -> str:
    """
    Generate the output file path.
    
    Args:
        base_dir: Base directory for data storage
        trade_type: "export" or "import"
        year: Financial year
        digit_level: HS code level
        value_type: "usd" or "inr"
        
    Returns:
        Full path to the output JSON file
    """
    output_dir = os.path.join(base_dir, trade_type.lower())
    filename = f"{year}_{digit_level}digit_{value_type.lower()}.json"
    return os.path.join(output_dir, filename)


def save_data(
    data: Dict[str, Any],
    base_dir: str,
    trade_type: str,
    year: str,
    digit_level: int,
    value_type: str
) -> str:
    """
    Save chapter-wise data to a JSON file.
    
    Args:
        data: Parsed data dictionary
        base_dir: Base directory for data storage
        trade_type: "export" or "import"
        year: Financial year
        digit_level: HS code level
        value_type: "usd" or "inr"
        
    Returns:
        Path to the saved file
    """
    output_path = get_output_path(base_dir, trade_type, year, digit_level, value_type)
    
    # Create directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Add storage metadata
    data["storage"] = {
        "saved_at": datetime.now().isoformat(),
        "file_path": output_path,
    }
    
    # Write file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Saved data to: {output_path}")
    return output_path
