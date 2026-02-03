#!/usr/bin/env python3
"""
CLI to scrape commodity-wise data from tradestat.commerce.gov.in

Usage: 
    python scrape_commodity_wise.py --hscode 27 --year 2024 --type export
    python scrape_commodity_wise.py --hscode 27101944 --year 2024 --type export --value-type quantity
    python scrape_commodity_wise.py --hscode 27 --all-years --type export
    python scrape_commodity_wise.py --all --digit-level 2 --year 2024 --type export
"""

import sys
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from session import TradeStatSession
from scraper import (
    scrape_commodity_wise,
    scrape_commodity_wise_all,
    COMMODITY_WISE_EXPORT_PATH,
    COMMODITY_WISE_IMPORT_PATH
)
from parser import parse_commodity_wise_html
from storage import save_commodity_wise_data, save_all_commodities_data


# Configuration
BASE_URL = os.getenv("BASE_URL", "https://tradestat.commerce.gov.in")
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

# Available years
AVAILABLE_YEARS = ["2024", "2023", "2022", "2021", "2020", "2019", "2018"]


def main():
    parser = argparse.ArgumentParser(
        description="Scrape commodity-wise trade data from tradestat.commerce.gov.in"
    )
    
    # Mode
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--hscode", help="Specific HS code (2, 4, 6, or 8 digit)")
    mode_group.add_argument("--all", action="store_true", help="Scrape all commodities at digit level")
    
    parser.add_argument("--digit-level", type=int, choices=[2, 4, 6, 8], help="Digit level (with --all)")
    
    # Year options
    year_group = parser.add_mutually_exclusive_group()
    year_group.add_argument("--year", help="Financial year (e.g., 2024)")
    year_group.add_argument("--years", help="Multiple years: comma-separated")
    year_group.add_argument("--all-years", action="store_true", help="All available years")
    
    parser.add_argument("--type", choices=["export", "import"], default="export", help="Trade type")
    parser.add_argument("--value-type", choices=["usd", "inr", "quantity"], default="usd", help="Value type")
    
    args = parser.parse_args()
    
    # Validate
    if args.all and not args.digit_level:
        parser.error("--digit-level required with --all")
    
    if args.value_type == "quantity":
        if args.hscode and len(args.hscode) != 8:
            parser.error("Quantity only available at 8-digit level")
        if args.all and args.digit_level != 8:
            parser.error("Quantity only available at 8-digit level")
    
    # Parse years
    if args.all_years:
        years = AVAILABLE_YEARS
    elif args.years:
        years = [y.strip() for y in args.years.split(",")]
    elif args.year:
        years = [args.year]
    else:
        years = [AVAILABLE_YEARS[0]]
    
    # Bootstrap path
    bootstrap_path = COMMODITY_WISE_EXPORT_PATH if args.type == "export" else COMMODITY_WISE_IMPORT_PATH
    
    print(f"\n{'='*60}")
    print(f"COMMODITY-WISE {args.type.upper()} SCRAPER")
    print(f"{'='*60}")
    if args.hscode:
        print(f"HS Code: {args.hscode} ({len(args.hscode)}-digit)")
    else:
        print(f"Mode: All {args.digit_level}-digit commodities")
    print(f"Years: {', '.join(years)}")
    print(f"Value Type: {args.value_type.upper()}")
    print(f"{'='*60}\n")
    
    successful = 0
    failed = 0
    
    try:
        # Initialize session
        session_obj = TradeStatSession(base_url=BASE_URL, user_agent=USER_AGENT)
        state = session_obj.bootstrap(bootstrap_path)
        
        if not state:
            print("[!] Failed to bootstrap session")
            return 1
        
        # Scrape each year
        for year in years:
            print(f"\n[*] Processing year {year}...")
            
            if args.hscode:
                response = scrape_commodity_wise(
                    session=session_obj.session,
                    base_url=BASE_URL,
                    hscode=args.hscode,
                    year=year,
                    trade_type=args.type,
                    value_type=args.value_type,
                    state=state,
                )
            else:
                response = scrape_commodity_wise_all(
                    session=session_obj.session,
                    base_url=BASE_URL,
                    digit_level=args.digit_level,
                    year=year,
                    trade_type=args.type,
                    value_type=args.value_type,
                    state=state,
                )
            
            if response:
                hscode_for_parse = args.hscode if args.hscode else f"all_{args.digit_level}digit"
                parsed_data = parse_commodity_wise_html(
                    response, hscode_for_parse, year, args.type, args.value_type
                )
                
                if parsed_data:
                    count = len(parsed_data.get('commodities', []))
                    print(f"[+] Parsed {count} records")
                    
                    if args.hscode:
                        save_commodity_wise_data(parsed_data, args.hscode, year, args.type, args.value_type)
                    else:
                        save_all_commodities_data(parsed_data, args.digit_level, year, args.type, args.value_type)
                    
                    india_total = parsed_data.get('india_total')
                    if india_total and india_total.get('curr_year_value'):
                        print(f"[i] India's Total: {india_total['curr_year_value']:,.2f}")
                    
                    successful += 1
                else:
                    print("[!] Parsing failed")
                    failed += 1
            else:
                print(f"[!] Scrape failed")
                failed += 1
        
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
