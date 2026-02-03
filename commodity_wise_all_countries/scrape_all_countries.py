#!/usr/bin/env python3
"""
CLI to scrape commodity-wise all countries data from tradestat.commerce.gov.in

Usage: 
    python scrape_all_countries.py --hsn 27101944 --year 2024 --type export
    python scrape_all_countries.py --hsn 27101944 --all-years --type export --consolidate
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from session import TradeStatSession
from scraper import scrape_commodity_export, scrape_commodity_import, EXPORT_PATH
from parser import parse_commodity_html
from consolidator import consolidate_years


# Configuration
BASE_URL = os.getenv("BASE_URL", "https://tradestat.commerce.gov.in")
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

# Available years
AVAILABLE_YEARS = ["2024", "2023", "2022", "2021", "2020", "2019", "2018"]


def get_output_dir(trade_type: str) -> Path:
    """Get output directory for data files."""
    data_dir = Path(__file__).parent / "data" / trade_type
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def save_data(data: dict, hsn: str, year: str, trade_type: str) -> Path:
    """Save parsed data to JSON file."""
    output_dir = get_output_dir(trade_type)
    filepath = output_dir / f"{hsn}_{year}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[+] Saved: {filepath}")
    return filepath


def save_consolidated(data: dict, hsn: str, trade_type: str) -> Path:
    """Save consolidated data to JSON file."""
    output_dir = get_output_dir(trade_type)
    filepath = output_dir / f"{hsn}_consolidated.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[+] Saved consolidated: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Scrape commodity-wise all countries trade data"
    )
    
    parser.add_argument("--hsn", required=True, help="HSN code (e.g., 27101944)")
    
    # Year options
    year_group = parser.add_mutually_exclusive_group()
    year_group.add_argument("--year", help="Single financial year (e.g., 2024)")
    year_group.add_argument("--years", help="Multiple years: comma-separated")
    year_group.add_argument("--all-years", action="store_true", help="All available years")
    
    parser.add_argument("--type", choices=["export", "import"], default="export", help="Trade type")
    parser.add_argument("--consolidate", action="store_true", help="Consolidate all years into single file")
    parser.add_argument("--output", help="Custom output directory")
    
    args = parser.parse_args()
    
    # Parse years
    if args.all_years:
        years = AVAILABLE_YEARS
    elif args.years:
        years = [y.strip() for y in args.years.split(",")]
    elif args.year:
        years = [args.year]
    else:
        years = [AVAILABLE_YEARS[0]]
    
    print(f"\n{'='*60}")
    print(f"COMMODITY-WISE ALL COUNTRIES {args.type.upper()} SCRAPER")
    print(f"{'='*60}")
    print(f"HSN Code: {args.hsn}")
    print(f"Years: {', '.join(years)}")
    if args.consolidate:
        print(f"Mode: CONSOLIDATE")
    print(f"{'='*60}\n")
    
    successful = 0
    failed = 0
    parsed_years_data = {}
    
    try:
        # Initialize session
        session_obj = TradeStatSession(base_url=BASE_URL, user_agent=USER_AGENT)
        state = session_obj.bootstrap(EXPORT_PATH)
        
        if not state:
            print("[!] Failed to bootstrap session")
            return 1
        
        # Scrape each year
        for year in years:
            print(f"\n[*] Processing year {year}...")
            
            if args.type == "export":
                response = scrape_commodity_export(
                    session=session_obj.session,
                    base_url=BASE_URL,
                    hsn=args.hsn,
                    year=year,
                    state=state,
                )
            else:
                response = scrape_commodity_import(
                    session=session_obj.session,
                    base_url=BASE_URL,
                    hsn=args.hsn,
                    year=year,
                    state=state,
                )
            
            if response:
                parsed_data = parse_commodity_html(response, args.hsn, year)
                
                if parsed_data:
                    countries_count = len(parsed_data.get('countries', []))
                    print(f"[+] Parsed {countries_count} countries")
                    
                    if args.consolidate:
                        parsed_years_data[year] = parsed_data
                    else:
                        save_data(parsed_data, args.hsn, year, args.type)
                    
                    successful += 1
                else:
                    print("[!] Parsing failed")
                    failed += 1
            else:
                print(f"[!] Scrape failed")
                failed += 1
        
        # Consolidate if requested
        if args.consolidate and parsed_years_data:
            print(f"\n[*] Consolidating {len(parsed_years_data)} years...")
            consolidated = consolidate_years(args.hsn, args.type, parsed_years_data)
            save_consolidated(consolidated, args.hsn, args.type)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"SUMMARY: {successful} successful, {failed} failed")
        print(f"{'='*60}\n")
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
