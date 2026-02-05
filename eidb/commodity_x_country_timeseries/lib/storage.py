"""Storage module for EIDB Commodity x Country Timeseries data."""

import json
import os
import re
from typing import Dict, Any
from loguru import logger
from datetime import datetime


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
    """Generate the output file path."""
    output_dir = os.path.join(base_dir, trade_type.lower())
    country_safe = re.sub(r'[^\w]', '_', country_name).upper()
    filename = f"hs{hscode}_{country_code}_{country_safe}_{from_year}-{to_year}_{value_type}.json"
    return os.path.join(output_dir, filename)


def save_data(
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
    """Save timeseries data to JSON file."""
    output_path = get_output_path(
        base_dir, trade_type, hscode, country_code,
        country_name, from_year, to_year, value_type
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data["storage"] = {"saved_at": datetime.now().isoformat(), "file_path": output_path}
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Saved to: {output_path}")
    return output_path
