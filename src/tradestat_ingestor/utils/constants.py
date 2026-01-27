from pathlib import Path

# Website URL endpoints
EXPORT_PATH = "/eidb/commodity_wise_all_countries_export"

# Local data storage paths
DATA_ROOT = Path(__file__).parent.parent.parent / "data"
EXPORT_DATA_DIR = DATA_ROOT / "raw" / "export"
IMPORT_DATA_DIR = DATA_ROOT / "raw" / "import"

# Ensure directories exist
EXPORT_DATA_DIR.mkdir(parents=True, exist_ok=True)
IMPORT_DATA_DIR.mkdir(parents=True, exist_ok=True)

