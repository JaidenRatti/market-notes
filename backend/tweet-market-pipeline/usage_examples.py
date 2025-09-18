#!/usr/bin/env python3
"""
Examples of how to use the Tweet-to-Market Pipeline as a function in your programs
"""
import sys
import os
import json
from typing import Dict, List, Any

# Add the pipeline directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main function
from tweet_analyzer import analyze_tweet

# Example 1: Basic Usage
def basic_usage_example():
    """Most simple way to use the pipeline"""
    print("=== BASIC USAGE ===")
    
    tweet = "Bitcoin will hit $150K by end of 2025! This bull run is just getting started 🚀"
    
    # Simple function call - returns complete results
    result = analyze_tweet(tweet, author="CryptoTrader", save_to_file=False)
    
    # Access the results
    if "top_relevant_markets" in result:
        markets = result["top_relevant_markets"]
        print(f"Found {len(markets)} relevant markets")
        print(f"Top market: {markets[0]['title']} (Score: {markets[0]['relevance_score']:.2f})")
    
    return result

# Example 2: Process Multiple Tweets
def batch_processing_example():
    """Process multiple tweets in a batch"""
    print("\n=== BATCH PROCESSING ===")
    
    tweets = [
        "Fed will cut rates by 50 basis points next meeting",
        "Taylor Swift will announce tour dates before December",
        "Lakers going to win the championship this year!",
        "Trump will win 2024 election by landslide"
    ]
    
    results = []
    for i, tweet in enumerate(tweets):
        print(f"\nProcessing tweet {i+1}/{len(tweets)}...")
        result = analyze_tweet(tweet, author=f"User{i+1}", save_to_file=False)
        results.append({
            "tweet": tweet,
            "result": result
        })
    
    return results

# Example 3: Extract Only What You Need
def extract_specific_data_example():
    """Show how to extract only the data you need"""
    print("\n=== EXTRACT SPECIFIC DATA ===")
    
    tweet = "CZ pardon odds rising on Polymarket with no news. Insiders buying?"
    result = analyze_tweet(tweet, save_to_file=False)
    
    if "top_relevant_markets" in result:
        # Extract just the top market info
        top_market = result["top_relevant_markets"][0]
        
        market_info = {
            "title": top_market["title"],
            "score": top_market["relevance_score"],
            "ticker": top_market.get("ticker", "N/A"),
            "reason": top_market["relevance_explanation"]
        }
        
        print("Top Market Info:")
        for key, value in market_info.items():
            print(f"  {key}: {value}")
        
        return market_info
    
    return None

# Example 4: Custom Function Wrapper
def get_top_market_for_tweet(tweet_text: str, author: str = "Unknown") -> Dict[str, Any]:
    """
    Custom wrapper that returns only the most relevant market
    """
    result = analyze_tweet(tweet_text, author=author, save_to_file=False)
    
    if "top_relevant_markets" in result and len(result["top_relevant_markets"]) > 0:
        top_market = result["top_relevant_markets"][0]
        return {
            "success": True,
            "market": {
                "title": top_market["title"],
                "relevance_score": top_market["relevance_score"],
                "ticker": top_market.get("ticker"),
                "explanation": top_market["relevance_explanation"],
                "polymarket_url": f"https://polymarket.com/event/{top_market.get('ticker', '')}"
            },
            "search_query": result["sentiment_analysis"]["search_query"],
            "sentiment_score": result["sentiment_analysis"]["sentiment_score"]
        }
    else:
        return {
            "success": False,
            "error": "No relevant markets found",
            "search_query": result.get("sentiment_analysis", {}).get("search_query", ""),
            "sentiment_score": result.get("sentiment_analysis", {}).get("sentiment_score", 0)
        }

# Example 5: Error Handling
def robust_analysis_with_error_handling(tweet_text: str) -> Dict[str, Any]:
    """
    Robust function with comprehensive error handling
    """
    try:
        # Validate input
        if not tweet_text or not isinstance(tweet_text, str):
            return {"error": "Invalid tweet text provided", "success": False}
        
        if len(tweet_text.strip()) < 10:
            return {"error": "Tweet text too short", "success": False}
        
        # Process the tweet
        result = analyze_tweet(tweet_text, save_to_file=False)
        
        # Check for errors in the result
        if "error" in result:
            return {"error": result["error"], "success": False}
        
        # Validate we got markets
        if "top_relevant_markets" not in result or not result["top_relevant_markets"]:
            return {"error": "No relevant markets found", "success": False, "result": result}
        
        return {"success": True, "result": result}
        
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "success": False}

