#!/usr/bin/env python3
"""MEIDB Commodity-wise Scraper CLI."""

import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib import create_session, bootstrap_session, fetch_commodity_data, parse_commodity_response, save_data

BASE_URL = os.getenv("BASE_URL", "https://tradestat.commerce.gov.in")
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0")
DATA_DIR = Path(__file__).parent / "data"

MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
          7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}


def main():
    parser = argparse.ArgumentParser(description="Scrape MEIDB commodity-wise monthly data")
    parser.add_argument("--hscode", required=True, help="HS code (2, 4, 6, or 8 digits)")
    parser.add_argument("--month", type=int, required=True, choices=range(1, 13), metavar="1-12")
    parser.add_argument("--year", type=int, required=True, choices=range(2018, 2026))
    parser.add_argument("--type", dest="trade_type", required=True, choices=["export", "import"])
    parser.add_argument("--value-type", default="usd", choices=["usd", "inr", "quantity"])
    parser.add_argument("--year-type", default="financial", choices=["financial", "calendar"])
    parser.add_argument("--output", help="Custom output directory")
    
    args = parser.parse_args()
    
    print(f"[*] Scraping MEIDB COMMODITY-WISE {args.trade_type.upper()} data...")
    print(f"    HS Code: {args.hscode} ({len(args.hscode)}-digit)")
    print(f"    Period: {MONTHS.get(args.month)} {args.year}")
    print(f"    Value Type: {args.value_type.upper()}")
    print(f"    Year Type: {args.year_type.title()}")
    print("-" * 60)
    
    session = create_session(USER_AGENT)
    state = bootstrap_session(session, BASE_URL, f"/meidb/commoditywise_{args.trade_type}")
    print("[+] Session bootstrapped")
    
    html = fetch_commodity_data(
        session, BASE_URL, args.hscode, args.month, args.year,
        args.trade_type, args.value_type, args.year_type, state
    )
    
    if not html:
        print("[!] Failed to fetch data")
        sys.exit(1)
    
    print(f"[+] Received {len(html)} bytes")
    
    data = parse_commodity_response(html, args.hscode, args.month, args.year, args.trade_type, args.value_type, args.year_type)
    if not data:
        print("[!] Failed to parse")
        sys.exit(1)
    
    print(f"[+] Parsed {len(data.get('commodities', []))} commodity records")
    
    output_path = save_data(data, args.output or str(DATA_DIR), args.trade_type, args.hscode, args.month, args.year, args.value_type)
    print(f"[+] Saved to: {output_path}")
    print("\n[*] Scrape completed!")


if __name__ == "__main__":
    main()
