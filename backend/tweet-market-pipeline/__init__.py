"""
Tweet-Market Analysis Pipeline

A pipeline that analyzes tweet sentiment, extracts search queries,
and finds relevant Polymarket prediction markets.
"""

from .models import (
    TweetInput,
    SentimentAnalysis, 
    PolymarketMarket,
    PolymarketOutcome,
    RelevanceScore,
    RankedMarket,
    PipelineResult
)

from .config import config
from .sentiment_extractor import SentimentExtractor, analyze_tweet_sentiment, analyze_tweet_sentiment_sync

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = [
    "TweetInput",
    "SentimentAnalysis",
    "PolymarketMarket", 
    "PolymarketOutcome",
    "RelevanceScore",
    "RankedMarket",
    "PipelineResult",
    "config",
    "SentimentExtractor",
    "analyze_tweet_sentiment",
    "analyze_tweet_sentiment_sync"
]