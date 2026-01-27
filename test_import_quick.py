#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from tradestat_ingestor.tasks.batch_scraper import scrape_all_years

print('Testing import scraper for HSN=01012100...')
result = scrape_all_years('01012100', 'import')

print(f'\nSuccessful years: {len(result["successful"])}')
print(f'Failed years: {len(result["failed"])}')

if result['successful']:
    print('✅ IMPORT SCRAPER WORKING!')
    data = result['consolidated_data']
    print(f'Years scraped: {list(data["years"].keys())}')
    for year, year_data in data['years'].items():
        countries = len(year_data.get('countries', []))
        print(f'  {year}: {countries} countries')
else:
    print('❌ IMPORT SCRAPER FAILED')
    for year, error in result['errors'].items():
        print(f'  {year}: {error}')
