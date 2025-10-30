"""Tests for citation management."""

from datetime import datetime
import pytest

from src.utils.citation import Citation, CitationManager


class TestCitation:
    """Test Citation class."""
    
    def test_citation_creation(self):
        """Test creating a citation."""
        citation = Citation(
            url="https://example.com/article",
            title="Test Article",
            snippet="This is a test snippet",
            author="John Doe",
            published_date="2024-01-15",
        )
        
        assert citation.url == "https://example.com/article"
        assert citation.title == "Test Article"
        assert citation.snippet == "This is a test snippet"
        assert citation.author == "John Doe"
        assert citation.published_date == "2024-01-15"
        assert isinstance(citation.accessed_date, datetime)
    
    def test_citation_format(self):
        """Test formatting a citation."""
        citation = Citation(
            url="https://example.com/article",
            title="Test Article",
            author="John Doe",
        )
        
        formatted = citation.format_citation(1)
        
        assert "[1]" in formatted
        assert "Test Article" in formatted
        assert "by John Doe" in formatted
        assert "https://example.com/article" in formatted
        assert "Accessed:" in formatted
    
    def test_citation_format_without_author(self):
        """Test formatting citation without author."""
        citation = Citation(
            url="https://example.com/article",
            title="Test Article",
        )
        
        formatted = citation.format_citation(2)
        
        assert "[2]" in formatted
        assert "Test Article" in formatted
        assert "by" not in formatted
        assert "https://example.com/article" in formatted


class TestCitationManager:
    """Test CitationManager class."""
    
    def test_add_citation(self):
        """Test adding a citation."""
        manager = CitationManager()
        citation = Citation(
            url="https://example.com/article1",
            title="Article 1",
        )
        
        index = manager.add_citation(citation)
        
        assert index == 1
        assert manager.count() == 1
    
    def test_add_multiple_citations(self):
        """Test adding multiple citations."""
        manager = CitationManager()
        
        citation1 = Citation(url="https://example.com/1", title="Article 1")
        citation2 = Citation(url="https://example.com/2", title="Article 2")
        citation3 = Citation(url="https://example.com/3", title="Article 3")
        
        index1 = manager.add_citation(citation1)
        index2 = manager.add_citation(citation2)
        index3 = manager.add_citation(citation3)
        
        assert index1 == 1
        assert index2 == 2
        assert index3 == 3
        assert manager.count() == 3
    
    def test_add_duplicate_citation(self):
        """Test adding a duplicate citation returns existing index."""
        manager = CitationManager()
        
        citation1 = Citation(url="https://example.com/article", title="Article")
        citation2 = Citation(url="https://example.com/article", title="Same Article")
        
        index1 = manager.add_citation(citation1)
        index2 = manager.add_citation(citation2)
        
        assert index1 == index2
        assert manager.count() == 1
    
    def test_get_citation(self):
        """Test retrieving a citation by index."""
        manager = CitationManager()
        citation = Citation(url="https://example.com/article", title="Article")
        
        index = manager.add_citation(citation)
        retrieved = manager.get_citation(index)
        
        assert retrieved == citation
        assert retrieved.url == citation.url
        assert retrieved.title == citation.title
    
    def test_get_citation_invalid_index(self):
        """Test retrieving citation with invalid index."""
        manager = CitationManager()
        
        assert manager.get_citation(0) is None
        assert manager.get_citation(100) is None
        assert manager.get_citation(-1) is None
    
    def test_format_bibliography_empty(self):
        """Test formatting empty bibliography."""
        manager = CitationManager()
        
        bibliography = manager.format_bibliography()
        
        assert bibliography == ""
    
    def test_format_bibliography(self):
        """Test formatting bibliography with citations."""
        manager = CitationManager()
        
        citation1 = Citation(url="https://example.com/1", title="Article 1")
        citation2 = Citation(url="https://example.com/2", title="Article 2")
        
        manager.add_citation(citation1)
        manager.add_citation(citation2)
        
        bibliography = manager.format_bibliography()
        
        assert "## Sources" in bibliography
        assert "[1]" in bibliography
        assert "[2]" in bibliography
        assert "Article 1" in bibliography
        assert "Article 2" in bibliography
    
    def test_clear_citations(self):
        """Test clearing all citations."""
        manager = CitationManager()
        
        citation1 = Citation(url="https://example.com/1", title="Article 1")
        citation2 = Citation(url="https://example.com/2", title="Article 2")
        
        manager.add_citation(citation1)
        manager.add_citation(citation2)
        assert manager.count() == 2
        
        manager.clear()
        
        assert manager.count() == 0
        assert manager.format_bibliography() == ""
    
    def test_count(self):
        """Test counting citations."""
        manager = CitationManager()
        
        assert manager.count() == 0
        
        manager.add_citation(Citation(url="https://example.com/1", title="A1"))
        assert manager.count() == 1
        
        manager.add_citation(Citation(url="https://example.com/2", title="A2"))
        assert manager.count() == 2
        
        manager.clear()
        assert manager.count() == 0

