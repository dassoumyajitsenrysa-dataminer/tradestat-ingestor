#!/usr/bin/env python3
"""
Region-wise Trade Data Scraper for TradeStat

Scrapes region-wise export/import data from tradestat.commerce.gov.in

Usage Examples:
    python scrape_region_wise.py --year 2024 --type export
    python scrape_region_wise.py --year 2024 --type import --region europe
    python scrape_region_wise.py --all-years --type export --region asia
    python scrape_region_wise.py --list-regions
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
from tradestat_ingestor.scrapers.eidb.region_wise import (
    fetch_region_data,
    get_base_url,
    get_region_name,
    parse_region_wise_response,
    REGIONS,
    AVAILABLE_YEARS,
)


def find_region_code(search: str) -> tuple[str, str] | None:
    """
    Find region code by name or code.
    
    Returns (code, name) or None if not found.
    """
    search_lower = search.lower().strip()
    
    # Common aliases
    aliases = {
        "europe": "1",
        "eu": "1",
        "africa": "2",
        "america": "3",
        "americas": "3",
        "usa": "3",
        "asia": "4",
        "cis": "5",
        "baltics": "5",
        "cis & baltics": "5",
        "unspecified": "9",
    }
    
    if search_lower in aliases:
        code = aliases[search_lower]
        return (code, REGIONS[code])
    
    # Direct code match
    if search in REGIONS:
        return (search, REGIONS[search])
    
    # Name match (case-insensitive)
    for code, name in REGIONS.items():
        if code == "all":
            continue
        if name.lower() == search_lower or search_lower in name.lower():
            return (code, name)
    
    return None


def list_regions():
    """Print all available regions with their codes."""
    print("\nAvailable Regions:")
    print("-" * 30)
    for code, name in REGIONS.items():
        if code != "all":
            print(f"  {code} : {name}")
    print(f"\nTotal: {len(REGIONS) - 1} regions")


def save_json(data: dict, filepath: str) -> str:
    """Save data as JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return str(path.absolute())


def main():
    parser = argparse.ArgumentParser(
        description="Scrape region-wise trade data from TradeStat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    year_group = parser.add_mutually_exclusive_group()
    year_group.add_argument("--year", type=str, help="Single year (e.g., 2024)")
    year_group.add_argument("--years", type=str, nargs="+", help="Multiple years")
    year_group.add_argument("--all-years", action="store_true", help="All years (2018-2024)")
    
    parser.add_argument("--type", choices=["export", "import"], default="export")
    parser.add_argument("--value-type", choices=["usd", "inr"], default="usd")
    parser.add_argument("--region", type=str, help="Region name or code (e.g., 'europe', 'asia', '1')")
    parser.add_argument("--output", type=str, default="./src/data/raw/eidb/region_wise")
    parser.add_argument("--list-regions", action="store_true")
    parser.add_argument("--delay", type=float, default=1.0)
    
    args = parser.parse_args()
    
    if args.list_regions:
        list_regions()
        return
    
    if args.all_years:
        years = AVAILABLE_YEARS
    elif args.years:
        years = args.years
    elif args.year:
        years = [args.year]
    else:
        print("Error: Please specify --year, --years, or --all-years")
        sys.exit(1)
    
    # Handle region filter
    region_code = "all"
    region_name = "All Regions"
    if args.region:
        result = find_region_code(args.region)
        if result is None:
            print(f"Error: Region '{args.region}' not found. Use --list-regions to see available options.")
            sys.exit(1)
        region_code, region_name = result
    
    print(f"\n{'='*60}")
    print(f"Region-wise {args.type.upper()} Data Scraper")
    print(f"{'='*60}")
    print(f"Region: {region_name}" + (f" (code: {region_code})" if region_code != "all" else ""))
    print(f"Years: {', '.join(years)}")
    print(f"Value Type: {'US $ Million' if args.value_type == 'usd' else '₹ Crore'}")
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
        print(f"Fetching {args.type} data for {region_name}, FY {fiscal_year}...")
        
        try:
            html = fetch_region_data(
                session=session,
                csrf_token=csrf_token,
                trade_type=args.type,
                year=year,
                region_code=region_code,
                value_type=args.value_type
            )
            
            data = parse_region_wise_response(
                html, args.type, year, region_code, region_name, args.value_type
            )
            
            # Generate filename
            if region_code == "all":
                filename = f"all_regions_{fiscal_year}_{args.value_type}.json"
            else:
                safe_name = region_name.replace(" ", "_").replace("&", "and")
                filename = f"{safe_name}_{fiscal_year}_{args.value_type}.json"
            
            output_path = os.path.join(args.output, args.type, filename)
            saved_path = save_json(data, output_path)
            
            count = data["metadata"]["data_info"]["record_count"]
            print(f"  ✓ Saved {count} records to {saved_path}")
            
            if len(years) > 1:
                time.sleep(args.delay)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nDone!")


if __name__ == "__main__":
    main()
