"""Citation management for tracking and formatting sources."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class Citation(BaseModel):
    """A citation for a research source."""
    
    url: str
    title: str
    snippet: Optional[str] = None
    accessed_date: datetime = Field(default_factory=datetime.now)
    author: Optional[str] = None
    published_date: Optional[str] = None
    
    def format_citation(self, index: int) -> str:
        """
        Format citation in a readable format.
        
        Args:
            index: Citation number/index
            
        Returns:
            Formatted citation string
        """
        parts = [f"[{index}]", self.title]
        
        if self.author:
            parts.append(f"by {self.author}")
        
        parts.append(f"- {self.url}")
        parts.append(f"(Accessed: {self.accessed_date.strftime('%Y-%m-%d')})")
        
        return " ".join(parts)


class CitationManager:
    """Manages citations for research results."""
    
    def __init__(self):
        """Initialize the citation manager."""
        self.citations: List[Citation] = []
        self._url_to_index: dict[str, int] = {}
    
    def add_citation(self, citation: Citation) -> int:
        """
        Add a citation and return its index.
        
        Args:
            citation: Citation to add
            
        Returns:
            Index of the citation (1-based)
        """
        # Check if citation already exists
        if citation.url in self._url_to_index:
            return self._url_to_index[citation.url]
        
        # Add new citation
        self.citations.append(citation)
        index = len(self.citations)
        self._url_to_index[citation.url] = index
        return index
    
    def get_citation(self, index: int) -> Optional[Citation]:
        """
        Get citation by index.
        
        Args:
            index: Citation index (1-based)
            
        Returns:
            Citation if found, None otherwise
        """
        if 0 < index <= len(self.citations):
            return self.citations[index - 1]
        return None
    
    def format_bibliography(self) -> str:
        """
        Format all citations as a bibliography.
        
        Returns:
            Formatted bibliography string
        """
        if not self.citations:
            return ""
        
        lines = ["## Sources\n"]
        for i, citation in enumerate(self.citations, 1):
            lines.append(citation.format_citation(i))
        
        return "\n".join(lines)
    
    def clear(self) -> None:
        """Clear all citations."""
        self.citations = []
        self._url_to_index = {}
    
    def count(self) -> int:
        """
        Get the number of citations.
        
        Returns:
            Number of citations
        """
        return len(self.citations)

