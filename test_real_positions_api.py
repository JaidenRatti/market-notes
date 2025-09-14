import os
import requests
from dotenv import load_dotenv
from py_clob_client.client import ClobClient

load_dotenv()
PRIVATE_KEY = os.getenv('magickey')
FUNDER_ADDRESS = os.getenv('funder')

# Setup client correctly
client = ClobClient(
    'https://clob.polymarket.com',
    key=PRIVATE_KEY,
    chain_id=137,
    signature_type=1,
    funder=FUNDER_ADDRESS
)
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)

print(f'Using API key: {creds.api_key[:20]}...')
print(f'Funder address: {FUNDER_ADDRESS}')

# Test the corrected positions API call
headers = {
    'Authorization': f'Bearer {creds.api_key}',
    'Content-Type': 'application/json'
}

positions_url = f'https://clob.polymarket.com/positions?user={FUNDER_ADDRESS}'
print(f'Calling: {positions_url}')

try:
    response = requests.get(positions_url, headers=headers)
    print(f'Status code: {response.status_code}')
    
    if response.ok:
        data = response.json()
        print(f'✅ SUCCESS! Got {len(data)} positions')
        if data:
            print('First position keys:', list(data[0].keys()))
            sample = data[0]
            print(f'Sample position:')
            print(f'  Title: {sample.get("title", "N/A")}')
            print(f'  Outcome: {sample.get("outcome", "N/A")}')
            print(f'  Size: {sample.get("size", 0)}')
            print(f'  Current Value: ${sample.get("currentValue", 0)}')
            print(f'  Cash P&L: ${sample.get("cashPnl", 0)}')
        else:
            print('No positions found')
    else:
        print(f'❌ Failed: {response.status_code}')
        print(f'Response: {response.text}')
        
except Exception as e:
    print(f'Error: {e}')
