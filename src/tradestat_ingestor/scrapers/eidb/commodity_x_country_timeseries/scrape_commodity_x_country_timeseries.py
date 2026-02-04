#!/usr/bin/env python3
"""
Commodity x Country-wise Trade Data Scraper for TradeStat

Scrapes trade data for a specific HS code and country combination.
Shows time series data across 5 years.

Usage Examples:
    # Fetch specific HS code for a country
    python scrape_commodity_x_country_timeseries.py --hs-code 10 --country 423 --year 2024 --type export
    python scrape_commodity_x_country_timeseries.py --hs-code 8501 --country 77 --year 2024 --type import
    
    # List common countries
    python scrape_commodity_x_country_timeseries.py --list-countries
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
from tradestat_ingestor.scrapers.eidb.commodity_x_country_timeseries import (
    fetch_commodity_country_data,
    get_base_url,
    parse_commodity_country_response,
    AVAILABLE_YEARS,
    VALUE_TYPES,
    COUNTRIES,
    get_country_name,
)


def save_json(data: dict, filepath: str) -> str:
    """Save data as JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return str(path.absolute())


def list_countries():
    """Print common countries with codes."""
    print("\nCommon Country Codes:")
    print("=" * 60)
    
    # Sort by country name
    sorted_countries = sorted(COUNTRIES.items(), key=lambda x: x[1])
    
    for code, name in sorted_countries:
        print(f"  {code:>4} - {name}")
    
    print("\n" + "=" * 60)
    print("Note: This is a partial list. See full HTML for all countries.")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Scrape commodity x country trade data from TradeStat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("--hs-code", type=str,
                        help="HS code (2, 4, 6, or 8 digits)")
    parser.add_argument("--country", type=str,
                        help="Country code (e.g., '423' for USA, '77' for China)")
    
    year_group = parser.add_mutually_exclusive_group()
    year_group.add_argument("--year", type=str, default="2024",
                            help="Year (determines 5-year range)")
    year_group.add_argument("--years", type=str, nargs="+", help="Multiple years")
    
    parser.add_argument("--type", choices=["export", "import"], default="export")
    parser.add_argument("--value-type", choices=["usd", "inr"], default="usd")
    parser.add_argument("--output", type=str, default="./src/data/raw/eidb/commodity_x_country_timeseries")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--list-countries", action="store_true", help="List common country codes")
    
    args = parser.parse_args()
    
    # Handle list-countries
    if args.list_countries:
        list_countries()
        sys.exit(0)
    
    # Validate required args
    if not args.hs_code:
        print("Error: --hs-code is required")
        sys.exit(1)
    if not args.country:
        print("Error: --country is required")
        sys.exit(1)
    
    if args.years:
        years = args.years
    else:
        years = [args.year]
    
    hs_code = args.hs_code.strip()
    country_code = args.country.strip()
    country_name = get_country_name(country_code)
    hs_level = len(hs_code)
    
    print(f"\n{'='*60}")
    print(f"Commodity x Country-wise {args.type.upper()} Data Scraper")
    print(f"{'='*60}")
    print(f"HS Code: {hs_code} (Level: {hs_level}-digit)")
    print(f"Country: {country_code} - {country_name}")
    print(f"Years: {', '.join(years)}")
    print(f"Value Type: {args.value_type.upper()}")
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
        print(f"Fetching {args.type} data for HS {hs_code}, {country_name}, FY {fiscal_year}...")
        
        try:
            html = fetch_commodity_country_data(
                session=session,
                csrf_token=csrf_token,
                trade_type=args.type,
                hs_code=hs_code,
                year=year,
                country_code=country_code,
                value_type=args.value_type
            )
            
            data = parse_commodity_country_response(
                html, args.type, hs_code, year, country_code, country_name, args.value_type
            )
            
            # Generate filename
            safe_country = country_name.replace(" ", "_").replace("&", "and").replace("'", "")
            filename = f"hs{hs_code}_{country_code}_{safe_country}_{fiscal_year}_{args.value_type}.json"
            
            output_path = os.path.join(args.output, args.type, filename)
            saved_path = save_json(data, output_path)
            
            years_covered = data["metadata"]["data_info"]["years_covered"]
            print(f"  ✓ Saved data for years {years_covered} to {saved_path}")
            
            if len(years) > 1:
                time.sleep(args.delay)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nDone!")


if __name__ == "__main__":
    main()
