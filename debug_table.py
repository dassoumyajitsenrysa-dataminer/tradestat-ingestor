#!/usr/bin/env python3
"""Debug script to check table structure"""

import sys
sys.path.insert(0, 'src')

from tradestat_ingestor.core.session import TradeStatSession
from bs4 import BeautifulSoup

ts = TradeStatSession(
    base_url='https://tradestat.commerce.gov.in',
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
)
form_data = ts.bootstrap('/eidb/region_wise_export')
token = form_data['_token']

payload = {
    '_token': token,
    'eidbYearRwe': '2024',
    'eidbrwexp_regid': '4',
    'eidbReportRwe': '2',
}
resp = ts.session.post('https://tradestat.commerce.gov.in/eidb/region_wise_export', data=payload)
soup = BeautifulSoup(resp.text, 'lxml')
tables = soup.find_all('table')
print(f'Found {len(tables)} tables')

for i, t in enumerate(tables):
    rows = t.find_all('tr')
    print(f'\nTable {i}: {len(rows)} rows, class={t.get("class")}')
    for j, row in enumerate(rows[:3]):  # First 3 rows
        cells = row.find_all(['td', 'th'])
        cell_texts = [c.get_text(strip=True)[:30] for c in cells]
        print(f'  Row {j}: {cell_texts}')
