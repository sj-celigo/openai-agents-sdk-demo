"""Pydantic data models for the research assistant."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ResearchDepth(str, Enum):
    """Research depth levels."""
    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class ResearchQuery(BaseModel):
    """A research query from the user."""
    
    query: str = Field(..., description="The research question or topic")
    research_depth: ResearchDepth = Field(
        default=ResearchDepth.STANDARD,
        description="How deep to research"
    )
    max_sources: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of sources to consult"
    )
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class SearchResult(BaseModel):
    """A single search result from a search engine."""
    
    url: str
    title: str
    snippet: str
    score: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet,
            "score": self.score,
        }


class WebpageContent(BaseModel):
    """Extracted content from a webpage."""
    
    url: str
    title: str
    content: str
    author: Optional[str] = None
    published_date: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.now)
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "published_date": self.published_date,
            "extracted_at": self.extracted_at.isoformat(),
            "success": self.success,
            "error": self.error,
        }


class Finding(BaseModel):
    """A key finding from research."""
    
    claim: str
    evidence: str
    source_urls: List[str]
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class ResearchResult(BaseModel):
    """The result of a research query."""
    
    query: str
    summary: str
    key_findings: List[Finding] = Field(default_factory=list)
    sources_consulted: List[str] = Field(default_factory=list)
    research_depth: ResearchDepth
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "summary": self.summary,
            "key_findings": [f.dict() for f in self.key_findings],
            "sources_consulted": self.sources_consulted,
            "research_depth": self.research_depth,
            "timestamp": self.timestamp.isoformat(),
        }

