import os
import requests
from dotenv import load_dotenv

load_dotenv()
FUNDER_ADDRESS = os.getenv('funder')

# Test with different parameters to get all positions
test_urls = [
    f'https://data-api.polymarket.com/positions?user={FUNDER_ADDRESS}',
    f'https://data-api.polymarket.com/positions?user={FUNDER_ADDRESS}&sizeThreshold=0',
    f'https://data-api.polymarket.com/positions?user={FUNDER_ADDRESS}&redeemable=true',
    f'https://data-api.polymarket.com/positions?user={FUNDER_ADDRESS}&limit=500',
    f'https://data-api.polymarket.com/positions?user={FUNDER_ADDRESS}&sizeThreshold=0&redeemable=true&limit=500',
]

for i, url in enumerate(test_urls, 1):
    print(f'\n--- Test #{i} ---')
    print(f'URL: {url}')
    
    try:
        response = requests.get(url)
        print(f'Status: {response.status_code}')
        
        if response.ok:
            data = response.json()
            print(f'Positions found: {len(data)}')
            
            if data:
                print('First position summary:')
                sample = data[0]
                print(f'  Title: {sample.get("title", "N/A")}')
                print(f'  Size: {sample.get("size", 0)}')
                print(f'  Redeemable: {sample.get("redeemable", False)}')
                print(f'  P&L: ${sample.get("cashPnl", 0)}')
                break  # Found positions, no need to continue
        else:
            print(f'Failed: {response.status_code}')
            
    except Exception as e:
        print(f'Error: {e}')

print('\nDone testing position endpoints.')
