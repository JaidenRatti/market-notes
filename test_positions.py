#!/usr/bin/env python3

import os
import requests
import json
from dotenv import load_dotenv
from py_clob_client.client import ClobClient

load_dotenv()

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = os.getenv("magickey")
FUNDER_ADDRESS = os.getenv("funder")

def setup_client():
    """Setup authenticated Magic wallet client"""
    client = ClobClient(
        HOST,
        key=PRIVATE_KEY,
        chain_id=CHAIN_ID,
        signature_type=1,  # Magic wallet
        funder=FUNDER_ADDRESS
    )
    client.set_api_creds(client.create_or_derive_api_creds())
    return client

def test_direct_positions():
    """Test getting positions directly from client"""
    print("🔍 Testing direct positions from client...")
    try:
        client = setup_client()
        positions = client.get_positions()
        
        print(f"✅ Got {len(positions)} positions")
        if positions:
            print("📄 Sample position:")
            sample = positions[0]
            print(f"   Title: {sample.get('title', 'N/A')}")
            print(f"   Position: {sample.get('outcome', 'N/A')}")
            print(f"   Size: {sample.get('size', 0)}")
            print(f"   P&L: ${sample.get('cashPnl', 0):.4f}")
            print(f"   Current Value: ${sample.get('currentValue', 0):.2f}")
        
        return positions
        
    except Exception as e:
        print(f"❌ Direct positions failed: {e}")
        return None

def test_api_endpoint():
    """Test the Flask API endpoint"""
    print("\n🔍 Testing Flask API endpoint...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/positions")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                positions = data.get('positions', [])
                print(f"✅ API returned {len(positions)} positions")
                if positions:
                    print("📄 Sample formatted position:")
                    sample = positions[0]
                    print(f"   Title: {sample.get('title', 'N/A')}")
                    print(f"   Position: {sample.get('position', 'N/A')}")
                    print(f"   Shares: {sample.get('shares', 0)}")
                    print(f"   P&L: ${sample.get('pnl', 0):.2f}")
                    print(f"   Status: {sample.get('status', 'N/A')}")
                return positions
            else:
                print(f"❌ API error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server. Is it running?")
        print("   Run: python3 trading_backend.py")
    except Exception as e:
        print(f"❌ API test failed: {e}")
        
    return None

if __name__ == "__main__":
    print("🧪 Testing Positions Integration")
    print("=" * 50)
    
    # Test 1: Direct client call
    direct_positions = test_direct_positions()
    
    # Test 2: API endpoint
    api_positions = test_api_endpoint()
    
    print("\n📊 Summary:")
    print(f"   Direct positions: {'✅' if direct_positions else '❌'}")
    print(f"   API endpoint: {'✅' if api_positions else '❌'}")
    
    if direct_positions and api_positions:
        print(f"   Count match: {'✅' if len(direct_positions) == len(api_positions) else '❌'}")
    
    print("\n💡 Next steps:")
    print("   1. Ensure trading_backend.py is running")
    print("   2. Open Chrome extension and check profile page")
    print("   3. Look for 'Polymarket Positions (Live)' section")
