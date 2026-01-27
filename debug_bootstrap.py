import requests
from bs4 import BeautifulSoup

url = 'https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_export'
resp = requests.get(url, timeout=30)
soup = BeautifulSoup(resp.text, 'lxml')

# Search for the fields
viewstate = soup.find('input', {'name': '__VIEWSTATE'})
eventval = soup.find('input', {'name': '__EVENTVALIDATION'})

print(f'__VIEWSTATE found: {viewstate is not None}')
print(f'__EVENTVALIDATION found: {eventval is not None}')

# Check for any input fields
inputs = soup.find_all('input')
print(f'\nTotal input fields: {len(inputs)}')
print('\nAll input field names:')
for inp in inputs:
    print(f'  - {inp.get("name", "(no name)")}')
