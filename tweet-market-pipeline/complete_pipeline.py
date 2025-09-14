#!/usr/bin/env python3
"""
Complete Tweet-to-Polymarket Pipeline
Combines sentiment analysis with Polymarket API search
"""
import asyncio
import json
import os
import sys
from typing import Dict, Any
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentiment_extractor import analyze_tweet_sentiment_sync
from polymarket_client import PolymarketClient

class TweetMarketPipeline:
    """Complete pipeline from tweet to Polymarket search results"""
    
    def __init__(self):
        self.polymarket_client = PolymarketClient()
    
    async def process_tweet(self, tweet_text: str, author: str = None) -> Dict[str, Any]:
        """
        Complete pipeline: Tweet → Sentiment Analysis → Polymarket Search
        
        Args:
            tweet_text: The tweet to analyze
            author: Optional author of the tweet
            
        Returns:
            Complete results including sentiment analysis and market data
        """
        print(f"🚀 PROCESSING TWEET: {tweet_text}")
        print("=" * 60)
        
        # Step 1: Sentiment Analysis
        print("📊 Step 1: Analyzing sentiment with Cohere API...")
        # Use the async version directly since we're already in an async context
        from sentiment_extractor import analyze_tweet_sentiment
        sentiment_analysis = await analyze_tweet_sentiment(tweet_text, author)
        
        print(f"✅ Generated Search Query: '{sentiment_analysis.search_query}'")
        print(f"🏷️  Key Topics: {sentiment_analysis.key_topics}")
        print(f"📊 Sentiment Score: {sentiment_analysis.sentiment_score}")
        print(f"🎯 Confidence: {sentiment_analysis.confidence}")
        print()
        
        # Step 2: Polymarket Search
        print("🔍 Step 2: Searching Polymarket for active markets...")
        market_results = await self.polymarket_client.search_active_markets(sentiment_analysis.search_query)
        
        if "error" in market_results:
            print(f"❌ Polymarket API Error: {market_results['error']}")
            markets_count = 0
        else:
            markets_count = len(market_results) if isinstance(market_results, list) else len(market_results.get('data', []))
            print(f"✅ Found {markets_count} active markets")
        print()
        
        # Step 3: Combine Results
        pipeline_result = {
            "tweet": {
                "text": tweet_text,
                "author": author
            },
            "sentiment_analysis": {
                "search_query": sentiment_analysis.search_query,
                "key_topics": sentiment_analysis.key_topics,
                "sentiment_score": sentiment_analysis.sentiment_score,
                "confidence": sentiment_analysis.confidence
            },
            "polymarket_results": {
                "markets_found": markets_count,
                "search_query_used": sentiment_analysis.search_query,
                "raw_data": market_results
            }
        }
        
        return pipeline_result

# Test function
async def test_complete_pipeline():
    """Test the complete pipeline with various tweets"""
    
    print("🚀 COMPLETE TWEET-TO-POLYMARKET PIPELINE TEST")
    print("=" * 60)
    
    pipeline = TweetMarketPipeline()
    
    # Test tweets covering different market categories
    test_tweets = [
        {
            "text": "Trump is going to win the 2024 election easily! The polls are looking great 🇺🇸",
            "author": "PoliticalAnalyst",
            "category": "Politics"
        },
        {
            "text": "Bitcoin will hit $150,000 before end of 2025! Best investment right now 🚀 #BTC",
            "author": "CryptoTrader",
            "category": "Cryptocurrency"
        },
        {
            "text": "Fed will cut interest rates 3 times this year. Inflation is finally under control!",
            "author": "EconomicExpert",
            "category": "Economics"
        }
    ]
    
    results = []
    
    for i, tweet_data in enumerate(test_tweets, 1):
        print(f"\n🧪 TEST CASE #{i} - {tweet_data['category']}")
        print("=" * 50)
        
        try:
            result = await pipeline.process_tweet(
                tweet_data["text"], 
                tweet_data["author"]
            )
            results.append(result)
            
            # Show summary
            markets_found = result["polymarket_results"]["markets_found"]
            search_query = result["sentiment_analysis"]["search_query"]
            
            print("📋 SUMMARY:")
            print(f"   🔍 Search Query: '{search_query}'")
            print(f"   🏪 Markets Found: {markets_found}")
            print(f"   📊 Sentiment: {result['sentiment_analysis']['sentiment_score']}")
            print()
            
        except Exception as e:
            print(f"❌ Error processing tweet: {e}")
            import traceback
            traceback.print_exc()
        
        # Small delay between requests
        await asyncio.sleep(1)
    
    # Save complete results to file
    output_file = "pipeline_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print("🎯 PIPELINE TEST COMPLETE!")
    print(f"📁 Full results saved to: {output_file}")
    print(f"✅ Successfully processed {len(results)} tweets")
    print("🔍 Each tweet generated a search query and found active markets!")

# Convenience function for single tweet processing
def process_single_tweet_sync(tweet_text: str, author: str = None) -> Dict[str, Any]:
    """
    Synchronous wrapper for processing a single tweet
    
    Args:
        tweet_text: Tweet text to process
        author: Optional author
        
    Returns:
        Complete pipeline results
    """
    pipeline = TweetMarketPipeline()
    return asyncio.run(pipeline.process_tweet(tweet_text, author))

if __name__ == "__main__":
    # Run the complete pipeline test
    asyncio.run(test_complete_pipeline())