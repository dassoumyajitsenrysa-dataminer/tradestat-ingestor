#!/usr/bin/env python3
"""
MEIDB Commodity-wise All Countries Scraper CLI

Scrapes monthly trade data for a specific HS code across all countries from MEIDB.

Usage:
    # Scrape export data for HS code 85 for November 2025
    python scrape_meidb_commodity_wise_all_countries.py --type export --hscode 85 --month 11 --year 2025

    # Scrape import data for 8-digit HS code with quantity
    python scrape_meidb_commodity_wise_all_countries.py --type import --hscode 85171300 --month 11 --year 2025 --value-type quantity

    # Use calendar year instead of financial year
    python scrape_meidb_commodity_wise_all_countries.py --type export --hscode 85 --month 11 --year 2025 --year-type calendar
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tradestat_ingestor.core.session import TradeStatSession
from tradestat_ingestor.scrapers.meidb.commodity_wise_all_countries.scraper import (
    scrape_meidb_commodity_wise_all_countries,
    MONTHS
)
from tradestat_ingestor.scrapers.meidb.commodity_wise_all_countries.parser import (
    parse_meidb_commodity_wise_all_countries_html
)
from tradestat_ingestor.scrapers.meidb.commodity_wise_all_countries.storage import (
    save_meidb_commodity_wise_all_countries_data
)

# Constants
BASE_URL = "https://tradestat.commerce.gov.in"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "src" / "data" / "raw"


def main():
    parser = argparse.ArgumentParser(
        description="Scrape MEIDB monthly commodity-wise trade data for all countries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export data for 2-digit HS code
  python scrape_meidb_commodity_wise_all_countries.py --type export --hscode 85 --month 11 --year 2025

  # Import data for 8-digit HS code with quantity values
  python scrape_meidb_commodity_wise_all_countries.py --type import --hscode 85171300 --month 11 --year 2025 --value-type quantity

  # Calendar year instead of financial year
  python scrape_meidb_commodity_wise_all_countries.py --type export --hscode 85 --month 6 --year 2025 --year-type calendar
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--hscode",
        required=True,
        help="HS code (2, 4, 6, or 8 digit)"
    )
    parser.add_argument(
        "--month",
        type=int,
        required=True,
        choices=range(1, 13),
        metavar="1-12",
        help="Month (1=January, 12=December)"
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        choices=range(2018, 2026),
        help="Year (2018-2025)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--type",
        choices=["export", "import"],
        default="export",
        help="Trade type (default: export)"
    )
    parser.add_argument(
        "--value-type",
        choices=["usd", "inr", "quantity"],
        default="usd",
        help="Value type: usd (US $ Million), inr (₹ Crore), quantity (default: usd)"
    )
    parser.add_argument(
        "--year-type",
        choices=["financial", "calendar"],
        default="financial",
        help="Year type: financial (Apr-Mar) or calendar (Jan-Dec) (default: financial)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    
    args = parser.parse_args()
    
    # Validate HS code length
    if len(args.hscode) not in [2, 4, 6, 8]:
        print(f"[!] Error: HS code must be 2, 4, 6, or 8 digits. Got: {len(args.hscode)} digits")
        sys.exit(1)
    
    # Validate quantity only for 8-digit
    if args.value_type == "quantity" and len(args.hscode) != 8:
        print("[!] Error: Quantity data is only available for 8-digit HS codes")
        sys.exit(1)
    
    month_name = MONTHS.get(args.month, str(args.month))
    digit_level = len(args.hscode)
    
    print(f"[*] Scraping MEIDB COMMODITY-WISE ALL COUNTRIES {args.type.upper()} data...")
    print(f"    HS Code: {args.hscode} ({digit_level}-digit)")
    print(f"    Period: {month_name} {args.year}")
    print(f"    Value Type: {args.value_type.upper()}")
    print(f"    Year Type: {args.year_type.capitalize()}")
    print("-" * 60)
    
    # Bootstrap session
    trade_session = TradeStatSession(BASE_URL, USER_AGENT)
    
    # Bootstrap path based on trade type
    if args.type == "export":
        bootstrap_path = "/meidb/commodity_wise_all_countries_export"
    else:
        bootstrap_path = "/meidb/commodity_wise_all_countries_import"
    
    state = trade_session.bootstrap(bootstrap_path)
    print("[+] Session bootstrapped successfully")
    
    # Scrape the data
    html = scrape_meidb_commodity_wise_all_countries(
        session=trade_session.session,
        base_url=BASE_URL,
        hscode=args.hscode,
        month=args.month,
        year=args.year,
        trade_type=args.type,
        value_type=args.value_type,
        year_type=args.year_type,
        state=state
    )
    
    if not html:
        print("[!] Failed to scrape data")
        sys.exit(1)
    
    print(f"[+] Received {len(html)} bytes")
    
    # Parse the data
    parsed_data = parse_meidb_commodity_wise_all_countries_html(
        html=html,
        hscode=args.hscode,
        month=args.month,
        year=args.year,
        trade_type=args.type,
        value_type=args.value_type,
        year_type=args.year_type
    )
    
    if not parsed_data:
        print("[!] Failed to parse data")
        sys.exit(1)
    
    countries_count = len(parsed_data.get("countries", []))
    print(f"[+] Parsed {countries_count} country records")
    
    # Save the data
    output_path = save_meidb_commodity_wise_all_countries_data(
        data=parsed_data,
        base_dir=args.output,
        hscode=args.hscode,
        month=args.month,
        year=args.year,
        trade_type=args.type,
        value_type=args.value_type,
        year_type=args.year_type
    )
    
    if output_path:
        print(f"[+] Saved to: {output_path}")
        print("\n[*] Scrape completed successfully!")
    else:
        print("[!] Failed to save data")
        sys.exit(1)


if __name__ == "__main__":
    main()
