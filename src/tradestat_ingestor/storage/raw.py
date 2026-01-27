from pathlib import Path
from loguru import logger
from tradestat_ingestor.config.settings import settings

def save_raw_html(trade: str, hsn: str, year: str, html: str):
    base = Path(settings.raw_data_dir) / trade.lower() / hsn
    base.mkdir(parents=True, exist_ok=True)

    file_path = base / f"{year}.html"
    file_path.write_text(html, encoding="utf-8")

    logger.success(f"Raw HTML saved → {file_path}")
