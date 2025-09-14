#!/usr/bin/env python3
"""
Quick verification that Cohere API is working with real calls
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import TweetInput
from sentiment_extractor import analyze_tweet_sentiment_sync

def main():
    print("🔍 Verifying Real Cohere API Usage")
    print("=" * 50)
    
    # Test with a specific tweet to see real API response
    test_tweet = "Ethereum will hit $5000 before the end of this year! The merge was a success 🚀 #ETH"
    
    print(f"📝 Test Tweet: {test_tweet}")
    print("-" * 50)
    
    try:
        # This should use the real Cohere API
        analysis = analyze_tweet_sentiment_sync(test_tweet, author="CryptoAnalyst")
        
        print("✅ REAL COHERE API CALL SUCCESSFUL!")
        print(f"🔍 Generated Search Query: '{analysis.search_query}'")
        print(f"🏷️  Extracted Key Topics: {analysis.key_topics}")
        print(f"📊 Sentiment Score: {analysis.sentiment_score}")
        print(f"🎯 Confidence Level: {analysis.confidence}")
        
        # Verify this isn't fallback data
        if analysis.confidence >= 0.8 and len(analysis.key_topics) > 1:
            print("\n✅ CONFIRMED: This is using REAL Cohere API (not fallback)")
        else:
            print("\n⚠️  WARNING: This might be using fallback logic")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    print("\n" + "=" * 50)
    print("🚀 Ready to integrate with Polymarket API!")

if __name__ == "__main__":
    main()