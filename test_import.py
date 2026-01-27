#!/usr/bin/env python3
"""Quick test of import scraper"""
import sys
sys.path.insert(0, 'src')

from tradestat_ingestor.core.session import bootstrap
from tradestat_ingestor.core.scraper import scrape_import
from tradestat_ingestor.core.parser import parse_commodity_from_html
from requests import Session

# Test parameters
HSN = "01012100"
YEAR = "2024"
BASE_URL = "https://tradestat.commerce.gov.in"

print(f"Testing import scraper for HSN={HSN}, YEAR={YEAR}")
print("=" * 60)

try:
    # Create session
    session = Session()
    
    # Bootstrap to get CSRF token
    print(f"1. Bootstrapping session...")
    state = bootstrap(session)
    print(f"   ✓ CSRF token obtained")
    
    # Scrape import data
    print(f"2. Scraping import data...")
    html = scrape_import(session, BASE_URL, HSN, YEAR, state)
    print(f"   ✓ HTML received ({len(html)} bytes)")
    
    # Parse data
    print(f"3. Parsing data...")
    data = parse_commodity_from_html(html, HSN, YEAR, "import")
    
    if data:
        print(f"   ✓ Parsing successful!")
        print(f"   - Countries: {len(data.get('countries', []))}")
        print(f"   - First 3 countries: {[c['name'] for c in data.get('countries', [])[:3]]}")
    else:
        print(f"   ✗ No data parsed")
    
    print("\n" + "=" * 60)
    print("✅ IMPORT SCRAPER TEST PASSED!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
