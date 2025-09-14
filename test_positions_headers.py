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

positions_url = f'https://clob.polymarket.com/positions?user={FUNDER_ADDRESS}'

# Try different header combinations
header_combinations = [
    # Standard Bearer token
    {
        'Authorization': f'Bearer {creds.api_key}',
        'Content-Type': 'application/json'
    },
    # API key in different format
    {
        'X-API-KEY': creds.api_key,
        'Content-Type': 'application/json'
    },
    # All credentials in headers
    {
        'Authorization': f'Bearer {creds.api_key}',
        'X-API-SECRET': creds.api_secret,
        'X-API-PASSPHRASE': creds.api_passphrase,
        'Content-Type': 'application/json'
    },
    # Polymarket specific format (if any)
    {
        'POLY-API-KEY': creds.api_key,
        'POLY-API-SECRET': creds.api_secret,
        'POLY-API-PASSPHRASE': creds.api_passphrase,
        'Content-Type': 'application/json'
    }
]

for i, headers in enumerate(header_combinations, 1):
    print(f'\nTrying header combination #{i}:')
    print(f'Headers: {list(headers.keys())}')
    
    try:
        response = requests.get(positions_url, headers=headers)
        print(f'Status code: {response.status_code}')
        
        if response.ok:
            data = response.json()
            print(f'✅ SUCCESS! Got {len(data)} positions')
            if data:
                sample = data[0]
                print(f'Sample: {sample.get("title", "N/A")} - {sample.get("outcome", "N/A")}')
            break
        elif response.status_code != 404:
            print(f'Response preview: {response.text[:200]}')
        else:
            print('404 Not Found')
            
    except Exception as e:
        print(f'Error: {e}')
