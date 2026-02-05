"""Storage module for EIDB Region-wise data."""

import json
import os
from typing import Dict, Any
from loguru import logger
from datetime import datetime


def get_output_path(base_dir: str, trade_type: str, hscode: str, year: str, value_type: str) -> str:
    digit_level = len(hscode)
    output_dir = os.path.join(base_dir, trade_type.lower(), f"level_{digit_level}")
    filename = f"{hscode}_{year}_{value_type}.json"
    return os.path.join(output_dir, filename)


def save_data(data: Dict[str, Any], base_dir: str, trade_type: str, hscode: str, year: str, value_type: str) -> str:
    output_path = get_output_path(base_dir, trade_type, hscode, year, value_type)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data["storage"] = {"saved_at": datetime.now().isoformat(), "file_path": output_path}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.success(f"Saved to: {output_path}")
    return output_path
