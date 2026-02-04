#!/usr/bin/env python3
"""
EIDB Chapter-wise All Commodities Scraper CLI.
Fetches chapter-wise trade data for all commodities at various HS code levels.

Usage:
    python scrape_chapter_wise_all_commodities.py --year 2024 --type export
    python scrape_chapter_wise_all_commodities.py --year 2024 --type import --digit-level 4
"""

import os
import sys
import argparse
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib import (
    create_session,
    bootstrap_session,
    fetch_chapter_data,
    parse_chapter_wise_response,
    save_data,
)

# Configuration
BASE_URL = os.getenv("BASE_URL", "https://tradestat.commerce.gov.in")
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
DATA_DIR = Path(__file__).parent / "data"


def main():
    parser = argparse.ArgumentParser(
        description="Scrape EIDB chapter-wise all commodities data"
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        choices=range(2018, 2026),
        help="Financial year (e.g., 2024 for FY 2024-25)"
    )
    parser.add_argument(
        "--type",
        dest="trade_type",
        required=True,
        choices=["export", "import"],
        help="Trade type"
    )
    parser.add_argument(
        "--digit-level",
        type=int,
        default=2,
        choices=[2, 4, 6, 8],
        help="HS code digit level (default: 2)"
    )
    parser.add_argument(
        "--value-type",
        default="usd",
        choices=["usd", "inr"],
        help="Value type (default: usd)"
    )
    parser.add_argument(
        "--output",
        help="Custom output directory"
    )
    
    args = parser.parse_args()
    
    print(f"[*] Scraping EIDB CHAPTER-WISE ALL COMMODITIES {args.trade_type.upper()} data...")
    print(f"    Year: {args.year}")
    print(f"    Digit Level: {args.digit_level}")
    print(f"    Value Type: {args.value_type.upper()}")
    print("-" * 60)
    
    # Create session
    session = create_session(USER_AGENT)
    
    # Bootstrap
    path = f"/eidb/chapter_wise_{args.trade_type}"
    state = bootstrap_session(session, BASE_URL, path)
    print("[+] Session bootstrapped successfully")
    
    # Fetch data
    html = fetch_chapter_data(
        session=session,
        base_url=BASE_URL,
        year=str(args.year),
        digit_level=args.digit_level,
        trade_type=args.trade_type,
        value_type=args.value_type,
        state=state
    )
    
    if not html:
        print("[!] Failed to fetch data")
        sys.exit(1)
    
    print(f"[+] Received {len(html)} bytes")
    
    # Parse
    data = parse_chapter_wise_response(
        html=html,
        year=str(args.year),
        digit_level=args.digit_level,
        trade_type=args.trade_type,
        value_type=args.value_type
    )
    
    if not data:
        print("[!] Failed to parse response")
        sys.exit(1)
    
    print(f"[+] Parsed {len(data.get('commodities', []))} commodity records")
    
    # Save
    output_dir = args.output or str(DATA_DIR)
    output_path = save_data(
        data=data,
        base_dir=output_dir,
        trade_type=args.trade_type,
        year=str(args.year),
        digit_level=args.digit_level,
        value_type=args.value_type
    )
    
    print(f"[+] Saved to: {output_path}")
    print("\n[*] Scrape completed successfully!")


if __name__ == "__main__":
    main()