# Example 6: Integration with Web App
def web_app_integration_example():
    """
    Example of how you might integrate this in a web application
    """
    print("\n=== WEB APP INTEGRATION EXAMPLE ===")
    
    def analyze_tweet_for_api(tweet_text: str, author: str = None) -> Dict[str, Any]:
        """
        Function designed for API responses - returns clean, structured data
        """
        try:
            result = analyze_tweet(tweet_text, author=author, save_to_file=False)
            
            # Structure for API response
            api_response = {
                "status": "success",
                "data": {
                    "tweet": {
                        "text": tweet_text,
                        "author": author or "Unknown"
                    },
                    "analysis": {
                        "search_query": result.get("sentiment_analysis", {}).get("search_query", ""),
                        "sentiment_score": result.get("sentiment_analysis", {}).get("sentiment_score", 0),
                        "key_topics": result.get("sentiment_analysis", {}).get("key_topics", [])
                    },
                    "markets": []
                }
            }
            
            # Add market data
            if "top_relevant_markets" in result:
                for market in result["top_relevant_markets"]:
                    api_response["data"]["markets"].append({
                        "rank": market["rank"],
                        "title": market["title"],
                        "relevance_score": round(market["relevance_score"], 3),
                        "ticker": market.get("ticker"),
                        "explanation": market["relevance_explanation"],
                        "polymarket_url": f"https://polymarket.com/event/{market.get('ticker', '')}"
                    })
            
            return api_response
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }
    
    # Test the API function
    sample_tweet = "Fed hiking rates again! Recession incoming 📉"
    api_result = analyze_tweet_for_api(sample_tweet, "EconAnalyst")
    print(json.dumps(api_result, indent=2))
    
    return api_result

# Example 7: Real-time Tweet Monitoring
class TweetMarketMonitor:
    """
    Class for monitoring and analyzing tweets in real-time
    """
    
    def __init__(self):
        self.analyzed_tweets = []
        self.high_relevance_threshold = 0.7
    
    def analyze_and_store(self, tweet_text: str, author: str = None) -> Dict[str, Any]:
        """Analyze tweet and store results"""
        result = analyze_tweet(tweet_text, author=author, save_to_file=False)
        
        # Store for later analysis
        self.analyzed_tweets.append({
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "tweet": tweet_text,
            "author": author,
            "result": result
        })
        
        return result
    
    def get_high_relevance_alerts(self) -> List[Dict[str, Any]]:
        """Get tweets with high-relevance market matches"""
        alerts = []
        
        for entry in self.analyzed_tweets:
            result = entry["result"]
            if "top_relevant_markets" in result and result["top_relevant_markets"]:
                top_market = result["top_relevant_markets"][0]
                if top_market["relevance_score"] >= self.high_relevance_threshold:
                    alerts.append({
                        "tweet": entry["tweet"],
                        "author": entry["author"],
                        "timestamp": entry["timestamp"],
                        "top_market": top_market["title"],
                        "relevance_score": top_market["relevance_score"]
                    })
        
        return alerts

def run_monitor_example():
    """Example of using the monitor class"""
    print("\n=== REAL-TIME MONITORING EXAMPLE ===")
    
    monitor = TweetMarketMonitor()
    
    # Simulate analyzing several tweets
    test_tweets = [
        ("Bitcoin going to moon! $200K target 🚀", "CryptoWhale"),
        ("Fed meeting next week will be dovish", "EconExpert"), 
        ("Just had coffee this morning", "RandomUser"),
        ("CZ pardon odds spiking on Polymarket", "DegenTrader")
    ]
    
    for tweet, author in test_tweets:
        print(f"Analyzing: {tweet[:50]}...")
        monitor.analyze_and_store(tweet, author)
    
    # Get high-relevance alerts
    alerts = monitor.get_high_relevance_alerts()
    print(f"\n📢 Found {len(alerts)} high-relevance alerts:")
    
    for alert in alerts:
        print(f"  🚨 '{alert['tweet'][:50]}...' -> {alert['top_market']} (Score: {alert['relevance_score']:.2f})")

if __name__ == "__main__":
    # Run all examples
    print("🚀 TWEET PIPELINE USAGE EXAMPLES")
    print("=" * 60)
    
    # Run examples
    basic_usage_example()
    batch_processing_example()
    extract_specific_data_example()
    
    # Test custom wrapper
    print("\n=== CUSTOM WRAPPER TEST ===")
    custom_result = get_top_market_for_tweet("Will Trump pardon CZ before 2026?", "PoliticalTrader")
    print(f"Success: {custom_result['success']}")
    if custom_result['success']:
        print(f"Top Market: {custom_result['market']['title']}")
        print(f"Score: {custom_result['market']['relevance_score']:.2f}")
    
    # Test error handling
    print("\n=== ERROR HANDLING TEST ===")
    error_result = robust_analysis_with_error_handling("")
    print(f"Error handling result: {error_result}")
    
    # Web app example
    web_app_integration_example()
    
    # Monitor example
    run_monitor_example()
    
    print("\n✅ All examples completed!")