#!/usr/bin/env python3
"""
Country-wise Trade Data Scraper for TradeStat

Scrapes country-wise export/import data from tradestat.commerce.gov.in

Usage Examples:
    python scrape_country_wise.py --year 2024 --type export
    python scrape_country_wise.py --year 2024 --type export --country usa
    python scrape_country_wise.py --years 2024 2023 --type import --value-type inr
    python scrape_country_wise.py --all-years --type export --country china
    python scrape_country_wise.py --list-countries
"""

import argparse
import sys
import time
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib import (
    create_session,
    fetch_country_data,
    get_base_url,
    get_country_name,
    parse_all_countries_table,
    parse_country_wise_response,
    save_json,
    get_output_path,
    COUNTRIES,
    AVAILABLE_YEARS,
)


# Common aliases for easy lookup
COUNTRY_ALIASES = {
    "usa": "423",
    "us": "423",
    "america": "423",
    "united states": "423",
    "uk": "421",
    "britain": "421",
    "england": "421",
    "united kingdom": "421",
    "uae": "419",
    "emirates": "419",
    "china": "77",
    "germany": "147",
    "japan": "205",
    "france": "129",
    "italy": "197",
    "canada": "59",
    "australia": "17",
    "russia": "344",
    "brazil": "43",
    "singapore": "359",
    "korea": "217",
    "south korea": "217",
    "saudi": "351",
    "saudi arabia": "351",
    "bangladesh": "27",
    "nepal": "273",
    "sri lanka": "369",
    "pakistan": "309",
}


def find_country_code(search: str):
    """Find country code by name or code."""
    search_lower = search.lower().strip()
    
    # Check aliases first
    if search_lower in COUNTRY_ALIASES:
        code = COUNTRY_ALIASES[search_lower]
        return (code, COUNTRIES[code])
    
    # Direct code match
    if search in COUNTRIES:
        return (search, COUNTRIES[search])
    
    # Exact name match
    for code, name in COUNTRIES.items():
        if code == "all":
            continue
        if name.lower() == search_lower:
            return (code, name)
    
    # Normalized match (remove spaces)
    search_normalized = search_lower.replace(" ", "")
    for code, name in COUNTRIES.items():
        if code == "all":
            continue
        name_normalized = name.lower().replace(" ", "")
        if search_normalized == name_normalized:
            return (code, name)
    
    # Partial match
    matches = []
    for code, name in COUNTRIES.items():
        if code == "all":
            continue
        if search_lower in name.lower():
            matches.append((code, name))
    
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"\nMultiple matches for '{search}':")
        for code, name in matches:
            print(f"  {code:5} : {name}")
        print("Please be more specific or use the exact code.")
        return None
    
    return None


def list_countries():
    """Print all available countries with their codes."""
    print("\nAvailable Countries:")
    print("-" * 50)
    sorted_countries = sorted(COUNTRIES.items(), key=lambda x: x[1])
    for code, name in sorted_countries:
        if code != "all":
            print(f"  {code:5} : {name}")
    print(f"\nTotal: {len(COUNTRIES) - 1} countries")
    print("\nCommon aliases: usa, uk, uae, china, germany, japan, france, etc.")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape country-wise trade data from TradeStat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scrape_country_wise.py --year 2024 --type export
  python scrape_country_wise.py --year 2024 --type export --country usa
  python scrape_country_wise.py --all-years --type import --country china
  python scrape_country_wise.py --list-countries
        """
    )
    
    year_group = parser.add_mutually_exclusive_group()
    year_group.add_argument("--year", type=str, help="Single year (e.g., 2024)")
    year_group.add_argument("--years", type=str, nargs="+", help="Multiple years")
    year_group.add_argument("--all-years", action="store_true", help="All years (2018-2024)")
    
    parser.add_argument("--type", choices=["export", "import"], default="export")
    parser.add_argument("--value-type", choices=["usd", "inr"], default="usd")
    parser.add_argument("--country", type=str, help="Country name or code (e.g., 'usa', '423')")
    parser.add_argument("--output", type=str, default="./data/raw/country_wise")
    parser.add_argument("--list-countries", action="store_true")
    parser.add_argument("--delay", type=float, default=1.0)
    
    args = parser.parse_args()
    
    if args.list_countries:
        list_countries()
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
    
    # Handle country filter
    country_code = "all"
    country_name = "All Countries"
    if args.country:
        result = find_country_code(args.country)
        if result is None:
            print(f"Error: Country '{args.country}' not found. Use --list-countries to see options.")
            sys.exit(1)
        country_code, country_name = result
    
    print(f"\n{'='*60}")
    print(f"Country-wise {args.type.upper()} Data Scraper")
    print(f"{'='*60}")
    print(f"Country: {country_name}" + (f" (code: {country_code})" if country_code != "all" else ""))
    print(f"Years: {', '.join(years)}")
    print(f"Value Type: {'US $ Million' if args.value_type == 'usd' else '₹ Crore'}")
    print(f"{'='*60}\n")
    
    base_url = get_base_url(args.type)
    print(f"Connecting to {base_url}...")
    
    try:
        session, csrf_token = create_session(base_url)
        print("Session established.\n")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    total_saved = 0
    
    for year in years:
        fiscal_year = f"{year}-{int(year)+1}"
        print(f"Fetching {args.type} data for {country_name}, FY {fiscal_year}...")
        
        try:
            html = fetch_country_data(
                session=session,
                csrf_token=csrf_token,
                trade_type=args.type,
                year=year,
                country_code=country_code,
                value_type=args.value_type
            )
            
            if country_code == "all":
                data = parse_all_countries_table(html, args.type, year, args.value_type)
                count = data["metadata"]["data_info"]["country_count"]
            else:
                data = parse_country_wise_response(
                    html, args.type, year, country_code, country_name, args.value_type
                )
                count = data["metadata"]["data_info"]["record_count"]
            
            output_path = get_output_path(
                args.output, args.type, year, country_code, country_name, args.value_type
            )
            saved_path = save_json(data, output_path)
            
            print(f"  ✓ Saved {count} records to {saved_path}")
            total_saved += 1
            
            if len(years) > 1:
                time.sleep(args.delay)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"Completed! Saved {total_saved} file(s).")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
