"""
Configuration module for the Tweet-Market Analysis Pipeline
"""
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator

# Load environment variables
load_dotenv()

class PipelineConfig(BaseModel):
    """Pipeline configuration settings"""
    
    # Cohere API settings
    cohere_api_key: str
    cohere_model: str = "command-r-plus"
    
    # Polymarket API settings
    polymarket_base_url: str = "https://gamma-api.polymarket.com"
    
    # Pipeline settings
    max_markets_to_fetch: int = 50
    top_markets_count: int = 5
    request_timeout: int = 30
    rate_limit_delay: float = 0.1
    
    # Sentiment extraction settings
    sentiment_max_tokens: int = 50
    sentiment_temperature: float = 0.3
    
    # Market relevance settings
    relevance_max_tokens: int = 200
    relevance_temperature: float = 0.2
    
    @field_validator('cohere_api_key')
    @classmethod
    def validate_cohere_api_key(cls, v):
        if not v or v == "your_cohere_api_key_here":
            raise ValueError("COHERE_API_KEY must be set in environment or .env file")
        return v
    
    @field_validator('top_markets_count')
    @classmethod
    def validate_top_markets_count(cls, v):
        if v < 1 or v > 10:
            raise ValueError("top_markets_count must be between 1 and 10")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global configuration instance
config = PipelineConfig(
    cohere_api_key=os.getenv("COHERE_API_KEY", ""),
    polymarket_base_url=os.getenv("POLYMARKET_BASE_URL", "https://gamma-api.polymarket.com"),
    max_markets_to_fetch=int(os.getenv("MAX_MARKETS_TO_FETCH", "50")),
    top_markets_count=int(os.getenv("TOP_MARKETS_COUNT", "5")),
    request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
    rate_limit_delay=float(os.getenv("RATE_LIMIT_DELAY", "0.1"))
)