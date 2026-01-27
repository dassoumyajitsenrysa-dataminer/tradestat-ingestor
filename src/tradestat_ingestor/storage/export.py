from pathlib import Path
import json
from typing import Dict, Any, List
from loguru import logger
from tradestat_ingestor.config.settings import settings
from tradestat_ingestor.utils.constants import EXPORT_DATA_DIR
from tradestat_ingestor.utils.import_config import IMPORT_DATA_DIR
from datetime import datetime


def get_export_dir(trade: str) -> Path:
    """Get the export directory for the trade type."""
    if trade.lower() == "import":
        return IMPORT_DATA_DIR
    return EXPORT_DATA_DIR


def merge_years_to_export(trade: str, hsn: str) -> Dict[str, Any]:
    """
    Merge all year JSON files into a single consolidated export.
    """
    export_base = get_export_dir(trade)
    base_dir = export_base / hsn
    
    if not base_dir.exists():
        logger.error(f"Directory not found: {base_dir}")
        return {}
    
    # Find all JSON files (excluding the consolidated export file)
    json_files = sorted(
        [f for f in base_dir.glob("*.json") if not f.name.endswith(f"_{trade}.json")],
        key=lambda x: x.stem,
        reverse=True
    )
    
    if not json_files:
        logger.warning(f"No JSON files found in {base_dir}")
        return {}
    
    # Load and parse first file to get commodity info
    first_file_data = json.loads(json_files[0].read_text())
    
    consolidated = {
        "metadata": {
            "consolidated_at": datetime.now().isoformat(),
            "source_url": "https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_export",
            "hsn_code": hsn,
            "trade_type": trade,
            "schema_version": "2.0",
            "years_count": 0,
            "data_availability": first_file_data.get("metadata", {}).get("data_availability"),
            "last_updated": first_file_data.get("metadata", {}).get("last_updated"),
        },
        "commodity": first_file_data.get("commodity", {}),
        "years": {},
    }
    
    # Load and merge all years
    for json_file in json_files:
        try:
            data = json.loads(json_file.read_text())
            year = json_file.stem
            
            consolidated["years"][year] = {
                "report_date": data.get("report_date"),
                "scraped_at": data.get("metadata", {}).get("scraped_at"),
                "countries": data.get("countries", []),
                "totals": data.get("totals", {}),
            }
            
            logger.info(f"Merged year {year}: {len(data.get('countries', []))} countries")
            
        except Exception as e:
            logger.error(f"Failed to merge {json_file}: {str(e)}")
    
    consolidated["metadata"]["years_count"] = len(consolidated["years"])
    logger.success(f"Successfully merged {len(consolidated['years'])} years")
    
    return consolidated


def save_consolidated_export(trade: str, hsn: str, data: Dict[str, Any]) -> Path:
    """
    Save consolidated data to a single export JSON file.
    """
    export_base = get_export_dir(trade)
    hsn_dir = export_base / hsn
    hsn_dir.mkdir(parents=True, exist_ok=True)
    
    export_file = hsn_dir / f"{hsn}_{trade}.json"
    
    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.success(f"Consolidated export saved → {export_file}")
    return export_file
