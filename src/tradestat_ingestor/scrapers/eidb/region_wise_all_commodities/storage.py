"""
Storage module for EIDB Region-wise All Commodities data.
Handles saving parsed data to JSON files with proper directory structure.
"""

import json
import os
import re
from typing import Dict, Any
from loguru import logger
from datetime import datetime


def sanitize_filename(name: str) -> str:
    """Sanitize country name for use in filename."""
    # Replace spaces and special characters with underscores
    sanitized = re.sub(r'[^\w\s-]', '', name)
    sanitized = re.sub(r'[\s]+', '_', sanitized)
    return sanitized.upper()


def get_output_path(
    base_dir: str,
    trade_type: str,
    country_code: str,
    country_name: str,
    year: str,
    digit_level: int,
    value_type: str
) -> str:
    """
    Generate the output file path for region-wise all commodities data.

    Args:
        base_dir: Base directory for data storage
        trade_type: "export" or "import"
        country_code: Country code
        country_name: Country name
        year: Financial year
        digit_level: HS code level (2, 4, 6, 8)
        value_type: "usd", "inr", "quantity"

    Returns:
        Full path to the output JSON file
    """
    # Build path: base_dir/eidb/region_wise_all_commodities/{trade_type}/level_{digit}/
    output_dir = os.path.join(
        base_dir,
        "eidb",
        "region_wise_all_commodities",
        trade_type.lower(),
        f"level_{digit_level}"
    )
    
    # Filename: {country_code}_{country_name}_{year}_{value_type}.json
    country_safe = sanitize_filename(country_name)
    filename = f"{country_code}_{country_safe}_{year}_{value_type.lower()}.json"
    
    return os.path.join(output_dir, filename)


def save_region_wise_all_commodities_data(
    data: Dict[str, Any],
    base_dir: str,
    trade_type: str,
    country_code: str,
    country_name: str,
    year: str,
    digit_level: int,
    value_type: str
) -> str:
    """
    Save region-wise all commodities data to a JSON file.

    Args:
        data: Parsed data dictionary
        base_dir: Base directory for data storage
        trade_type: "export" or "import"
        country_code: Country code
        country_name: Country name
        year: Financial year
        digit_level: HS code level
        value_type: "usd", "inr", "quantity"

    Returns:
        Path to the saved file
    """
    output_path = get_output_path(
        base_dir, trade_type, country_code, country_name, 
        year, digit_level, value_type
    )
    
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
    
    logger.success(f"Saved region-wise all commodities data to: {output_path}")
    return output_path
