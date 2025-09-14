# Tweet-Market Analysis Pipeline

## Step 2: Tweet Sentiment Extraction ✅ COMPLETED

This module analyzes tweet text using Cohere AI to extract sentiment, key themes, and generate optimized search queries for Polymarket's prediction markets.

### Features

- 🧠 **AI-Powered Analysis**: Uses Cohere's LLM to understand tweet context and sentiment
- 🔍 **Smart Query Generation**: Creates optimized search queries for Polymarket API
- 🏷️ **Topic Extraction**: Identifies key topics and themes related to prediction markets
- 📊 **Sentiment Scoring**: Provides sentiment analysis (-1.0 to 1.0 scale)
- 🛡️ **Robust Fallback**: Works even when API fails using keyword extraction
- ⚡ **Async Support**: Both synchronous and asynchronous interfaces

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your COHERE_API_KEY
```

### Quick Start

```python
from sentiment_extractor import analyze_tweet_sentiment_sync

# Analyze a tweet
result = analyze_tweet_sentiment_sync(
    "Bitcoin is going to hit $100k by end of 2024! 🚀 #BTC"
)

print(f"Search Query: {result.search_query}")    # "Bitcoin"
print(f"Key Topics: {result.key_topics}")        # ["Bitcoin", "cryptocurrency", "2024"]
print(f"Sentiment: {result.sentiment_score}")    # 0.8 (positive)
```

### Advanced Usage

```python
import asyncio
from models import TweetInput
from sentiment_extractor import SentimentExtractor

async def analyze_tweet():
    tweet = TweetInput(
        text="Tesla stock looking bullish after earnings! $TSLA 📈",
        author="StockTrader",
        tweet_id="123456"
    )
    
    extractor = SentimentExtractor()
    analysis = await extractor.extract_sentiment(tweet)
    
    return analysis

# Run async analysis
result = asyncio.run(analyze_tweet())
```

### Testing

Run the test suite to see examples:

```bash
cd tweet-market-pipeline
python test_sentiment.py
```

### Output Format

The `SentimentAnalysis` model returns:

```python
{
    "search_query": "Bitcoin",              # Optimized for Polymarket search
    "key_topics": ["Bitcoin", "2024"],      # Related prediction market topics
    "sentiment_score": 0.8,                 # -1.0 (negative) to 1.0 (positive)
    "confidence": 0.8                       # Confidence in the analysis
}
```

### Examples

| Tweet | Search Query | Key Topics |
|-------|-------------|------------|
| "Bitcoin hitting $100k this year 🚀" | "Bitcoin" | ["Bitcoin", "cryptocurrency", "2024"] |
| "Trump will win 2024 election easily" | "election 2024" | ["Trump", "election", "2024"] |
| "Tesla stock going to moon after earnings!" | "Tesla stock" | ["Tesla", "earnings", "stock"] |
| "Fed cutting rates next month for sure" | "Fed rates" | ["Federal Reserve", "interest rates"] |

### Next Steps

The generated search queries are ready to be used with:
- **Step 3**: Polymarket API client to fetch related markets
- **Step 4**: Market relevance ranking with Cohere
- **Step 5**: Final pipeline orchestration

### Error Handling

The module includes robust error handling:
- **API Failures**: Automatic fallback to keyword extraction
- **Invalid Input**: Graceful handling of malformed tweets
- **Rate Limiting**: Built-in delays and retry logic
- **Confidence Scoring**: Lower confidence for fallback methods

### Configuration

Customize behavior in `config.py`:
- `sentiment_max_tokens`: Response length (default: 50)
- `sentiment_temperature`: Creativity level (default: 0.3)
- `cohere_model`: Model to use (default: "command-r-plus")