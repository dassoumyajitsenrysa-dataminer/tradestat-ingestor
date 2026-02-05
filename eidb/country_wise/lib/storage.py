"""
Storage utilities for saving scraped data.
"""

import json
import os
from pathlib import Path


def save_json(data: dict, filepath: str) -> str:
    """Save data as JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(path.absolute())


def get_output_path(
    base_dir: str,
    trade_type: str,
    year: str,
    country_code: str = "all",
    country_name: str = "all",
    value_type: str = "usd"
) -> str:
    """Generate output file path based on parameters."""
    fiscal_year = f"{year}-{int(year)+1}"
    
    if country_code == "all":
        filename = f"all_countries_{fiscal_year}_{value_type}.json"
        path = os.path.join(base_dir, trade_type, filename)
    else:
        safe_name = country_name.replace(" ", "_").replace(".", "").replace("'", "")
        filename = f"{safe_name}_{fiscal_year}_{value_type}.json"
        path = os.path.join(base_dir, trade_type, "by_country", filename)
    
    return path
