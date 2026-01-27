from pathlib import Path
import json
from loguru import logger
from tradestat_ingestor.config.settings import settings


def save_parsed_json(trade: str, hsn: str, year: str, data: dict):
    """Save parsed trade data as JSON."""
    base = Path(settings.raw_data_dir) / trade.lower() / hsn
    base.mkdir(parents=True, exist_ok=True)

    file_path = base / f"{year}.json"
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.success(f"Parsed JSON saved → {file_path}")
