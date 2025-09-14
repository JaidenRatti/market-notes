"""
Tweet Sentiment Extraction Module using Cohere AI
Analyzes tweet text to extract key themes and generate search queries for Polymarket
"""
import re
import asyncio
from typing import List, Optional, Dict, Any
import cohere

from .models import TweetInput, SentimentAnalysis
from .config import config


class SentimentExtractor:
    """
    Extracts sentiment, key themes, and generates search queries from tweet text using Cohere
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the sentiment extractor with Cohere client"""
        self.api_key = api_key or config.cohere_api_key
        self.client = cohere.Client(self.api_key)
        self.model = config.cohere_model
        
    async def extract_sentiment(self, tweet: TweetInput) -> SentimentAnalysis:
        """
        Extract sentiment and generate search query from tweet text
        
        Args:
            tweet: TweetInput object containing tweet data
            
        Returns:
            SentimentAnalysis object with search query and extracted themes
        """
        try:
            # Clean and preprocess tweet text
            cleaned_text = self._preprocess_tweet_text(tweet.text)
            
            # Generate search query using Cohere
            search_query = await self._generate_search_query(cleaned_text)
            
            # Extract key topics
            key_topics = await self._extract_key_topics(cleaned_text)
            
            # Calculate sentiment score (optional)
            sentiment_score = await self._calculate_sentiment_score(cleaned_text)
            
            return SentimentAnalysis(
                search_query=search_query,
                key_topics=key_topics,
                sentiment_score=sentiment_score,
                confidence=0.8  # Default confidence, could be enhanced
            )
            
        except Exception as e:
            # Fallback to basic keyword extraction if Cohere fails
            return self._fallback_analysis(tweet.text, str(e))
    
    async def _generate_search_query(self, text: str) -> str:
        """
        Generate a concise search query optimized for Polymarket's search endpoint
        """
        prompt = f"""
Analyze this tweet and extract the core predictable events, topics, or outcomes that could be found on Polymarket (a prediction market).

Tweet: "{text}"

Generate a concise search query (1-5 words) that would find relevant prediction markets. Focus on:
- Political events, elections, policy outcomes
- Economic indicators, market movements, company performance  
- Sports events, entertainment awards, technology releases
- Cryptocurrency, AI developments, social trends
- Weather, natural disasters, global events

Return ONLY the search query, nothing else. Make it specific enough to find relevant markets but broad enough to catch variations.

Examples:
- "Bitcoin price 2024" → "Bitcoin"
- "Who will win the election?" → "election 2024" 
- "Tesla stock going up!" → "Tesla stock"
- "Fed will cut rates soon" → "Fed rates"

Search query:"""

        try:
            response = self.client.chat(
                message=prompt,
                model=self.model,
                max_tokens=config.sentiment_max_tokens,
                temperature=config.sentiment_temperature,
                connectors=[]
            )
            
            search_query = response.text.strip()
            
            # Clean up the response to ensure it's just the query
            search_query = self._clean_search_query(search_query)
            
            return search_query or self._extract_fallback_keywords(text)
            
        except Exception as e:
            print(f"Error generating search query with Cohere: {e}")
            return self._extract_fallback_keywords(text)
    
    async def _extract_key_topics(self, text: str) -> List[str]:
        """
        Extract key topics and themes from the tweet
        """
        prompt = f"""
Extract 3-5 key topics from this tweet that relate to predictable future events or market outcomes:

Tweet: "{text}"

Focus on topics that could have prediction markets, such as:
- Political figures, parties, elections
- Companies, stocks, economic indicators
- Sports teams, players, events
- Technology products, releases, adoption
- Cryptocurrencies, financial instruments
- Entertainment, awards, cultural events

Return topics as a simple comma-separated list, nothing else.

Example: "Bitcoin, Federal Reserve, inflation, 2024 election"

Topics:"""

        try:
            response = self.client.chat(
                message=prompt,
                model=self.model,
                max_tokens=config.sentiment_max_tokens,
                temperature=config.sentiment_temperature,
                connectors=[]
            )
            
            topics_text = response.text.strip()
            
            # Parse comma-separated topics
            topics = [topic.strip() for topic in topics_text.split(',')]
            topics = [topic for topic in topics if topic and len(topic) > 1]
            
            return topics[:5]  # Limit to 5 topics max
            
        except Exception as e:
            print(f"Error extracting topics with Cohere: {e}")
            return self._extract_fallback_topics(text)
    
    async def _calculate_sentiment_score(self, text: str) -> Optional[float]:
        """
        Calculate sentiment score (positive/negative) for the tweet
        Optional feature - could be used for market direction bias
        """
        prompt = f"""
Analyze the sentiment of this tweet on a scale from -1.0 (very negative) to 1.0 (very positive), with 0.0 being neutral.

Tweet: "{text}"

Consider:
- Market optimism/pessimism
- Bullish/bearish sentiment
- Positive/negative predictions
- Confidence/uncertainty

Return only a single number between -1.0 and 1.0:"""

        try:
            response = self.client.chat(
                message=prompt,
                model=self.model,
                max_tokens=10,
                temperature=0.1,
                connectors=[]
            )
            
            sentiment_text = response.text.strip()
            
            # Extract numeric value
            import re
            numbers = re.findall(r'-?\d+\.?\d*', sentiment_text)
            if numbers:
                score = float(numbers[0])
                return max(-1.0, min(1.0, score))  # Clamp to [-1, 1]
            
            return None
            
        except Exception as e:
            print(f"Error calculating sentiment with Cohere: {e}")
            return None
    
    def _preprocess_tweet_text(self, text: str) -> str:
        """
        Clean and preprocess tweet text for analysis
        """
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove mentions and hashtags for cleaner analysis (but keep the content)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#(\w+)', r'\1', text)  # Keep hashtag content, remove #
        
        # Remove extra punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    def _clean_search_query(self, query: str) -> str:
        """
        Clean up the generated search query
        """
        # Remove quotes and extra formatting
        query = re.sub(r'["\']', '', query)
        
        # Remove any explanatory text that might have leaked through
        query = re.sub(r'^(search query|query):\s*', '', query, flags=re.IGNORECASE)
        
        # Limit length
        words = query.split()
        if len(words) > 5:
            query = ' '.join(words[:5])
        
        return query.strip()
    
    def _extract_fallback_keywords(self, text: str) -> str:
        """
        Fallback method to extract keywords if Cohere fails
        """
        # Common prediction market topics
        market_keywords = [
            'bitcoin', 'btc', 'ethereum', 'crypto', 'election', 'trump', 'biden', 
            'tesla', 'apple', 'stock', 'fed', 'rates', 'inflation', 'gdp',
            'super bowl', 'world cup', 'olympics', 'ai', 'chatgpt', 'openai'
        ]
        
        text_lower = text.lower()
        found_keywords = [keyword for keyword in market_keywords if keyword in text_lower]
        
        if found_keywords:
            return found_keywords[0]  # Return first match
        
        # Extract capitalized words as potential proper nouns
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        if words:
            return words[0]
        
        # Last resort: extract any meaningful words
        words = re.findall(r'\b\w{4,}\b', text.lower())
        return words[0] if words else "market"
    
    def _extract_fallback_topics(self, text: str) -> List[str]:
        """
        Fallback method to extract topics if Cohere fails
        """
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        
        # Extract mentions
        mentions = re.findall(r'@(\w+)', text)
        
        # Extract capitalized words
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        # Combine and deduplicate
        topics = list(set(hashtags + mentions + proper_nouns))
        
        return topics[:5]
    
    def _fallback_analysis(self, text: str, error: str) -> SentimentAnalysis:
        """
        Fallback analysis when Cohere API fails
        """
        print(f"Using fallback analysis due to error: {error}")
        
        return SentimentAnalysis(
            search_query=self._extract_fallback_keywords(text),
            key_topics=self._extract_fallback_topics(text),
            sentiment_score=None,
            confidence=0.3  # Lower confidence for fallback
        )


# Convenience function for single tweet analysis
async def analyze_tweet_sentiment(tweet_text: str, author: Optional[str] = None) -> SentimentAnalysis:
    """
    Convenience function to analyze a single tweet
    
    Args:
        tweet_text: The tweet text to analyze
        author: Optional tweet author
        
    Returns:
        SentimentAnalysis object
    """
    tweet = TweetInput(text=tweet_text, author=author)
    extractor = SentimentExtractor()
    return await extractor.extract_sentiment(tweet)


# Synchronous wrapper for backwards compatibility
def analyze_tweet_sentiment_sync(tweet_text: str, author: Optional[str] = None) -> SentimentAnalysis:
    """
    Synchronous wrapper for tweet sentiment analysis
    """
    return asyncio.run(analyze_tweet_sentiment(tweet_text, author))