#!/usr/bin/env python3
"""
Test Polymarket API and display full JSON responses
"""
import asyncio
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from polymarket_client import PolymarketClient

async def test_full_response():
    """Test and display complete JSON response from Polymarket API"""
    
    print("🔍 Testing Polymarket API - Full JSON Response")
    print("=" * 60)
    
    # Test with a specific query
    test_query = "Bitcoin"
    
    client = PolymarketClient()
    
    print(f"📝 Search Query: '{test_query}'")
    print("-" * 40)
    
    try:
        result = await client.search_active_markets(test_query)
        
        if "error" in result:
            print(f"❌ Error: {result}")
            return
            
        # Display the full JSON response
        print("🔍 FULL JSON RESPONSE:")
        print("=" * 40)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Also analyze the structure
        print("\n" + "=" * 40)
        print("📊 RESPONSE ANALYSIS:")
        
        if isinstance(result, list):
            print(f"✅ Response is a LIST with {len(result)} items")
            if result:
                first_item = result[0]
                print(f"📋 First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                if isinstance(first_item, dict):
                    # Look for common fields
                    for field in ['question', 'title', 'description', 'id', 'slug']:
                        if field in first_item:
                            print(f"   - {field}: {first_item[field]}")
                            
        elif isinstance(result, dict):
            print(f"✅ Response is a DICT with keys: {list(result.keys())}")
            if 'data' in result:
                data = result['data']
                print(f"📋 Data section has {len(data) if isinstance(data, list) else 'unknown'} items")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_response())