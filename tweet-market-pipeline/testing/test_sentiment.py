#!/usr/bin/env python3
"""
Test script for tweet sentiment extraction
Demonstrates the functionality of the SentimentExtractor module
"""
import asyncio
import os
import sys
from datetime import datetime

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import TweetInput, SentimentAnalysis
from sentiment_extractor import SentimentExtractor, analyze_tweet_sentiment_sync


def test_examples():
    """Test the sentiment extraction with various tweet examples"""
    
    # Example tweets covering different topics
    test_tweets = [
        "Bitcoin is going to hit $100k by end of 2024! 🚀 #BTC #crypto",
        "I think Trump will win the 2024 election based on latest polls",
        "Tesla stock looking bullish after the earnings call. $TSLA to the moon! 📈",
        "Fed will definitely cut interest rates next month. Inflation is cooling down.",
        "OpenAI just announced GPT-5! This will change everything for AI adoption",
        "The Lakers are going to win the championship this year with their new roster",
        "Apple's next iPhone will have revolutionary battery tech. Stock will soar!",
        "Climate change will force major policy changes before 2030",
    ]
    
    print("🔍 Testing Tweet Sentiment Extraction")
    print("=" * 60)
    
    for i, tweet_text in enumerate(test_tweets, 1):
        print(f"\n📝 Test Tweet #{i}:")
        print(f"Text: {tweet_text}")
        print("-" * 40)
        
        try:
            # Analyze the tweet
            analysis = analyze_tweet_sentiment_sync(tweet_text, author=f"TestUser{i}")
            
            print(f"🔍 Search Query: '{analysis.search_query}'")
            print(f"🏷️  Key Topics: {analysis.key_topics}")
            print(f"📊 Sentiment Score: {analysis.sentiment_score}")
            print(f"🎯 Confidence: {analysis.confidence}")
            
        except Exception as e:
            print(f"❌ Error analyzing tweet: {e}")
        
        print("-" * 40)


async def test_async_functionality():
    """Test the async functionality of the sentiment extractor"""
    
    print("\n🔄 Testing Async Functionality")
    print("=" * 60)
    
    tweet_text = "Bitcoin just broke $50k! Next stop $100k by end of year 🚀"
    tweet = TweetInput(
        text=tweet_text,
        author="CryptoTrader",
        timestamp=datetime.now(),
        tweet_id="123456789"
    )
    
    extractor = SentimentExtractor()
    
    try:
        analysis = await extractor.extract_sentiment(tweet)
        
        print(f"📝 Tweet: {tweet.text}")
        print(f"👤 Author: {tweet.author}")
        print(f"🔍 Search Query: '{analysis.search_query}'")
        print(f"🏷️  Key Topics: {analysis.key_topics}")
        print(f"📊 Sentiment Score: {analysis.sentiment_score}")
        print(f"🎯 Confidence: {analysis.confidence}")
        
    except Exception as e:
        print(f"❌ Error in async test: {e}")


def test_fallback_functionality():
    """Test fallback functionality when API fails"""
    
    print("\n🛡️  Testing Fallback Functionality")
    print("=" * 60)
    
    # Create extractor with invalid API key to trigger fallback
    extractor = SentimentExtractor(api_key="invalid_key")
    
    tweet = TweetInput(
        text="Tesla stock is going to the moon! #TSLA #ElonMusk great earnings 🚀",
        author="StockTrader"
    )
    
    try:
        # This should trigger fallback analysis
        analysis = asyncio.run(extractor.extract_sentiment(tweet))
        
        print(f"📝 Tweet: {tweet.text}")
        print(f"🔍 Search Query: '{analysis.search_query}'")
        print(f"🏷️  Key Topics: {analysis.key_topics}")
        print(f"📊 Sentiment Score: {analysis.sentiment_score}")
        print(f"🎯 Confidence: {analysis.confidence}")
        print("✅ Fallback analysis worked successfully!")
        
    except Exception as e:
        print(f"❌ Error in fallback test: {e}")


def main():
    """Run all tests"""
    
    print("🚀 Tweet Sentiment Extraction Test Suite")
    print("=" * 60)
    
    # Check if API key is available
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key or api_key == "your_cohere_api_key_here":
        print("⚠️  Warning: COHERE_API_KEY not found or using placeholder.")
        print("   Set your Cohere API key in .env file for full testing.")
        print("   Fallback functionality will be demonstrated instead.")
        print()
    
    # Run synchronous tests
    test_examples()
    
    # Run async test
    asyncio.run(test_async_functionality())
    
    # Test fallback functionality
    test_fallback_functionality()
    
    print("\n✅ All tests completed!")
    print("\n💡 Next step: Use these search queries with Polymarket API")


if __name__ == "__main__":
    main()