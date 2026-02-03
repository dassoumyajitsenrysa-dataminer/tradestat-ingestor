"""
Storage utilities for commodity-wise data.
"""

import json
from pathlib import Path
from typing import Dict, Any


def get_output_dir(trade_type: str = "export") -> Path:
    """Get the output directory for commodity-wise data."""
    data_root = Path(__file__).parent.parent / "data"
    output_dir = data_root / trade_type
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_commodity_wise_data(
    data: Dict[str, Any],
    hscode: str,
    year: str,
    trade_type: str = "export",
    value_type: str = "usd"
) -> Path:
    """Save commodity-wise data to a JSON file."""
    output_dir = get_output_dir(trade_type)
    filename = f"{hscode}_{year}_{value_type}.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[+] Saved: {filepath}")
    return filepath


def save_all_commodities_data(
    data: Dict[str, Any],
    digit_level: int,
    year: str,
    trade_type: str = "export",
    value_type: str = "usd"
) -> Path:
    """Save all commodities data to a JSON file."""
    output_dir = get_output_dir(trade_type)
    filename = f"all_{digit_level}digit_{year}_{value_type}.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[+] Saved: {filepath}")
    return filepath
