"""
Import-specific configuration and constants
"""
from pathlib import Path

# Import endpoint
IMPORT_PATH = "/eidb/commodity_wise_import"

# Import data storage
DATA_ROOT = Path(__file__).parent.parent.parent / "data"
IMPORT_DATA_DIR = DATA_ROOT / "raw" / "import"

# Ensure directory exists
IMPORT_DATA_DIR.mkdir(parents=True, exist_ok=True)
