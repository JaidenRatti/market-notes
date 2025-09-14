#!/usr/bin/env python3
"""
Polymarket API Client
Searches for active prediction markets using generated search queries
"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode
from config import config

class PolymarketClient:
    """Client for interacting with Polymarket's public API"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config.polymarket_base_url
        self.timeout = aiohttp.ClientTimeout(total=config.request_timeout)
    
    async def search_active_markets(self, search_query: str) -> Dict[str, Any]:
        """
        Search for active markets using a search query
        
        Args:
            search_query: The search term generated from sentiment analysis
            
        Returns:
            Complete JSON response from Polymarket API
        """
        # Build search parameters for active, open markets accepting orders
        params = {
            'q': search_query,
            'active': 'true',           # Only active markets (not resolved)
            'closed': 'false',          # Only markets open for trading
            'acceptingOrders': 'true',  # Only markets accepting new trades
            'events_status': 'active'   # Only events with active status
        }
        
        search_url = f"{self.base_url}/public-search"
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Add query parameters
                full_url = f"{search_url}?{urlencode(params)}"
                
                print(f"🔍 Searching Polymarket: {full_url}")
                
                async with session.get(full_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # public-search returns {"events": [...]} structure
                        if isinstance(data, dict) and 'events' in data:
                            events = data['events']
                            print(f"✅ Found {len(events)} markets")
                            return events
                        elif isinstance(data, list):
                            print(f"✅ Found {len(data)} markets")
                            return data
                        else:
                            print(f"✅ Found unknown number of markets")
                            return data
                    else:
                        print(f"❌ API Error: Status {response.status}")
                        error_text = await response.text()
                        return {
                            "error": f"API returned status {response.status}",
                            "details": error_text,
                            "search_query": search_query
                        }
                        
        except Exception as e:
            print(f"❌ Network Error: {e}")
            return {
                "error": f"Network error: {str(e)}",
                "search_query": search_query
            }
    
    async def search_markets_by_text(self, search_text: str) -> Dict[str, Any]:
        """
        Alternative search method using text search endpoint if available
        """
        try:
            # Try the public-search endpoint
            search_url = f"{self.base_url}/public-search"
            params = {
                'q': search_text,
                'active': 'true',
                'closed': 'false',
                'acceptingOrders': 'true',
                'events_status': 'active'
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                full_url = f"{search_url}?{urlencode(params)}"
                print(f"🔍 Text search: {full_url}")
                
                async with session.get(full_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        # Fallback to events search
                        return await self.search_active_markets(search_text)
                        
        except Exception as e:
            print(f"⚠️  Text search failed, falling back to events search: {e}")
            return await self.search_active_markets(search_text)


# Convenience function for synchronous usage
def search_polymarket_sync(search_query: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for Polymarket search
    
    Args:
        search_query: Search query from sentiment analysis
        
    Returns:
        JSON data from Polymarket API
    """
    client = PolymarketClient()
    return asyncio.run(client.search_active_markets(search_query))


# Test function
async def test_polymarket_search():
    """Test the Polymarket search functionality"""
    
    print("🧪 Testing Polymarket API Integration")
    print("=" * 50)
    
    # Test queries from our sentiment analysis
    test_queries = [
        "Election 2024",
        "Bitcoin price", 
        "Fed rates",
        "Tesla stock"
    ]
    
    client = PolymarketClient()
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 30)
        
        try:
            result = await client.search_active_markets(query)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                # Show summary of results
                if isinstance(result, list):
                    print(f"📊 Found {len(result)} markets")
                    if result:
                        print(f"📋 Sample market: {result[0].get('question', 'No question field')}")
                elif isinstance(result, dict) and 'data' in result:
                    markets = result['data']
                    print(f"📊 Found {len(markets)} markets")
                    if markets:
                        print(f"📋 Sample market: {markets[0].get('question', 'No question field')}")
                else:
                    print(f"📊 Response type: {type(result)}")
                    print(f"📋 Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            
        # Small delay between requests
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_polymarket_search())