#!/usr/bin/env python3
"""
MEIDB Principal Commodity-wise All HSCode Scraper CLI

Scrapes all HSCode breakdowns for a given principal commodity from MEIDB.

Usage:
    # List all available principal commodity codes
    python scrape_meidb_principal_commodity.py --list-commodities

    # Scrape export data for TEA (A1) for November 2025
    python scrape_meidb_principal_commodity.py --type export --commodity A1 --month 11 --year 2025

    # Scrape import data for IRON AND STEEL (L3) in INR
    python scrape_meidb_principal_commodity.py --type import --commodity L3 --month 11 --year 2025 --value-type inr

    # Use calendar year instead of financial year
    python scrape_meidb_principal_commodity.py --type export --commodity A1 --month 11 --year 2025 --year-type calendar
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tradestat_ingestor.core.session import TradeStatSession
from tradestat_ingestor.scrapers.meidb.principal_commodity_wise_all_hscode.scraper import (
    scrape_meidb_principal_commodity_wise_all_hscode,
    PRINCIPAL_COMMODITIES,
    get_commodity_name,
    MONTHS
)
from tradestat_ingestor.scrapers.meidb.principal_commodity_wise_all_hscode.parser import (
    parse_meidb_principal_commodity_wise_all_hscode_html
)
from tradestat_ingestor.scrapers.meidb.principal_commodity_wise_all_hscode.storage import (
    save_meidb_principal_commodity_wise_all_hscode_data
)

# Constants
BASE_URL = "https://tradestat.commerce.gov.in"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "src" / "data" / "raw"


def print_commodity_list():
    """Print all available principal commodity codes."""
    print("\n" + "=" * 70)
    print("AVAILABLE PRINCIPAL COMMODITY CODES")
    print("=" * 70)
    for code, name in sorted(PRINCIPAL_COMMODITIES.items()):
        print(f"  {code:4} : {name}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape MEIDB principal commodity-wise all HSCode data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all commodity codes
  python scrape_meidb_principal_commodity.py --list-commodities

  # Export data for TEA
  python scrape_meidb_principal_commodity.py --type export --commodity A1 --month 11 --year 2025

  # Import data for IRON AND STEEL in INR
  python scrape_meidb_principal_commodity.py --type import --commodity L3 --month 11 --year 2025 --value-type inr

  # Calendar year instead of financial year
  python scrape_meidb_principal_commodity.py --type export --commodity A1 --month 6 --year 2025 --year-type calendar
        """
    )
    
    # List commodities flag
    parser.add_argument(
        "--list-commodities",
        action="store_true",
        help="List all available principal commodity codes"
    )
    
    # Required arguments (not required if --list-commodities is used)
    parser.add_argument(
        "--commodity",
        help="Principal commodity code (e.g., A1=TEA, L3=IRON AND STEEL)"
    )
    parser.add_argument(
        "--month",
        type=int,
        choices=range(1, 13),
        metavar="1-12",
        help="Month (1=January, 12=December)"
    )
    parser.add_argument(
        "--year",
        type=int,
        choices=range(2018, 2027),
        help="Year (2018-2026)"
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
    
    # Handle --list-commodities
    if args.list_commodities:
        print_commodity_list()
        sys.exit(0)
    
    # Validate required arguments when not listing commodities
    if not all([args.commodity, args.month, args.year]):
        print("[!] Error: --commodity, --month, and --year are required")
        print("    Use --list-commodities to see available codes")
        parser.print_help()
        sys.exit(1)
    
    # Validate commodity code
    commodity_code = args.commodity.upper()
    if commodity_code not in PRINCIPAL_COMMODITIES:
        print(f"[!] Error: Unknown commodity code: {commodity_code}")
        print("    Use --list-commodities to see available codes")
        sys.exit(1)
    
    commodity_name = get_commodity_name(commodity_code)
    month_name = MONTHS.get(args.month, str(args.month))
    
    print(f"\n[*] Scraping MEIDB PRINCIPAL COMMODITY-WISE ALL HSCODE {args.type.upper()} data...")
    print(f"    Principal Commodity: {commodity_name} ({commodity_code})")
    print(f"    Period: {month_name} {args.year}")
    print(f"    Value Type: {args.value_type.upper()}")
    print(f"    Year Type: {args.year_type.capitalize()}")
    print("-" * 60)
    
    # Bootstrap session
    trade_session = TradeStatSession(BASE_URL, USER_AGENT)
    
    # Bootstrap path based on trade type
    if args.type == "export":
        bootstrap_path = "/meidb/principal_commodity_wise_all_HSCode_export"
    else:
        bootstrap_path = "/meidb/principal_commodity_wise_all_HSCode_import"
    
    state = trade_session.bootstrap(bootstrap_path)
    print("[+] Session bootstrapped successfully")
    
    # Scrape the data
    html = scrape_meidb_principal_commodity_wise_all_hscode(
        session=trade_session.session,
        base_url=BASE_URL,
        commodity_code=commodity_code,
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
    parsed_data = parse_meidb_principal_commodity_wise_all_hscode_html(
        html=html,
        commodity_code=commodity_code,
        commodity_name=commodity_name,
        month=args.month,
        year=args.year,
        trade_type=args.type,
        value_type=args.value_type,
        year_type=args.year_type
    )
    
    if not parsed_data:
        print("[!] Failed to parse data")
        sys.exit(1)
    
    hscode_count = len(parsed_data.get("commodities", []))
    print(f"[+] Parsed {hscode_count} HSCode records")
    
    # Display total if available
    total = parsed_data.get("total")
    if total:
        print(f"\n[*] Total {args.type.title()} of {commodity_name}:")
        if total.get("month_curr_year") is not None:
            print(f"    {month_name} {args.year}: {total['month_curr_year']:.2f} {args.value_type.upper()}")
        if total.get("cumulative_curr_year") is not None:
            fy_label = f"Apr-{month_name[:3]}" if args.year_type == "financial" else f"Jan-{month_name[:3]}"
            print(f"    {fy_label} {args.year}: {total['cumulative_curr_year']:.2f} {args.value_type.upper()}")
        if total.get("cumulative_yoy_growth_pct") is not None:
            print(f"    YoY Growth: {total['cumulative_yoy_growth_pct']:.2f}%")
    
    # Save the data
    output_path = save_meidb_principal_commodity_wise_all_hscode_data(
        data=parsed_data,
        base_dir=args.output,
        trade_type=args.type,
        commodity_code=commodity_code,
        month=args.month,
        year=args.year,
        value_type=args.value_type
    )
    
    if output_path:
        print(f"\n[+] Saved to: {output_path}")
        print("\n[*] Scrape completed successfully!")
    else:
        print("[!] Failed to save data")
        sys.exit(1)


if __name__ == "__main__":
    main()
