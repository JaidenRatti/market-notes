"""
Data models for the Tweet-Market Analysis Pipeline
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class TweetInput(BaseModel):
    """Input tweet data"""
    text: str = Field(..., description="The tweet text content")
    author: Optional[str] = Field(None, description="Tweet author username")
    timestamp: Optional[datetime] = Field(None, description="Tweet timestamp")
    tweet_id: Optional[str] = Field(None, description="Tweet ID")

class SentimentAnalysis(BaseModel):
    """Extracted sentiment and search query from tweet"""
    search_query: str = Field(..., description="Concise search query derived from tweet sentiment")
    key_topics: List[str] = Field(default_factory=list, description="Key topics identified in the tweet")
    sentiment_score: Optional[float] = Field(None, description="Sentiment score if available")
    confidence: Optional[float] = Field(None, description="Confidence in the extraction")

class PolymarketOutcome(BaseModel):
    """Individual outcome in a Polymarket event"""
    id: str
    title: str
    price: float = Field(..., ge=0.0, le=1.0, description="Price as decimal (0-1)")
    tokens: str

class PolymarketMarket(BaseModel):
    """Polymarket market/event data"""
    id: str
    question: str
    description: Optional[str] = None
    image: Optional[str] = None
    icon: Optional[str] = None
    slug: str
    market_slug: str
    outcomes: List[PolymarketOutcome]
    volume: float = Field(default=0.0, description="Market volume")
    volume_num: float = Field(default=0.0, description="Numeric volume")
    liquidity: float = Field(default=0.0, description="Market liquidity") 
    end_date_iso: Optional[str] = Field(None, description="Market end date")
    closed: bool = Field(default=False, description="Whether market is closed")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    @property
    def is_active(self) -> bool:
        """Check if market is active (not closed)"""
        return not self.closed

class RelevanceScore(BaseModel):
    """Market relevance scoring result"""
    market_id: str
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    relevance_explanation: str = Field(..., description="Explanation of why this market is relevant")
    key_matches: List[str] = Field(default_factory=list, description="Key matching topics/themes")

class RankedMarket(BaseModel):
    """Market with relevance ranking"""
    market: PolymarketMarket
    relevance: RelevanceScore

class PipelineResult(BaseModel):
    """Final pipeline output"""
    tweet: TweetInput
    sentiment_analysis: SentimentAnalysis
    total_markets_found: int
    ranked_markets: List[RankedMarket]
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def to_display_json(self) -> Dict[str, Any]:
        """Convert to JSON format suitable for display in your application"""
        return {
            "tweet": {
                "text": self.tweet.text,
                "author": self.tweet.author,
                "timestamp": self.tweet.timestamp.isoformat() if self.tweet.timestamp else None,
                "tweet_id": self.tweet.tweet_id
            },
            "analysis": {
                "search_query": self.sentiment_analysis.search_query,
                "key_topics": self.sentiment_analysis.key_topics,
                "sentiment_score": self.sentiment_analysis.sentiment_score,
                "confidence": self.sentiment_analysis.confidence
            },
            "markets": [
                {
                    "id": rm.market.id,
                    "question": rm.market.question,
                    "description": rm.market.description,
                    "slug": rm.market.slug,
                    "market_slug": rm.market.market_slug,
                    "volume": rm.market.volume,
                    "liquidity": rm.market.liquidity,
                    "end_date": rm.market.end_date_iso,
                    "closed": rm.market.closed,
                    "tags": rm.market.tags,
                    "outcomes": [
                        {
                            "id": outcome.id,
                            "title": outcome.title,
                            "price": outcome.price,
                            "tokens": outcome.tokens
                        }
                        for outcome in rm.market.outcomes
                    ],
                    "relevance": {
                        "score": rm.relevance.relevance_score,
                        "explanation": rm.relevance.relevance_explanation,
                        "key_matches": rm.relevance.key_matches
                    }
                }
                for rm in self.ranked_markets
            ],
            "metadata": {
                "total_markets_found": self.total_markets_found,
                "processing_time": self.processing_time,
                "timestamp": self.timestamp.isoformat()
            }
        }