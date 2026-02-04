#!/usr/bin/env python3
"""
Region-wise All Commodities Trade Data Scraper for TradeStat

Scrapes region-wise commodity export/import data from tradestat.commerce.gov.in
Supports HS code levels: 2, 4, 6, 8 digits
Supports all regions and sub-regions

Usage Examples:
    # Fetch all 2-digit commodities for ASEAN
    python scrape_region_wise_all_commodities.py --region 420 --hs-code all --year 2024 --type export
    
    # Fetch specific HS code for a region
    python scrape_region_wise_all_commodities.py --region 420 --hs-code 85 --year 2024 --type export
    python scrape_region_wise_all_commodities.py --region 310 --hs-code 8501 --year 2024 --type import
    python scrape_region_wise_all_commodities.py --region 1 --hs-code 85011011 --all-years --type export
    
    # List all regions
    python scrape_region_wise_all_commodities.py --list-regions
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
from tradestat_ingestor.scrapers.eidb.region_wise_all_commodities import (
    fetch_region_commodities_data,
    get_base_url,
    parse_region_commodities_response,
    AVAILABLE_YEARS,
    VALUE_TYPES,
    HS_LEVELS,
    REGIONS,
    get_region_name,
)


def save_json(data: dict, filepath: str) -> str:
    """Save data as JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return str(path.absolute())


def list_regions():
    """Print all available regions."""
    print("\nAvailable Regions:")
    print("=" * 60)
    
    # Group by main region
    main_regions = {k: v for k, v in REGIONS.items() if len(k) == 1}
    
    for code, name in sorted(main_regions.items()):
        print(f"\n{code} - {name}")
        
        # Find sub-regions
        sub_regions = {k: v for k, v in REGIONS.items() if len(k) > 1 and k.startswith(code)}
        for sub_code, sub_name in sorted(sub_regions.items()):
            print(f"    {sub_code} - {sub_name}")
    
    print("\n" + "=" * 60)


def get_hs_level(hs_code: str) -> str:
    """Determine the HS level from the code length."""
    if hs_code == "all":
        return "2"
    length = len(hs_code)
    if length <= 2:
        return "2"
    elif length <= 4:
        return "4"
    elif length <= 6:
        return "6"
    else:
        return "8"


def main():
    parser = argparse.ArgumentParser(
        description="Scrape region-wise commodity trade data from TradeStat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("--region", type=str, default="1",
                        help="Region code (e.g., '1' for Europe, '420' for ASEAN)")
    parser.add_argument("--hs-code", type=str, default="all",
                        help="HS code (2, 4, 6, or 8 digits) or 'all' for all commodities at that level")
    
    year_group = parser.add_mutually_exclusive_group()
    year_group.add_argument("--year", type=str, help="Single year (e.g., 2024)")
    year_group.add_argument("--years", type=str, nargs="+", help="Multiple years")
    year_group.add_argument("--all-years", action="store_true", help="All years (2018-2024)")
    
    parser.add_argument("--type", choices=["export", "import"], default="export")
    parser.add_argument("--value-type", choices=["usd", "inr", "qty"], default="usd")
    parser.add_argument("--output", type=str, default="./src/data/raw/eidb/region_wise_all_commodities")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--list-regions", action="store_true", help="List all available regions")
    
    args = parser.parse_args()
    
    # Handle list-regions
    if args.list_regions:
        list_regions()
        sys.exit(0)
    
    if args.all_years:
        years = AVAILABLE_YEARS
    elif args.years:
        years = args.years
    elif args.year:
        years = [args.year]
    else:
        years = ["2024"]  # Default to current year
    
    region_code = args.region.strip()
    region_name = get_region_name(region_code)
    hs_code = args.hs_code.strip()
    hs_level = get_hs_level(hs_code)
    
    print(f"\n{'='*60}")
    print(f"Region-wise All Commodities {args.type.upper()} Data Scraper")
    print(f"{'='*60}")
    print(f"Region: {region_code} - {region_name}")
    print(f"HS Code: {hs_code} (Level: {hs_level}-digit)")
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
        print(f"Fetching {args.type} data for {region_name}, HS {hs_code}, FY {fiscal_year}...")
        
        try:
            html = fetch_region_commodities_data(
                session=session,
                csrf_token=csrf_token,
                trade_type=args.type,
                year=year,
                region_code=region_code,
                hs_level=hs_level,
                value_type=args.value_type
            )
            
            data = parse_region_commodities_response(
                html, args.type, year, region_code, region_name, hs_level, args.value_type, hs_code
            )
            
            # Generate filename
            # Make region name filesystem safe
            safe_region = region_name.replace(" ", "_").replace("&", "and").replace("(", "").replace(")", "").replace("-", "_")
            if hs_code == "all":
                filename = f"region_{region_code}_{safe_region}_all_level{hs_level}_{fiscal_year}_{args.value_type}.json"
            else:
                filename = f"region_{region_code}_{safe_region}_hs{hs_code}_{fiscal_year}_{args.value_type}.json"
            
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
