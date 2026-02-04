"""
Storage utilities for commodity-wise data.
Handles saving scraped data to JSON files.
"""

import json
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from datetime import datetime


def get_output_dir(trade_type: str = "export") -> Path:
    """Get the output directory for commodity-wise data."""
    data_root = Path(__file__).parent.parent.parent.parent / "data"
    output_dir = data_root / "raw" / "commodity_wise" / trade_type
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_commodity_wise_data(
    data: Dict[str, Any],
    hscode: str,
    year: str,
    trade_type: str = "export",
    value_type: str = "usd"
) -> Path:
    """
    Save commodity-wise data to a JSON file.
    
    Args:
        data: Parsed data dictionary
        hscode: HS code
        year: Financial year
        trade_type: "export" or "import"
        value_type: "usd", "inr", or "quantity"
        
    Returns:
        Path to the saved file
    """
    output_dir = get_output_dir(trade_type)
    
    # Filename: {hscode}_{year}_{value_type}.json
    filename = f"{hscode}_{year}_{value_type}.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Saved commodity-wise data to: {filepath}")
    return filepath


def save_all_commodities_data(
    data: Dict[str, Any],
    digit_level: int,
    year: str,
    trade_type: str = "export",
    value_type: str = "usd"
) -> Path:
    """
    Save all commodities data at a digit level to a JSON file.
    
    Args:
        data: Parsed data dictionary
        digit_level: HS code digit level (2, 4, 6, 8)
        year: Financial year
        trade_type: "export" or "import"
        value_type: "usd", "inr", or "quantity"
        
    Returns:
        Path to the saved file
    """
    output_dir = get_output_dir(trade_type)
    
    # Filename: all_{digit_level}digit_{year}_{value_type}.json
    filename = f"all_{digit_level}digit_{year}_{value_type}.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Saved all commodities data to: {filepath}")
    return filepath
