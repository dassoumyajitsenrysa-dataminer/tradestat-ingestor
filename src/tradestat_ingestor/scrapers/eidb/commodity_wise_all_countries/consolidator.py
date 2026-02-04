"""
Consolidator for multi-year commodity data.
Merges parsed data from multiple years into a single JSON structure.
"""

from typing import Dict, List, Any
from datetime import datetime
from loguru import logger


def consolidate_years(
    hsn: str,
    trade_type: str,
    parsed_years_data: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Consolidate parsed data from multiple years.
    
    Args:
        hsn: HSN code
        trade_type: "export" or "import"
        parsed_years_data: Dictionary with year as key and parsed data as value
        
    Returns:
        Consolidated data structure with all years
    """
    
    if not parsed_years_data:
        logger.warning(f"No parsed data to consolidate for HSN={hsn}")
        return {}
    
    # Sort years in descending order
    sorted_years = sorted(parsed_years_data.keys(), reverse=True)
    
    consolidated = {
        "hsn_code": hsn,
        "years": {},
        "metadata": {
            "consolidated_at": datetime.now().isoformat(),
            "trade_type": trade_type,
            "years_count": len(sorted_years),
            "schema_version": "2.0",
        }
    }
    
    # Add each year's data
    for year in sorted_years:
        if parsed_years_data[year]:
            consolidated["years"][year] = parsed_years_data[year]
    
    logger.success(f"Consolidated {len(sorted_years)} years for HSN={hsn}")
    return consolidated


def merge_consolidated_files(
    consolidated_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Merge multiple consolidated files (for batch operations).
    
    Args:
        consolidated_list: List of consolidated data dictionaries
        
    Returns:
        Merged consolidated data
    """
    if not consolidated_list:
        return {}
    
    # Use first as base
    merged = consolidated_list[0]
    
    # Merge additional ones
    for consolidated in consolidated_list[1:]:
        for year, data in consolidated.get("years", {}).items():
            if year not in merged["years"]:
                merged["years"][year] = data
        
        # Update metadata
        merged["metadata"]["years_count"] = len(merged["years"])
        merged["metadata"]["consolidated_at"] = datetime.now().isoformat()
    
    return merged
