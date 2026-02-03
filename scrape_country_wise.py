#!/usr/bin/env python3
"""
Country-wise Trade Data Scraper for TradeStat

Scrapes country-wise export/import data from tradestat.commerce.gov.in

Usage Examples:
    python scrape_country_wise.py --year 2024 --type export
    python scrape_country_wise.py --years 2024 2023 2022 --type import --value-type inr
    python scrape_country_wise.py --all-years --type export
    python scrape_country_wise.py --list-countries
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
from tradestat_ingestor.scrapers.country_wise import (
    fetch_country_data,
    get_base_url,
    get_country_name,
    parse_all_countries_table,
    parse_country_wise_response,
    COUNTRIES,
    AVAILABLE_YEARS,
)


def find_country_code(search: str) -> tuple[str, str] | None:
    """
    Find country code by name or code.
    Supports partial matching and common aliases (e.g., 'usa', 'uk', 'uae').
    
    Returns (code, name) or None if not found.
    """
    search_lower = search.lower().strip()
    
    # Common aliases mapping
    aliases = {
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
        "india": "187",  # Actually Indonesia, but common mistake
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
    
    # Check aliases first
    if search_lower in aliases:
        code = aliases[search_lower]
        return (code, COUNTRIES[code])
    
    # Direct code match
    if search in COUNTRIES:
        return (search, COUNTRIES[search])
    
    # Exact name match (case-insensitive)
    for code, name in COUNTRIES.items():
        if code == "all":
            continue
        if name.lower() == search_lower:
            return (code, name)
    
    # Normalize search (remove spaces for matching "U S A" with "usa")
    search_normalized = search_lower.replace(" ", "")
    for code, name in COUNTRIES.items():
        if code == "all":
            continue
        name_normalized = name.lower().replace(" ", "")
        if search_normalized == name_normalized:
            return (code, name)
    
    # Partial name match
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


def save_json(data: dict, filepath: str) -> str:
    """Save data as JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return str(path.absolute())


def main():
    parser = argparse.ArgumentParser(
        description="Scrape country-wise trade data from TradeStat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    year_group = parser.add_mutually_exclusive_group()
    year_group.add_argument("--year", type=str, help="Single year (e.g., 2024)")
    year_group.add_argument("--years", type=str, nargs="+", help="Multiple years")
    year_group.add_argument("--all-years", action="store_true", help="All years (2018-2024)")
    
    parser.add_argument("--type", choices=["export", "import"], default="export")
    parser.add_argument("--value-type", choices=["usd", "inr"], default="usd")
    parser.add_argument("--country", type=str, help="Country name or code (e.g., 'usa', 'U S A', '423')")
    parser.add_argument("--output", type=str, default="./src/data/raw/country_wise")
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
            print(f"Error: Country '{args.country}' not found. Use --list-countries to see available options.")
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
        # Create session and get CSRF token
        ts_session = TradeStatSession(
            base_url="https://tradestat.commerce.gov.in",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        # Bootstrap to get CSRF token - use the path part of the URL
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
            
            # Use appropriate parser based on country filter
            if country_code == "all":
                data = parse_all_countries_table(html, args.type, year, args.value_type)
                filename = f"all_countries_{fiscal_year}_{args.value_type}.json"
                output_path = os.path.join(args.output, args.type, filename)
                count = data["metadata"]["data_info"]["country_count"]
            else:
                data = parse_country_wise_response(
                    html, args.type, year, country_code, country_name, args.value_type
                )
                # Sanitize country name for filename
                safe_name = country_name.replace(" ", "_").replace(".", "").replace("'", "")
                filename = f"{safe_name}_{fiscal_year}_{args.value_type}.json"
                output_path = os.path.join(args.output, args.type, "by_country", filename)
                count = data["metadata"]["data_info"]["record_count"]
            
            saved_path = save_json(data, output_path)
            print(f"  ✓ Saved {count} records to {saved_path}")
            
            if len(years) > 1:
                time.sleep(args.delay)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nDone!")


if __name__ == "__main__":
    main()
