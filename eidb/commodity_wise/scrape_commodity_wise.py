#!/usr/bin/env python3
"""
CLI to scrape commodity-wise data from tradestat.commerce.gov.in

Usage: 
    # Specific HS code (any digit level)
    python scrape_commodity_wise.py --hscode 27 --year 2024 --type export
    python scrape_commodity_wise.py --hscode 2701 --year 2024 --type export
    python scrape_commodity_wise.py --hscode 27011100 --year 2024 --type export --value-type quantity
    
    # All commodities at a digit level
    python scrape_commodity_wise.py --all --digit-level 2 --year 2024 --type export
"""

import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, 'src')

from tradestat_ingestor.core.session import TradeStatSession
from tradestat_ingestor.scrapers.eidb.commodity_wise.scraper import (
    scrape_commodity_wise,
    scrape_commodity_wise_all,
    COMMODITY_WISE_EXPORT_PATH,
    COMMODITY_WISE_IMPORT_PATH
)
from tradestat_ingestor.scrapers.eidb.commodity_wise.parser import parse_commodity_wise_html
from tradestat_ingestor.scrapers.eidb.commodity_wise.storage import (
    save_commodity_wise_data,
    save_all_commodities_data
)
from tradestat_ingestor.config.settings import settings


# Available years for scraping
AVAILABLE_YEARS = ["2024", "2023", "2022", "2021", "2020", "2019", "2018"]


def main():
    parser = argparse.ArgumentParser(
        description="Scrape commodity-wise trade data from tradestat.commerce.gov.in"
    )
    
    # Mode: specific HS code or all commodities at digit level
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--hscode",
        help="Specific HS code (2, 4, 6, or 8 digit)"
    )
    mode_group.add_argument(
        "--all",
        action="store_true",
        help="Scrape all commodities at a specified digit level"
    )
    
    parser.add_argument(
        "--digit-level",
        type=int,
        choices=[2, 4, 6, 8],
        help="Digit level (required when using --all)"
    )
    
    # Year options
    year_group = parser.add_mutually_exclusive_group()
    year_group.add_argument(
        "--year",
        help="Financial year (e.g., 2024 for 2024-2025)"
    )
    year_group.add_argument(
        "--years",
        help="Multiple years: comma-separated (2022,2023,2024)"
    )
    year_group.add_argument(
        "--all-years",
        action="store_true",
        help="Scrape all available years (2018-2024)"
    )
    
    parser.add_argument(
        "--type",
        choices=["export", "import"],
        default="export",
        help="Trade type (default: export)"
    )
    
    parser.add_argument(
        "--value-type",
        choices=["usd", "inr", "quantity"],
        default="usd",
        help="Value type: usd (US $ Million), inr (₹ Crore), quantity (default: usd)"
    )
    
    parser.add_argument(
        "--output",
        help="Custom output directory (optional)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.all and not args.digit_level:
        parser.error("--digit-level is required when using --all")
    
    if args.value_type == "quantity":
        if args.hscode and len(args.hscode) != 8:
            parser.error("Quantity data is only available at 8-digit level")
        if args.all and args.digit_level != 8:
            parser.error("Quantity data is only available at 8-digit level")
    
    # Parse years
    if args.all_years:
        years = AVAILABLE_YEARS
    elif args.years:
        years = [y.strip() for y in args.years.split(",")]
    elif args.year:
        years = [args.year]
    else:
        years = [AVAILABLE_YEARS[0]]  # Default to latest year
    
    # Determine the bootstrap path based on trade type
    bootstrap_path = COMMODITY_WISE_EXPORT_PATH if args.type == "export" else COMMODITY_WISE_IMPORT_PATH
    
    print(f"[*] Scraping COMMODITY-WISE {args.type.upper()} data...")
    if args.hscode:
        print(f"   HS Code: {args.hscode} ({len(args.hscode)}-digit)")
    else:
        print(f"   Mode: All commodities at {args.digit_level}-digit level")
    print(f"   Years: {', '.join(years)}")
    print(f"   Value Type: {args.value_type.upper()}")
    print("-" * 60)
    
    successful = 0
    failed = 0
    
    try:
        # Initialize session
        session_obj = TradeStatSession(
            base_url=settings.base_url,
            user_agent=settings.user_agent,
        )
        state = session_obj.bootstrap(bootstrap_path)
        
        if not state:
            print("[!] Failed to bootstrap session")
            return 1
        
        # Scrape for each year
        for year in years:
            try:
                print(f"\n[*] Scraping year {year}...")
                
                if args.hscode:
                    # Scrape specific HS code
                    response = scrape_commodity_wise(
                        session=session_obj.session,
                        base_url=settings.base_url,
                        hscode=args.hscode,
                        year=year,
                        trade_type=args.type,
                        value_type=args.value_type,
                        state=state,
                    )
                else:
                    # Scrape all commodities at digit level
                    response = scrape_commodity_wise_all(
                        session=session_obj.session,
                        base_url=settings.base_url,
                        digit_level=args.digit_level,
                        year=year,
                        trade_type=args.type,
                        value_type=args.value_type,
                        state=state,
                    )
                
                if response:
                    print(f"   [+] Received {len(response)} bytes")
                    
                    # Parse HTML
                    hscode_for_parse = args.hscode if args.hscode else f"all_{args.digit_level}digit"
                    parsed_data = parse_commodity_wise_html(
                        response,
                        hscode_for_parse,
                        year,
                        trade_type=args.type,
                        value_type=args.value_type
                    )
                    
                    if parsed_data:
                        commodities_count = len(parsed_data.get('commodities', []))
                        print(f"   [+] Parsed {commodities_count} commodity records")
                        
                        # Save to file
                        if args.hscode:
                            filepath = save_commodity_wise_data(
                                parsed_data,
                                args.hscode,
                                year,
                                args.type,
                                args.value_type
                            )
                        else:
                            filepath = save_all_commodities_data(
                                parsed_data,
                                args.digit_level,
                                year,
                                args.type,
                                args.value_type
                            )
                        
                        print(f"   [+] Saved to: {filepath}")
                        
                        # Show India's total if available
                        india_total = parsed_data.get('india_total')
                        if india_total:
                            curr_val = india_total.get('curr_year_value')
                            prev_val = india_total.get('prev_year_value')
                            if curr_val is not None:
                                print(f"   [i] India's Total ({year}-{int(year)+1}): {curr_val:,.2f}")
                            if prev_val is not None:
                                print(f"   [i] India's Total ({int(year)-1}-{year}): {prev_val:,.2f}")
                        
                        successful += 1
                    else:
                        print(f"   [!] Parsing failed")
                        failed += 1
                else:
                    print(f"   [!] Scrape failed for year {year}")
                    failed += 1
                    
            except Exception as e:
                print(f"   [!] Error scraping year {year}: {e}")
                import traceback
                traceback.print_exc()
                failed += 1
        
        # Summary
        print("\n" + "=" * 60)
        print(f"[*] Summary:")
        print(f"   [+] Successful: {successful}")
        print(f"   [-] Failed: {failed}")
        print(f"   [*] Total: {successful + failed}")
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
