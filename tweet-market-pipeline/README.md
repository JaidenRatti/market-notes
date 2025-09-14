# Tweet-to-Market Pipeline

An intelligent pipeline that analyzes tweets and finds the most relevant prediction markets on Polymarket using AI-powered sentiment analysis and market ranking.

## Features

- **Tweet Sentiment Analysis**: Uses Cohere AI to extract key topics and generate search queries
- **Polymarket Integration**: Searches active prediction markets with filtering
- **AI-Powered Ranking**: Uses Cohere to rank markets by relevance to tweet content
- **Easy Integration**: Simple function interface for use in other programs
- **Comprehensive Output**: Returns top 5 most relevant markets with explanations

## Quick Start

### 1. Setup Environment
```bash
# Enter directory
cd tweet-market-pipeline

# Create virtual environment  
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your COHERE_API_KEY
```

### 2. Command Line Usage
```bash
# Analyze any tweet
python tweet_analyzer.py "Bitcoin will hit $150K by end of 2025!"

# Interactive mode
python tweet_analyzer.py --interactive

# Demo mode with examples
python tweet_analyzer.py --demo
```

### 3. Use as Python Function
```python
from tweet_analyzer import analyze_tweet

# Analyze any tweet
result = analyze_tweet("Fed will cut rates next month!", author="EconAnalyst")

# Access results
top_market = result["top_relevant_markets"][0]
print(f"Top market: {top_market['title']}")
print(f"Relevance: {top_market['relevance_score']:.2f}")
```

## Module Structure

### Core Files (Essential)
- **`tweet_analyzer.py`** - Main interface for analyzing tweets (your entry point)
- **`include/`** - Internal implementation modules:
  - `enhanced_pipeline.py` - Core pipeline orchestration
  - `sentiment_extractor.py` - Tweet sentiment analysis with Cohere
  - `polymarket_client.py` - Polymarket API client
  - `market_ranker.py` - AI-powered market relevance ranking
  - `config.py` - Configuration and API settings
  - `models.py` - Data models and structures

### Documentation & Examples
- **`FUNCTION_USAGE.md`** - Complete guide for using as a Python function
- **`usage_examples.py`** - Comprehensive examples of integration patterns
- **`README.md`** - This file
- **`requirements.txt`** - Python dependencies
- **`.env.example`** - Environment variable template

### Testing & Development
- **`testing/`** - Archived test files and development scripts (not needed for usage)

## Example Output

For tweet: *"CZ pardon odds keep rising on Polymarket with zero news. Are these Binance insiders buying?"*

```
🎯 Top 5 most relevant markets (after AI ranking):

#1. Will Trump pardon Changpeng Zhao by September 30?
    Score: 0.90/1.0
    Why: Direct relevance to CZ pardon odds mentioned in tweet

#2. Who will Trump pardon in 2025?
    Score: 0.45/1.0
    Why: Related to pardons but less specific to CZ

[...more results...]
```

## Function Usage

See **`FUNCTION_USAGE.md`** for complete documentation on:
- Basic function usage
- Return data structure (complete JSON format)
- Integration patterns
- Error handling
- Web API integration
- Real-time monitoring examples

Or run the comprehensive examples:
```bash
python usage_examples.py
```

## Architecture

1. **Sentiment Analysis** (`sentiment_extractor.py`): Cohere AI analyzes tweet sentiment and generates search terms
2. **Market Search** (`polymarket_client.py`): Queries Polymarket API for active prediction markets
3. **AI Ranking** (`market_ranker.py`): Cohere AI ranks markets by relevance to original tweet
4. **Pipeline Orchestration** (`enhanced_pipeline.py`): Coordinates the full workflow

## Performance

- **Processing Time**: ~2-5 seconds per tweet
- **API Dependencies**: Requires Cohere API and internet connection
- **Market Coverage**: Searches all active Polymarket prediction markets
- **Accuracy**: AI relevance scoring typically 85%+ accurate for domain-relevant tweets

## Requirements

- Python 3.8+
- Cohere API key (for AI analysis)
- Internet connection (for Polymarket API)
- See `requirements.txt` for Python dependencies
