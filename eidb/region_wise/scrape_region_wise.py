#!/usr/bin/env python3
"""EIDB Region-wise Scraper CLI."""

import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib import create_session, bootstrap_session, fetch_region_data, parse_region_wise_response, save_data

BASE_URL = os.getenv("BASE_URL", "https://tradestat.commerce.gov.in")
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0")
DATA_DIR = Path(__file__).parent / "data"


def main():
    parser = argparse.ArgumentParser(description="Scrape EIDB region-wise data")
    parser.add_argument("--hscode", required=True, help="HS code")
    parser.add_argument("--year", type=int, required=True, choices=range(2018, 2026))
    parser.add_argument("--type", dest="trade_type", required=True, choices=["export", "import"])
    parser.add_argument("--value-type", default="usd", choices=["usd", "inr", "quantity"])
    parser.add_argument("--output", help="Custom output directory")
    
    args = parser.parse_args()
    
    print(f"[*] Scraping EIDB REGION-WISE {args.trade_type.upper()} data...")
    print(f"    HS Code: {args.hscode} ({len(args.hscode)}-digit)")
    print(f"    Year: {args.year}")
    print("-" * 60)
    
    session = create_session(USER_AGENT)
    state = bootstrap_session(session, BASE_URL, f"/eidb/region_wise_{args.trade_type}")
    print("[+] Session bootstrapped")
    
    html = fetch_region_data(session, BASE_URL, args.hscode, str(args.year), args.trade_type, args.value_type, state)
    if not html:
        print("[!] Failed to fetch data")
        sys.exit(1)
    
    print(f"[+] Received {len(html)} bytes")
    
    data = parse_region_wise_response(html, args.hscode, str(args.year), args.trade_type, args.value_type)
    if not data:
        print("[!] Failed to parse")
        sys.exit(1)
    
    print(f"[+] Parsed {len(data.get('countries', []))} country records")
    
    output_path = save_data(data, args.output or str(DATA_DIR), args.trade_type, args.hscode, str(args.year), args.value_type)
    print(f"[+] Saved to: {output_path}")
    print("\n[*] Scrape completed!")


if __name__ == "__main__":
    main()
