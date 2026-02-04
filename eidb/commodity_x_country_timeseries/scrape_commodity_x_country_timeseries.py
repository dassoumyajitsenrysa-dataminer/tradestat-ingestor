#!/usr/bin/env python3
"""
EIDB Commodity x Country Timeseries Scraper CLI.
Fetches historical trade data for a specific HS code and country combination.
"""

import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib import (
    create_session,
    bootstrap_session,
    fetch_timeseries_data,
    parse_timeseries_response,
    save_data,
)

BASE_URL = os.getenv("BASE_URL", "https://tradestat.commerce.gov.in")
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
DATA_DIR = Path(__file__).parent / "data"

# Common country codes
COUNTRIES = {
    "423": "U.S.A.",
    "306": "China",
    "412": "Japan",
    "314": "Germany",
    "526": "U.A.E.",
    "523": "Saudi Arabia",
}


def main():
    parser = argparse.ArgumentParser(description="Scrape EIDB commodity x country timeseries data")
    parser.add_argument("--hscode", required=True, help="HS code (2, 4, 6, or 8 digits)")
    parser.add_argument("--country", required=True, help="Country code (e.g., 423 for USA)")
    parser.add_argument("--from-year", type=int, required=True, help="Start year")
    parser.add_argument("--to-year", type=int, required=True, help="End year")
    parser.add_argument("--type", dest="trade_type", required=True, choices=["export", "import"])
    parser.add_argument("--value-type", default="usd", choices=["usd", "inr", "quantity"])
    parser.add_argument("--output", help="Custom output directory")
    
    args = parser.parse_args()
    
    country_name = COUNTRIES.get(args.country, f"Country_{args.country}")
    
    print(f"[*] Scraping EIDB COMMODITY x COUNTRY TIMESERIES {args.trade_type.upper()} data...")
    print(f"    HS Code: {args.hscode}")
    print(f"    Country: {country_name} ({args.country})")
    print(f"    Period: {args.from_year} - {args.to_year}")
    print("-" * 60)
    
    session = create_session(USER_AGENT)
    path = f"/eidb/commodity_country_timeseries_{args.trade_type}"
    state = bootstrap_session(session, BASE_URL, path)
    print("[+] Session bootstrapped")
    
    html = fetch_timeseries_data(
        session, BASE_URL, args.hscode, args.country,
        str(args.from_year), str(args.to_year),
        args.trade_type, args.value_type, state
    )
    
    if not html:
        print("[!] Failed to fetch data")
        sys.exit(1)
    
    print(f"[+] Received {len(html)} bytes")
    
    data = parse_timeseries_response(
        html, args.hscode, args.country, country_name,
        str(args.from_year), str(args.to_year),
        args.trade_type, args.value_type
    )
    
    if not data:
        print("[!] Failed to parse response")
        sys.exit(1)
    
    print(f"[+] Parsed {len(data.get('timeseries', []))} year records")
    
    output_dir = args.output or str(DATA_DIR)
    output_path = save_data(
        data, output_dir, args.trade_type, args.hscode,
        args.country, country_name, str(args.from_year),
        str(args.to_year), args.value_type
    )
    
    print(f"[+] Saved to: {output_path}")
    print("\n[*] Scrape completed successfully!")


if __name__ == "__main__":
    main()
