#!/usr/bin/env python3
"""
Market Relevance Ranker
Uses Cohere AI to rank Polymarket results against tweet sentiment analysis
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import cohere
from config import config

@dataclass
class MarketRelevanceScore:
    """Relevance score for a market"""
    market_id: str
    market_title: str
    relevance_score: float  # 0.0 to 1.0
    relevance_explanation: str
    key_matches: List[str]
    market_data: Dict[str, Any]

class MarketRelevanceRanker:
    """Ranks markets by relevance to tweet sentiment using Cohere AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.cohere_api_key
        self.client = cohere.Client(self.api_key)
        self.model = config.cohere_model
    
    async def rank_markets(
        self, 
        tweet_text: str,
        sentiment_analysis: Dict[str, Any],
        market_results: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[MarketRelevanceScore]:
        """
        Rank markets by relevance to the original tweet
        
        Args:
            tweet_text: Original tweet text
            sentiment_analysis: Sentiment analysis results
            market_results: Raw Polymarket API results
            top_n: Number of top markets to return
            
        Returns:
            List of top N most relevant markets with scores
        """
        if not market_results:
            return []
        
        print(f"🧠 Ranking {len(market_results)} markets for relevance...")
        
        # Extract key info for ranking
        search_query = sentiment_analysis.get("search_query", "")
        key_topics = sentiment_analysis.get("key_topics", [])
        sentiment_score = sentiment_analysis.get("sentiment_score", 0.0)
        
        # Rank each market
        scored_markets = []
        
        for market in market_results:
            try:
                score = await self._score_market_relevance(
                    tweet_text=tweet_text,
                    search_query=search_query,
                    key_topics=key_topics,
                    sentiment_score=sentiment_score,
                    market=market
                )
                scored_markets.append(score)
                
            except Exception as e:
                print(f"⚠️  Error scoring market {market.get('id', 'unknown')}: {e}")
                continue
        
        # Sort by relevance score (highest first)
        scored_markets.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Return top N
        top_markets = scored_markets[:top_n]
        
        print(f"✅ Ranked markets - Top {len(top_markets)} most relevant:")
        for i, market in enumerate(top_markets, 1):
            print(f"   {i}. {market.market_title} (Score: {market.relevance_score:.2f})")
        
        return top_markets
    
    async def _score_market_relevance(
        self,
        tweet_text: str,
        search_query: str,
        key_topics: List[str],
        sentiment_score: float,
        market: Dict[str, Any]
    ) -> MarketRelevanceScore:
        """Score a single market for relevance"""
        
        # Extract market info
        market_id = market.get("id", "")
        market_title = market.get("title", "")
        market_description = market.get("description", "")[:500]  # Limit description length
        market_tags = [tag.get("label", "") for tag in market.get("tags", [])]
        
        # Get first market question if available
        markets_data = market.get("markets", [])
        first_market_question = ""
        if markets_data:
            first_market_question = markets_data[0].get("question", "")
        
        # Create prompt for Cohere
        prompt = f"""
Analyze how relevant this prediction market is to the original tweet and sentiment analysis.

ORIGINAL TWEET: "{tweet_text}"

SENTIMENT ANALYSIS:
- Search Query: "{search_query}"  
- Key Topics: {key_topics}
- Sentiment Score: {sentiment_score} (where 1.0 = very positive, -1.0 = very negative)

PREDICTION MARKET:
- Title: "{market_title}"
- Question: "{first_market_question}"
- Description: "{market_description}"
- Tags: {market_tags}

TASK: Rate the relevance of this market to the original tweet on a scale of 0.0 to 1.0:
- 1.0 = Perfect match (market directly relates to tweet's prediction/topic)
- 0.8-0.9 = High relevance (market relates to main theme)
- 0.6-0.7 = Moderate relevance (market relates to some aspects)
- 0.4-0.5 = Low relevance (market somewhat relates)
- 0.0-0.3 = No relevance (market unrelated to tweet)

Consider:
1. Does the market topic match the tweet's subject matter?
2. Do the key topics from sentiment analysis align with market tags/content?
3. Would someone interested in the tweet's topic find this market useful?
4. Is the market's timeframe relevant to the tweet's context?

RESPOND WITH EXACTLY THIS FORMAT:
SCORE: [0.0-1.0]
EXPLANATION: [1-2 sentence explanation of why this score was given]
KEY_MATCHES: [comma-separated list of 2-3 matching elements between tweet and market]
"""

        try:
            response = self.client.chat(
                message=prompt,
                model=self.model,
                max_tokens=config.relevance_max_tokens,
                temperature=config.relevance_temperature
            )
            
            response_text = response.text.strip()
            
            # Parse the response
            score, explanation, key_matches = self._parse_relevance_response(response_text)
            
            return MarketRelevanceScore(
                market_id=market_id,
                market_title=market_title,
                relevance_score=score,
                relevance_explanation=explanation,
                key_matches=key_matches,
                market_data=market
            )
            
        except Exception as e:
            print(f"⚠️  Error getting relevance score: {e}")
            # Fallback scoring based on simple keyword matching
            return self._fallback_score_market(
                tweet_text, search_query, key_topics, market
            )
    
    def _parse_relevance_response(self, response_text: str) -> tuple[float, str, List[str]]:
        """Parse Cohere's relevance scoring response"""
        
        score = 0.0
        explanation = "No explanation provided"
        key_matches = []
        
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('SCORE:'):
                score_text = line.replace('SCORE:', '').strip()
                try:
                    score = float(score_text)
                    score = max(0.0, min(1.0, score))  # Clamp to [0,1]
                except ValueError:
                    score = 0.0
                    
            elif line.startswith('EXPLANATION:'):
                explanation = line.replace('EXPLANATION:', '').strip()
                
            elif line.startswith('KEY_MATCHES:'):
                matches_text = line.replace('KEY_MATCHES:', '').strip()
                key_matches = [match.strip() for match in matches_text.split(',') if match.strip()]
        
        return score, explanation, key_matches
    
    def _fallback_score_market(
        self,
        tweet_text: str,
        search_query: str,
        key_topics: List[str],
        market: Dict[str, Any]
    ) -> MarketRelevanceScore:
        """Fallback scoring when Cohere fails"""
        
        market_id = market.get("id", "")
        market_title = market.get("title", "")
        market_description = market.get("description", "")
        
        # Simple keyword matching
        all_text = f"{market_title} {market_description}".lower()
        tweet_lower = tweet_text.lower()
        query_lower = search_query.lower()
        
        score = 0.0
        matches = []
        
        # Check search query match
        query_words = query_lower.split()
        for word in query_words:
            if word in all_text:
                score += 0.2
                matches.append(word)
        
        # Check key topics
        for topic in key_topics:
            if topic.lower() in all_text:
                score += 0.1
                matches.append(topic)
        
        # Clamp score
        score = min(1.0, score)
        
        return MarketRelevanceScore(
            market_id=market_id,
            market_title=market_title,
            relevance_score=score,
            relevance_explanation=f"Fallback scoring based on keyword matching",
            key_matches=matches[:3],  # Limit to 3
            market_data=market
        )

def format_top_markets_json(
    tweet_text: str,
    sentiment_analysis: Dict[str, Any],
    top_markets: List[MarketRelevanceScore]
) -> Dict[str, Any]:
    """
    Format the top markets into a clean, easy-to-parse JSON structure
    """
    
    formatted_markets = []
    
    for rank, market_score in enumerate(top_markets, 1):
        market = market_score.market_data
        
        # Extract key market information
        market_info = {
            "rank": rank,
            "relevance_score": market_score.relevance_score,
            "relevance_explanation": market_score.relevance_explanation,
            "key_matches": market_score.key_matches,
            
            # Core market data
            "market_id": market.get("id", ""),
            "title": market.get("title", ""),
            "description": market.get("description", "")[:300],  # Truncate for readability
            "slug": market.get("slug", ""),
            
            # Market status
            "active": market.get("active", False),
            "closed": market.get("closed", True),
            "end_date": market.get("endDate", ""),
            
            # Trading data
            "volume_24hr": market.get("volume24hr", 0),
            "liquidity": market.get("liquidity", 0),
            "comment_count": market.get("commentCount", 0),
            
            # Tags
            "tags": [tag.get("label", "") for tag in market.get("tags", [])],
            
            # Individual markets within this event
            "prediction_markets": []
        }
        
        # Extract individual prediction markets
        for sub_market in market.get("markets", []):
            market_info["prediction_markets"].append({
                "question": sub_market.get("question", ""),
                "outcomes": sub_market.get("outcomes", ""),
                "outcome_prices": sub_market.get("outcomePrices", ""),
                "volume": sub_market.get("volume", ""),
                "liquidity": sub_market.get("liquidity", ""),
                "end_date": sub_market.get("endDate", "")
            })
        
        formatted_markets.append(market_info)
    
    # Final JSON structure
    result = {
        "original_tweet": {
            "text": tweet_text,
            "timestamp": "2025-09-14T05:58:02Z"  # Current timestamp
        },
        "sentiment_analysis": sentiment_analysis,
        "ranking_summary": {
            "total_markets_analyzed": len(top_markets),
            "top_markets_returned": len(top_markets),
            "ranking_method": "AI-powered relevance scoring using Cohere"
        },
        "top_relevant_markets": formatted_markets
    }
    
    return result

# Test function
async def test_market_ranking():
    """Test the market ranking functionality"""
    
    print("🧪 Testing Market Relevance Ranking")
    print("=" * 50)
    
    # Mock data for testing
    tweet_text = "Bitcoin will hit $150,000 by end of 2025! 🚀"
    
    sentiment_analysis = {
        "search_query": "Bitcoin price",
        "key_topics": ["Bitcoin", "Cryptocurrency", "Price Prediction"],
        "sentiment_score": 0.8,
        "confidence": 0.8
    }
    
    # This would normally come from the Polymarket API
    # For testing, we'll use a small sample
    sample_markets = [
        {
            "id": "123",
            "title": "Bitcoin to reach $100k in 2025?",
            "description": "Will Bitcoin reach $100,000 by December 31, 2025?",
            "tags": [{"label": "Cryptocurrency"}, {"label": "Bitcoin"}],
            "markets": [{"question": "Will Bitcoin reach $100k in 2025?"}]
        },
        {
            "id": "124", 
            "title": "Fed rate hike in 2025?",
            "description": "Will the Federal Reserve raise rates in 2025?",
            "tags": [{"label": "Fed Rates"}, {"label": "Economics"}],
            "markets": [{"question": "Fed rate hike in 2025?"}]
        }
    ]
    
    ranker = MarketRelevanceRanker()
    
    try:
        top_markets = await ranker.rank_markets(
            tweet_text=tweet_text,
            sentiment_analysis=sentiment_analysis,
            market_results=sample_markets,
            top_n=5
        )
        
        # Format results
        formatted_result = format_top_markets_json(
            tweet_text=tweet_text,
            sentiment_analysis=sentiment_analysis,
            top_markets=top_markets
        )
        
        print("\n📋 FORMATTED RESULTS:")
        print(json.dumps(formatted_result, indent=2))
        
        return formatted_result
        
    except Exception as e:
        print(f"❌ Error in ranking test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_market_ranking())