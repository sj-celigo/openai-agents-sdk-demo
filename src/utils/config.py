"""Configuration management for the research assistant."""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config(BaseModel):
    """Application configuration."""
    
    # API Keys
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    tavily_api_key: str = Field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    
    # Agent settings
    agent_model: str = Field(default_factory=lambda: os.getenv("AGENT_MODEL", "gpt-4-turbo"))
    agent_temperature: float = Field(default_factory=lambda: float(os.getenv("AGENT_TEMPERATURE", "0.3")))
    
    # Search settings
    max_search_results: int = Field(default_factory=lambda: int(os.getenv("MAX_SEARCH_RESULTS", "5")))
    request_timeout: int = Field(default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", "30")))
    
    # User agent for web requests
    user_agent: str = "Mozilla/5.0 (compatible; ResearchAssistant/1.0)"
    
    def validate_required_keys(self) -> None:
        """Validate that required API keys are present."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required")
    
    class Config:
        """Pydantic config."""
        frozen = True


def get_config() -> Config:
    """Get application configuration."""
    config = Config()
    config.validate_required_keys()
    return config

