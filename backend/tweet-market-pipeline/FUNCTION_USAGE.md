# Using Tweet-to-Market Pipeline as a Function

This guide shows you how to use the tweet analysis pipeline as a function in your own Python programs.

## Quick Start

### Basic Function Call
```python
from tweet_analyzer import analyze_tweet

# Analyze any tweet
result = analyze_tweet("Bitcoin will hit $150K by 2025!", author="CryptoTrader")

# Access the top market
if "top_relevant_markets" in result:
    top_market = result["top_relevant_markets"][0]
    print(f"Top market: {top_market['title']}")
    print(f"Relevance score: {top_market['relevance_score']:.2f}")
```

### Return Data Structure

The `analyze_tweet()` function returns a comprehensive JSON object with the following structure:

```json
{
  "tweet": {
    "text": "Bitcoin will hit $150K by end of 2025! This bull run is just getting started 🚀",
    "author": "CryptoTrader"
  },
  "sentiment_analysis": {
    "search_query": "Bitcoin price prediction",
    "sentiment_score": 0.75,
    "key_topics": ["cryptocurrency", "Bitcoin", "price prediction", "bull market"],
    "confidence": 0.92
  },
  "top_relevant_markets": [
    {
      "rank": 1,
      "title": "Bitcoin to hit $150k by end of 2025?",
      "ticker": "bitcoin-150k-2025",
      "relevance_score": 0.95,
      "relevance_explanation": "This market directly matches the tweet's prediction about Bitcoin reaching $150K by 2025, making it highly relevant for traders interested in this specific price target and timeframe.",
      "market_data": {
        "description": "Will Bitcoin reach $150,000 by December 31, 2025?",
        "category": "Cryptocurrency",
        "end_date": "2025-12-31",
        "active": true,
        "accepting_orders": true
      }
    },
    {
      "rank": 2,
      "title": "Bitcoin price above $100k in 2025?",
      "ticker": "bitcoin-100k-2025", 
      "relevance_score": 0.78,
      "relevance_explanation": "Related to Bitcoin price predictions for 2025, though with a lower price target than mentioned in the tweet.",
      "market_data": {
        "description": "Will Bitcoin trade above $100,000 at any point in 2025?",
        "category": "Cryptocurrency",
        "end_date": "2025-12-31",
        "active": true,
        "accepting_orders": true
      }
    }
  ],
  "polymarket_search": {
    "query_used": "Bitcoin price prediction",
    "total_markets_found": 8,
    "active_markets_returned": 5,
    "search_timestamp": "2025-01-14T15:30:22Z"
  },
  "pipeline_metadata": {
    "processing_time_seconds": 3.2,
    "ai_ranking_used": true,
    "version": "1.0"
  }
}
```

#### Key Fields Explained:

- **`tweet`**: Original tweet text and author information
- **`sentiment_analysis`**: AI-generated search query, sentiment score (0-1), key topics, and confidence
- **`top_relevant_markets`**: Array of markets ranked by AI relevance (0.0-1.0 scores)
  - **`rank`**: Position in ranking (1-N)
  - **`title`**: Market question/title
  - **`ticker`**: Polymarket identifier for the market
  - **`relevance_score`**: AI-calculated relevance (0.0-1.0)
  - **`relevance_explanation`**: Why this market matches the tweet
  - **`market_data`**: Additional market details from Polymarket
- **`polymarket_search`**: Search metadata and statistics
- **`pipeline_metadata`**: Processing information and performance metrics

## Function Parameters

### `analyze_tweet(tweet_text, author=None, top_n=5, save_to_file=True)`

- **tweet_text** (str, required): The tweet text to analyze
- **author** (str, optional): Author of the tweet (default: "Unknown")
- **top_n** (int, optional): Number of top markets to return (default: 5)
- **save_to_file** (bool, optional): Save results to JSON file (default: True)

## Usage Examples

### 1. Simple Analysis
```python
from tweet_analyzer import analyze_tweet

tweet = "Fed will cut rates next month!"
result = analyze_tweet(tweet, save_to_file=False)

# Get the most relevant market
top_market = result["top_relevant_markets"][0]
print(f"Best match: {top_market['title']} (Score: {top_market['relevance_score']:.2f})")
```

### 2. Batch Processing
```python
tweets = [
    "Bitcoin going to $200K!",
    "Taylor Swift tour announcement coming",
    "Lakers winning championship this year"
]

results = []
for tweet in tweets:
    result = analyze_tweet(tweet, save_to_file=False)
    results.append(result)
```

### 3. Custom Wrapper Function
```python
def get_best_market(tweet_text):
    """Get only the most relevant market for a tweet"""
    result = analyze_tweet(tweet_text, save_to_file=False)
    
    if "top_relevant_markets" in result and result["top_relevant_markets"]:
        top_market = result["top_relevant_markets"][0]
        return {
            "title": top_market["title"],
            "score": top_market["relevance_score"],
            "polymarket_url": f"https://polymarket.com/event/{top_market.get('ticker', '')}"
        }
    return None

# Usage
best_market = get_best_market("CZ pardon odds rising!")
if best_market:
    print(f"Best market: {best_market['title']}")
```

### 4. Error Handling
```python
def safe_analyze_tweet(tweet_text):
    """Analyze tweet with error handling"""
    try:
        result = analyze_tweet(tweet_text, save_to_file=False)
        
        if "error" in result:
            print(f"Analysis error: {result['error']}")
            return None
            
        return result
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
result = safe_analyze_tweet("Your tweet here")
if result:
    print("Analysis successful!")
```

### 5. Web API Integration
```python
def tweet_api_endpoint(tweet_text, author=None):
    """API endpoint function"""
    try:
        result = analyze_tweet(tweet_text, author=author, save_to_file=False)
        
        return {
            "status": "success",
            "data": {
                "tweet": {"text": tweet_text, "author": author},
                "markets": result.get("top_relevant_markets", []),
                "sentiment": result.get("sentiment_analysis", {})
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### 6. Real-time Monitoring
```python
class TweetMonitor:
    def __init__(self):
        self.alerts = []
        self.threshold = 0.8
    
    def check_tweet(self, tweet_text):
        result = analyze_tweet(tweet_text, save_to_file=False)
        
        if "top_relevant_markets" in result:
            top_market = result["top_relevant_markets"][0]
            if top_market["relevance_score"] >= self.threshold:
                self.alerts.append({
                    "tweet": tweet_text,
                    "market": top_market["title"],
                    "score": top_market["relevance_score"]
                })
                return True
        return False

# Usage
monitor = TweetMonitor()
if monitor.check_tweet("CZ pardon happening soon!"):
    print("High relevance alert triggered!")
```

## Integration Tips

### For Web Applications
- Set `save_to_file=False` to avoid creating files
- Implement proper error handling
- Consider rate limiting for API usage
- Cache results for repeated queries

### For Data Analysis
- Use batch processing for multiple tweets
- Store results in databases for analysis
- Track relevance scores over time
- Monitor market trends

### For Trading Bots
- Focus on high-relevance scores (>0.7)
- Implement real-time monitoring
- Set up alerts for specific market types
- Combine with other data sources

## Performance Considerations

- Each analysis takes ~2-5 seconds
- Uses AI APIs (requires internet connection)
- Consider caching for repeated tweets
- Batch processing is more efficient

## Complete Example

See `usage_examples.py` for comprehensive examples including:
- Basic usage patterns
- Batch processing
- Custom wrappers
- Error handling
- Web API integration
- Real-time monitoring
- Data extraction techniques

Run the examples:
```bash
python usage_examples.py
```