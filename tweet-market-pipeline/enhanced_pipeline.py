#!/usr/bin/env python3
"""
Enhanced Tweet-to-Market Pipeline with AI Ranking
Complete pipeline: Tweet → Sentiment Analysis → Polymarket Search → AI Ranking → Top 5 Markets
"""
import asyncio
import json
import os
import sys
from typing import Dict, Any, Optional
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentiment_extractor import analyze_tweet_sentiment
from polymarket_client import PolymarketClient
from market_ranker import MarketRelevanceRanker, format_top_markets_json

class EnhancedTweetMarketPipeline:
    """Complete AI-powered pipeline from tweet to ranked markets"""
    
    def __init__(self):
        self.polymarket_client = PolymarketClient()
        self.market_ranker = MarketRelevanceRanker()
    
    async def process_tweet_with_ranking(
        self, 
        tweet_text: str, 
        author: str = None,
        top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Complete enhanced pipeline with AI ranking
        
        Args:
            tweet_text: The tweet to analyze
            author: Optional author of the tweet
            top_n: Number of top markets to return
            
        Returns:
            Clean JSON with top N most relevant markets
        """
        print(f"🚀 ENHANCED PIPELINE: {tweet_text}")
        print("=" * 70)
        
        # Step 1: Sentiment Analysis with Cohere
        print("📊 Step 1: Analyzing tweet sentiment...")
        sentiment_result = await analyze_tweet_sentiment(tweet_text, author)
        
        sentiment_analysis = {
            "search_query": sentiment_result.search_query,
            "key_topics": sentiment_result.key_topics,
            "sentiment_score": sentiment_result.sentiment_score,
            "confidence": sentiment_result.confidence
        }
        
        print(f"✅ Search Query: '{sentiment_analysis['search_query']}'")
        print(f"🏷️  Key Topics: {sentiment_analysis['key_topics']}")
        print()
        
        # Step 2: Polymarket Search
        print("🔍 Step 2: Searching Polymarket for active markets...")
        market_results = await self.polymarket_client.search_active_markets(
            sentiment_analysis["search_query"]
        )
        
        if "error" in market_results:
            return {
                "error": f"Polymarket API error: {market_results['error']}",
                "tweet": {"text": tweet_text, "author": author},
                "sentiment_analysis": sentiment_analysis
            }
        
        markets_found = len(market_results) if isinstance(market_results, list) else 0
        print(f"✅ Found {markets_found} active markets")
        print()
        
        # Step 3: AI-Powered Market Ranking
        print("🧠 Step 3: Ranking markets by relevance with AI...")
        top_markets = await self.market_ranker.rank_markets(
            tweet_text=tweet_text,
            sentiment_analysis=sentiment_analysis,
            market_results=market_results,
            top_n=top_n
        )
        print()
        
        # Step 4: Format Final Results
        print("📋 Step 4: Formatting results...")
        final_result = format_top_markets_json(
            tweet_text=tweet_text,
            sentiment_analysis=sentiment_analysis,
            top_markets=top_markets
        )
        
        print(f"✅ Pipeline complete! Returning top {len(top_markets)} most relevant markets")
        print()
        
        return final_result

# Test function
async def test_enhanced_pipeline():
    """Test the enhanced pipeline with real data"""
    
    print("🚀 ENHANCED TWEET-TO-MARKET PIPELINE TEST")
    print("=" * 70)
    
    pipeline = EnhancedTweetMarketPipeline()
    
    # Test tweets for different categories
    test_cases = [
        {
            "text": "Fed will definitely cut rates in 2025! Inflation is coming down fast 📉",
            "author": "EconomicAnalyst",
            "category": "Economics"
        },
        {
            "text": "Bitcoin to $200K by end of 2025! Best crypto investment opportunity 🚀 #BTC",
            "author": "CryptoExpert", 
            "category": "Cryptocurrency"
        },
        {
            "text": "Trump's 2024 election win is guaranteed based on latest swing state polls! 🇺🇸",
            "author": "PoliticalAnalyst",
            "category": "Politics"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASE #{i} - {test_case['category']}")
        print("=" * 60)
        
        try:
            result = await pipeline.process_tweet_with_ranking(
                test_case["text"], 
                test_case["author"],
                top_n=5
            )
            
            results.append({
                "test_case": i,
                "category": test_case["category"],
                "result": result
            })
            
            # Show summary
            if "top_relevant_markets" in result:
                top_markets = result["top_relevant_markets"]
                print("📊 TOP RANKED MARKETS:")
                for market in top_markets:
                    rank = market["rank"]
                    title = market["title"]
                    score = market["relevance_score"]
                    print(f"   #{rank}: {title} (Score: {score:.2f})")
            else:
                print("❌ No markets returned")
            print()
            
        except Exception as e:
            print(f"❌ Error in test case: {e}")
            import traceback
            traceback.print_exc()
        
        # Delay between tests
        await asyncio.sleep(2)
    
    # Save all results
    output_file = "enhanced_pipeline_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("=" * 70)
    print("🎯 ENHANCED PIPELINE TEST COMPLETE!")
    print(f"📁 Full results saved to: {output_file}")
    print(f"✅ Processed {len(results)} tweets with AI ranking")
    print("🧠 Each tweet was analyzed, searched, and ranked using AI!")

# Convenience function for single tweet processing
def process_tweet_with_ranking_sync(tweet_text: str, author: str = None, top_n: int = 5) -> Dict[str, Any]:
    """
    Synchronous wrapper for the enhanced pipeline
    
    Args:
        tweet_text: Tweet text to process
        author: Optional author
        top_n: Number of top markets to return
        
    Returns:
        Complete pipeline results with AI ranking
    """
    pipeline = EnhancedTweetMarketPipeline()
    return asyncio.run(pipeline.process_tweet_with_ranking(tweet_text, author, top_n))

if __name__ == "__main__":
    # Run the enhanced pipeline test
    asyncio.run(test_enhanced_pipeline())