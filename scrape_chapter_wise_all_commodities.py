#!/usr/bin/env python3
"""
Chapter-wise All Commodities Trade Data Scraper for TradeStat

Scrapes chapter-wise export/import data from tradestat.commerce.gov.in
Supports HS code levels: 2, 4, 6, 8 digits

Usage Examples:
    python scrape_chapter_wise_all_commodities.py --hs-code 85 --year 2024 --type export
    python scrape_chapter_wise_all_commodities.py --hs-code 8501 --year 2024 --type export
    python scrape_chapter_wise_all_commodities.py --hs-code all --year 2024 --type export
    python scrape_chapter_wise_all_commodities.py --hs-code 85 --all-years --type export
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tradestat_ingestor.core.session import TradeStatSession
from tradestat_ingestor.scrapers.eidb.chapter_wise_all_commodities import (
    fetch_chapter_data,
    get_base_url,
    parse_chapter_wise_response,
    AVAILABLE_YEARS,
    VALUE_TYPES,
    HS_LEVELS,
)
from tradestat_ingestor.scrapers.eidb.chapter_wise_all_commodities.scraper import get_hs_level


def save_json(data: dict, filepath: str) -> str:
    """Save data as JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return str(path.absolute())


def main():
    parser = argparse.ArgumentParser(
        description="Scrape chapter-wise trade data from TradeStat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("--hs-code", type=str, default="all",
                        help="HS code (2, 4, 6, or 8 digits) or 'all'")
    
    year_group = parser.add_mutually_exclusive_group()
    year_group.add_argument("--year", type=str, help="Single year (e.g., 2024)")
    year_group.add_argument("--years", type=str, nargs="+", help="Multiple years")
    year_group.add_argument("--all-years", action="store_true", help="All years (2018-2024)")
    
    parser.add_argument("--type", choices=["export", "import"], default="export")
    parser.add_argument("--value-type", choices=["usd", "inr", "qty"], default="usd")
    parser.add_argument("--output", type=str, default="./src/data/raw/eidb/chapter_wise_all_commodities")
    parser.add_argument("--delay", type=float, default=1.0)
    
    args = parser.parse_args()
    
    if args.all_years:
        years = AVAILABLE_YEARS
    elif args.years:
        years = args.years
    elif args.year:
        years = [args.year]
    else:
        years = ["2024"]  # Default to current year
    
    hs_code = args.hs_code.strip()
    hs_level = get_hs_level(hs_code)
    
    print(f"\n{'='*60}")
    print(f"Chapter-wise {args.type.upper()} Data Scraper")
    print(f"{'='*60}")
    print(f"HS Code: {hs_code} (Level: {hs_level}-digit)")
    print(f"Years: {', '.join(years)}")
    print(f"Value Type: {VALUE_TYPES.get(args.value_type, 'USD')}")
    print(f"{'='*60}\n")
    
    base_url = get_base_url(args.type)
    print(f"Connecting to {base_url}...")
    
    try:
        ts_session = TradeStatSession(
            base_url="https://tradestat.commerce.gov.in",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        path = base_url.replace("https://tradestat.commerce.gov.in", "")
        form_data = ts_session.bootstrap(path)
        csrf_token = form_data["_token"]
        session = ts_session.session
        print("Session established.\n")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    for year in years:
        fiscal_year = f"{year}-{int(year)+1}"
        print(f"Fetching {args.type} data for HS {hs_code}, FY {fiscal_year}...")
        
        try:
            html = fetch_chapter_data(
                session=session,
                csrf_token=csrf_token,
                trade_type=args.type,
                year=year,
                hs_code=hs_code,
                value_type=args.value_type
            )
            
            data = parse_chapter_wise_response(
                html, args.type, year, hs_code, hs_level, args.value_type
            )
            
            # Generate filename
            if hs_code == "all":
                filename = f"all_chapters_{fiscal_year}_{args.value_type}.json"
            else:
                filename = f"hs{hs_code}_{fiscal_year}_{args.value_type}.json"
            
            output_path = os.path.join(args.output, args.type, f"level_{hs_level}", filename)
            saved_path = save_json(data, output_path)
            
            count = data["metadata"]["data_info"]["record_count"]
            warning = data["metadata"]["data_info"].get("warning")
            
            if warning:
                print(f"  ⚠ WARNING: {warning}")
                print(f"  ✗ No data saved (HS code not found)")
            else:
                print(f"  ✓ Saved {count} records to {saved_path}")
            
            if len(years) > 1:
                time.sleep(args.delay)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nDone!")


if __name__ == "__main__":
    main()
