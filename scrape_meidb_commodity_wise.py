#!/usr/bin/env python3
"""
CLI to scrape MEIDB (monthly) commodity-wise data from tradestat.commerce.gov.in

Usage:
    # Specific HS code (any digit level)
    python scrape_meidb_commodity_wise.py --hscode 27 --month 11 --year 2025 --type export
    python scrape_meidb_commodity_wise.py --hscode 2701 --month 11 --year 2025 --type import
    python scrape_meidb_commodity_wise.py --hscode 27011100 --month 11 --year 2025 --type export --value-type quantity

    # All commodities at a digit level
    python scrape_meidb_commodity_wise.py --all --digit-level 2 --month 11 --year 2025 --type export
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, 'src')

from tradestat_ingestor.core.session import TradeStatSession
from tradestat_ingestor.scrapers.meidb.commodity_wise import (
    scrape_meidb_commodity_wise,
    scrape_meidb_commodity_wise_all,
    parse_meidb_commodity_wise_html,
    save_meidb_commodity_wise_data,
    save_meidb_all_commodities_data,
    COMMODITY_WISE_EXPORT_PATH,
    COMMODITY_WISE_IMPORT_PATH,
    MONTHS
)
from tradestat_ingestor.config.settings import settings


# Available years for scraping (based on data availability: Jan 2018 to Nov 2025)
AVAILABLE_YEARS = list(range(2018, 2026))


def main():
    parser = argparse.ArgumentParser(
        description="Scrape MEIDB (monthly) commodity-wise trade data from tradestat.commerce.gov.in"
    )

    # Mode: specific HS code or all commodities at digit level
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--hscode",
        help="Specific HS code (2, 4, 6, or 8 digit)"
    )
    mode_group.add_argument(
        "--all",
        action="store_true",
        help="Scrape all commodities at a specified digit level"
    )

    parser.add_argument(
        "--digit-level",
        type=int,
        choices=[2, 4, 6, 8],
        help="Digit level (required when using --all)"
    )

    # Month and Year (required for MEIDB)
    parser.add_argument(
        "--month",
        type=int,
        choices=range(1, 13),
        required=True,
        metavar="1-12",
        help="Month (1=January, 12=December)"
    )

    parser.add_argument(
        "--year",
        type=int,
        choices=AVAILABLE_YEARS,
        required=True,
        help="Year (2018-2025)"
    )

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
        help="Custom output directory (optional)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.all and not args.digit_level:
        parser.error("--digit-level is required when using --all")

    if args.value_type == "quantity":
        if args.hscode and len(args.hscode) != 8:
            parser.error("Quantity data is only available at 8-digit level")
        if args.all and args.digit_level != 8:
            parser.error("Quantity data is only available at 8-digit level")

    # Determine the bootstrap path based on trade type
    bootstrap_path = COMMODITY_WISE_EXPORT_PATH if args.type == "export" else COMMODITY_WISE_IMPORT_PATH

    month_name = MONTHS.get(args.month, str(args.month))

    print(f"[*] Scraping MEIDB COMMODITY-WISE {args.type.upper()} data...")
    if args.hscode:
        print(f"    HS Code: {args.hscode} ({len(args.hscode)}-digit)")
    else:
        print(f"    Mode: All commodities at {args.digit_level}-digit level")
    print(f"    Period: {month_name} {args.year}")
    print(f"    Value Type: {args.value_type.upper()}")
    print(f"    Year Type: {args.year_type.title()}")
    print("-" * 60)

    try:
        # Initialize session
        session_obj = TradeStatSession(
            base_url=settings.base_url,
            user_agent=settings.user_agent,
        )
        state = session_obj.bootstrap(bootstrap_path)

        if not state:
            print("[!] Failed to bootstrap session")
            return 1

        print(f"[+] Session bootstrapped successfully")

        # Scrape data
        if args.hscode:
            # Scrape specific HS code
            response = scrape_meidb_commodity_wise(
                session=session_obj.session,
                base_url=settings.base_url,
                hscode=args.hscode,
                month=args.month,
                year=args.year,
                trade_type=args.type,
                value_type=args.value_type,
                year_type=args.year_type,
                state=state,
            )
        else:
            # Scrape all commodities at digit level
            response = scrape_meidb_commodity_wise_all(
                session=session_obj.session,
                base_url=settings.base_url,
                digit_level=args.digit_level,
                month=args.month,
                year=args.year,
                trade_type=args.type,
                value_type=args.value_type,
                year_type=args.year_type,
                state=state,
            )

        if response:
            print(f"[+] Received {len(response)} bytes")

            # Parse HTML
            hscode_for_parse = args.hscode if args.hscode else f"all_{args.digit_level}digit"
            parsed_data = parse_meidb_commodity_wise_html(
                response,
                hscode_for_parse,
                args.month,
                args.year,
                trade_type=args.type,
                value_type=args.value_type,
                year_type=args.year_type
            )

            if parsed_data:
                commodities_count = len(parsed_data.get('commodities', []))
                print(f"[+] Parsed {commodities_count} commodity records")

                # Save to file
                if args.hscode:
                    filepath = save_meidb_commodity_wise_data(
                        parsed_data,
                        args.hscode,
                        args.month,
                        args.year,
                        args.type,
                        args.value_type
                    )
                else:
                    filepath = save_meidb_all_commodities_data(
                        parsed_data,
                        args.digit_level,
                        args.month,
                        args.year,
                        args.type,
                        args.value_type
                    )

                print(f"[+] Saved to: {filepath}")

                # Show India's total if available
                india_total = parsed_data.get('india_total')
                if india_total:
                    value = india_total.get('value')
                    growth = india_total.get('growth_pct')
                    if value is not None:
                        print(f"[i] India's Total ({month_name} {args.year}): {value:,.2f}")
                    if growth is not None:
                        print(f"[i] Growth: {growth:+.2f}%")

                print("\n[*] Scrape completed successfully!")
                return 0
            else:
                print("[!] Parsing failed")
                return 1
        else:
            print("[!] Scrape failed - no response received")
            return 1

    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
