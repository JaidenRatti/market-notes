import os
import requests
from dotenv import load_dotenv

load_dotenv()
FUNDER_ADDRESS = os.getenv('funder')

# Test the correct data-api endpoint
positions_url = f'https://data-api.polymarket.com/positions?user={FUNDER_ADDRESS}'
print(f'Calling: {positions_url}')

try:
    # Try without authentication first (data-api might be public)
    response = requests.get(positions_url)
    print(f'Status code: {response.status_code}')
    
    if response.ok:
        data = response.json()
        print(f'✅ SUCCESS! Got {len(data)} positions')
        if data:
            print('\nFirst position:')
            sample = data[0]
            for key, value in sample.items():
                print(f'  {key}: {value}')
            
            print(f'\nPosition summary:')
            print(f'  Title: {sample.get("title", "N/A")}')
            print(f'  Outcome: {sample.get("outcome", "N/A")}')
            print(f'  Size: {sample.get("size", 0)}')
            print(f'  Current Value: ${sample.get("currentValue", 0)}')
            print(f'  Cash P&L: ${sample.get("cashPnl", 0)}')
            print(f'  Redeemable: {sample.get("redeemable", False)}')
        else:
            print('No positions found')
    else:
        print(f'❌ Failed: {response.status_code}')
        print(f'Response: {response.text}')
        
except Exception as e:
    print(f'Error: {e}')
