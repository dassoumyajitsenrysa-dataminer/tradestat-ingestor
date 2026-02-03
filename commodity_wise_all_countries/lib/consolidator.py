"""
Consolidator for multi-year commodity data.
Merges parsed data from multiple years into a single JSON structure.
"""

from typing import Dict, List, Any
from datetime import datetime


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
        print(f"[!] No data to consolidate for HSN={hsn}")
        return {}
    
    sorted_years = sorted(parsed_years_data.keys(), reverse=True)
    
    consolidated = {
        "hsn_code": hsn,
        "years": {},
        "metadata": {
            "consolidated_at": datetime.now().isoformat(),
            "trade_type": trade_type,
            "years_count": len(sorted_years),
            "years_included": sorted_years,
            "schema_version": "2.0",
        }
    }
    
    for year in sorted_years:
        if parsed_years_data[year]:
            consolidated["years"][year] = parsed_years_data[year]
    
    print(f"[+] Consolidated {len(sorted_years)} years for HSN={hsn}")
    return consolidated
