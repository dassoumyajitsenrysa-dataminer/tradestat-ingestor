"""
Storage module for EIDB Commodity x Country Timeseries data.
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
    hscode: str,
    country_code: str,
    country_name: str,
    from_year: str,
    to_year: str,
    value_type: str
) -> str:
    """
    Generate the output file path for commodity x country timeseries data.

    Args:
        base_dir: Base directory for data storage
        trade_type: "export" or "import"
        hscode: HS code
        country_code: Country code
        country_name: Country name
        from_year: Start year
        to_year: End year
        value_type: "usd", "inr", "quantity"

    Returns:
        Full path to the output JSON file
    """
    # Build path: base_dir/eidb/commodity_x_country_timeseries/{trade_type}/
    output_dir = os.path.join(
        base_dir,
        "eidb",
        "commodity_x_country_timeseries",
        trade_type.lower()
    )
    
    # Filename: hs{code}_{country_code}_{country_name}_{from}-{to}_{value_type}.json
    country_safe = sanitize_filename(country_name)
    filename = f"hs{hscode}_{country_code}_{country_safe}_{from_year}-{to_year}_{value_type.lower()}.json"
    
    return os.path.join(output_dir, filename)


def save_timeseries_data(
    data: Dict[str, Any],
    base_dir: str,
    trade_type: str,
    hscode: str,
    country_code: str,
    country_name: str,
    from_year: str,
    to_year: str,
    value_type: str
) -> str:
    """
    Save commodity x country timeseries data to a JSON file.

    Args:
        data: Parsed data dictionary
        base_dir: Base directory for data storage
        trade_type: "export" or "import"
        hscode: HS code
        country_code: Country code
        country_name: Country name
        from_year: Start year
        to_year: End year
        value_type: "usd", "inr", "quantity"

    Returns:
        Path to the saved file
    """
    output_path = get_output_path(
        base_dir, trade_type, hscode, country_code, 
        country_name, from_year, to_year, value_type
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
    
    logger.success(f"Saved timeseries data to: {output_path}")
    return output_path
