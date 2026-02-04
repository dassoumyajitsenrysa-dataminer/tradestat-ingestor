#!/usr/bin/env python3
"""EIDB Region-wise All Commodities Scraper CLI."""

import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib import create_session, bootstrap_session, fetch_region_commodities_data, parse_region_commodities_response, save_data

BASE_URL = os.getenv("BASE_URL", "https://tradestat.commerce.gov.in")
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0")
DATA_DIR = Path(__file__).parent / "data"

COUNTRIES = {"423": "U.S.A.", "306": "China", "412": "Japan", "314": "Germany", "526": "U.A.E."}


def main():
    parser = argparse.ArgumentParser(description="Scrape EIDB region-wise all commodities data")
    parser.add_argument("--country", required=True, help="Country code (e.g., 423)")
    parser.add_argument("--year", type=int, required=True, choices=range(2018, 2026))
    parser.add_argument("--digit-level", type=int, default=2, choices=[2, 4, 6, 8])
    parser.add_argument("--type", dest="trade_type", required=True, choices=["export", "import"])
    parser.add_argument("--value-type", default="usd", choices=["usd", "inr", "quantity"])
    parser.add_argument("--output", help="Custom output directory")
    
    args = parser.parse_args()
    country_name = COUNTRIES.get(args.country, f"Country_{args.country}")
    
    print(f"[*] Scraping EIDB REGION-WISE ALL COMMODITIES {args.trade_type.upper()}...")
    print(f"    Country: {country_name} ({args.country})")
    print(f"    Year: {args.year}, Level: {args.digit_level}-digit")
    print("-" * 60)
    
    session = create_session(USER_AGENT)
    state = bootstrap_session(session, BASE_URL, f"/eidb/region_wise_all_commodities_{args.trade_type}")
    print("[+] Session bootstrapped")
    
    html = fetch_region_commodities_data(session, BASE_URL, args.country, str(args.year), args.digit_level, args.trade_type, args.value_type, state)
    if not html:
        print("[!] Failed to fetch")
        sys.exit(1)
    
    print(f"[+] Received {len(html)} bytes")
    
    data = parse_region_commodities_response(html, args.country, country_name, str(args.year), args.digit_level, args.trade_type, args.value_type)
    if not data:
        print("[!] Failed to parse")
        sys.exit(1)
    
    print(f"[+] Parsed {len(data.get('commodities', []))} commodity records")
    
    output_path = save_data(data, args.output or str(DATA_DIR), args.trade_type, args.country, country_name, str(args.year), args.digit_level, args.value_type)
    print(f"[+] Saved to: {output_path}")
    print("\n[*] Scrape completed!")


if __name__ == "__main__":
    main()
