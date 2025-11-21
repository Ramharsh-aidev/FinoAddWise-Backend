from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # API Keys
    openai_api_key: str
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "financial-advisor-index"
    
    # Database
    database_url: str = "sqlite:///./financial_advisor.db"
    
    # Application
    app_name: str = "Financial Advisor"
    debug: bool = True
    host: str = "0.0.0.0" 
    port: int = 8000
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_tokens: int = 4000
    temperature: float = 0.1
    
    # Compliance thresholds
    compliance_threshold: float = 0.85
    risk_score_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()