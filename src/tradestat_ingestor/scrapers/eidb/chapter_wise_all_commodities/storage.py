"""
Storage module for EIDB Chapter-wise All Commodities data.
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
    year: str,
    value_type: str
) -> str:
    """
    Generate the output file path for chapter-wise all commodities data.

    Args:
        base_dir: Base directory for data storage
        trade_type: "export" or "import"
        year: Financial year (e.g., "2024")
        value_type: "usd", "inr"

    Returns:
        Full path to the output JSON file
    """
    # Build path: base_dir/eidb/chapter_wise_all_commodities/{trade_type}/{year}_{value_type}.json
    output_dir = os.path.join(
        base_dir,
        "eidb",
        "chapter_wise_all_commodities",
        trade_type.lower()
    )
    
    filename = f"{year}_{value_type.lower()}.json"
    return os.path.join(output_dir, filename)


def save_chapter_wise_data(
    data: Dict[str, Any],
    base_dir: str,
    trade_type: str,
    year: str,
    value_type: str
) -> str:
    """
    Save chapter-wise all commodities data to a JSON file.

    Args:
        data: Parsed data dictionary
        base_dir: Base directory for data storage
        trade_type: "export" or "import"
        year: Financial year
        value_type: "usd", "inr"

    Returns:
        Path to the saved file
    """
    output_path = get_output_path(base_dir, trade_type, year, value_type)
    
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
    
    logger.success(f"Saved chapter-wise all commodities data to: {output_path}")
    return output_path
