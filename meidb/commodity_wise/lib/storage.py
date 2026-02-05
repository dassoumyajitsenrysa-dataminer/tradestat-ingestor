"""Storage for MEIDB Commodity-wise data."""

import json
import os
from typing import Dict, Any
from loguru import logger
from datetime import datetime

MONTH_ABBR = {1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
              7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"}


def get_output_path(base_dir: str, trade_type: str, hscode: str, month: int, year: int, value_type: str) -> str:
    digit_level = len(hscode)
    output_dir = os.path.join(base_dir, trade_type.lower(), f"level_{digit_level}")
    month_abbr = MONTH_ABBR.get(month, str(month))
    filename = f"{hscode}_{month_abbr}_{year}_{value_type}.json"
    return os.path.join(output_dir, filename)


def save_data(data: Dict[str, Any], base_dir: str, trade_type: str, hscode: str, month: int, year: int, value_type: str) -> str:
    output_path = get_output_path(base_dir, trade_type, hscode, month, year, value_type)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data["storage"] = {"saved_at": datetime.now().isoformat(), "file_path": output_path}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.success(f"Saved to: {output_path}")
    return output_path
