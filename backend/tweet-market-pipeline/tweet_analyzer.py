#!/usr/bin/env python3
"""
Simple Tweet Analyzer Interface
Easy way to analyze any tweet and get top 5 relevant prediction markets
"""
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'include'))

from include.enhanced_pipeline import process_tweet_with_ranking_sync

def analyze_tweet(tweet_text: str, author: str = None, top_n: int = 5, save_to_file: bool = True) -> dict:
    """
    Analyze any tweet and get top relevant markets
    
    Args:
        tweet_text: The tweet text to analyze
        author: Optional tweet author (default: "Unknown")
        top_n: Number of top markets to return (default: 5)
        save_to_file: Whether to save results to a JSON file (default: True)
    
    Returns:
        Dict containing complete analysis results
    """
    if not author:
        author = "Unknown"
    
    print(f"🔍 Analyzing tweet: {tweet_text}")
    print("=" * 60)
    
    try:
        # Process the tweet through the complete pipeline
        result = process_tweet_with_ranking_sync(tweet_text, author, top_n)
        
        # Display summary
        if "top_relevant_markets" in result:
            markets = result["top_relevant_markets"]
            search_query = result["sentiment_analysis"]["search_query"]
            sentiment_score = result["sentiment_analysis"]["sentiment_score"]
            
            print(f"✅ Generated search query: '{search_query}'")
            print(f"📊 Sentiment score: {sentiment_score}")
            print(f"🎯 Top {len(markets)} most relevant markets (after AI ranking):")
            print()
            
            for market in markets:
                rank = market["rank"]
                title = market["title"]
                score = market["relevance_score"]
                explanation = market["relevance_explanation"]
                
                print(f"#{rank}. {title}")
                print(f"    Score: {score:.2f}/1.0")
                print(f"    Why: {explanation}")
                print()
        
        # Save to file if requested
        if save_to_file:
            filename = f"tweet_analysis_{hash(tweet_text) % 10000}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Full results saved to: {filename}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error analyzing tweet: {e}")
        return {"error": str(e)}

def quick_demo():
    """Run a quick demo with various tweet examples"""
    
    print("🚀 TWEET ANALYZER DEMO")
    print("=" * 60)
    
    # Example tweets to demonstrate different categories
    demo_tweets = [
        "Nvidia stock will hit $200 by end of 2025! AI boom is just getting started 🚀",
        "Taylor Swift will win Album of the Year at the 2025 Grammys! 🎵",
        "The Lakers are going all the way this year! Championship incoming 🏆",
        "Climate change will force major renewable energy adoption by 2030 🌱",
    ]
    
    for i, tweet in enumerate(demo_tweets, 1):
        print(f"\n📝 DEMO #{i}")
        print("-" * 40)
        analyze_tweet(tweet, author=f"DemoUser{i}", save_to_file=False)
        print("-" * 40)

def interactive_mode():
    """Interactive mode where users can input their own tweets"""
    
    print("🎯 INTERACTIVE TWEET ANALYZER")
    print("=" * 60)
    print("Enter any tweet text to analyze (or 'quit' to exit)")
    print()
    
    while True:
        try:
            tweet_text = input("📝 Enter tweet: ").strip()
            
            if tweet_text.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not tweet_text:
                print("⚠️  Please enter some tweet text")
                continue
            
            # Optional: ask for author
            author = input("👤 Enter author (optional): ").strip()
            if not author:
                author = "User"
            
            print()
            result = analyze_tweet(tweet_text, author)
            
            # Ask if they want to continue
            print("\n" + "=" * 60)
            continue_choice = input("🔄 Analyze another tweet? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print("👋 Thanks for using the Tweet Analyzer!")
                break
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def analyze_from_command_line():
    """Analyze tweet from command line arguments"""
    
    if len(sys.argv) < 2:
        print("Usage: python tweet_analyzer.py \"Your tweet text here\"")
        print("   or: python tweet_analyzer.py --demo")
        print("   or: python tweet_analyzer.py --interactive")
        return
    
    if sys.argv[1] == "--demo":
        quick_demo()
        return
    
    if sys.argv[1] == "--interactive":
        interactive_mode()
        return
    
    # Analyze the provided tweet
    tweet_text = " ".join(sys.argv[1:])
    analyze_tweet(tweet_text)

if __name__ == "__main__":
    analyze_from_command_line()