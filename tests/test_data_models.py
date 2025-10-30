"""Tests for data models."""

from datetime import datetime
import pytest
from pydantic import ValidationError

from src.models.data_models import (
    ResearchDepth,
    ResearchQuery,
    SearchResult,
    WebpageContent,
    Finding,
    ResearchResult,
)


class TestResearchDepth:
    """Test ResearchDepth enum."""
    
    def test_research_depth_values(self):
        """Test research depth enum values."""
        assert ResearchDepth.QUICK == "quick"
        assert ResearchDepth.STANDARD == "standard"
        assert ResearchDepth.COMPREHENSIVE == "comprehensive"


class TestResearchQuery:
    """Test ResearchQuery model."""
    
    def test_research_query_creation(self):
        """Test creating a research query."""
        query = ResearchQuery(
            query="vector databases",
            research_depth=ResearchDepth.STANDARD,
            max_sources=5,
        )
        
        assert query.query == "vector databases"
        assert query.research_depth == ResearchDepth.STANDARD
        assert query.max_sources == 5
    
    def test_research_query_defaults(self):
        """Test default values for research query."""
        query = ResearchQuery(query="test query")
        
        assert query.research_depth == ResearchDepth.STANDARD
        assert query.max_sources == 5
    
    def test_research_query_validation_max_sources(self):
        """Test validation of max_sources field."""
        # Should work
        query = ResearchQuery(query="test", max_sources=10)
        assert query.max_sources == 10
        
        # Should fail - too low
        with pytest.raises(ValidationError):
            ResearchQuery(query="test", max_sources=0)
        
        # Should fail - too high
        with pytest.raises(ValidationError):
            ResearchQuery(query="test", max_sources=100)


class TestSearchResult:
    """Test SearchResult model."""
    
    def test_search_result_creation(self):
        """Test creating a search result."""
        result = SearchResult(
            url="https://example.com",
            title="Test Article",
            snippet="This is a snippet",
            score=0.95,
        )
        
        assert result.url == "https://example.com"
        assert result.title == "Test Article"
        assert result.snippet == "This is a snippet"
        assert result.score == 0.95
    
    def test_search_result_to_dict(self):
        """Test converting search result to dict."""
        result = SearchResult(
            url="https://example.com",
            title="Test",
            snippet="Snippet",
            score=0.9,
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["url"] == "https://example.com"
        assert result_dict["title"] == "Test"
        assert result_dict["snippet"] == "Snippet"
        assert result_dict["score"] == 0.9


class TestWebpageContent:
    """Test WebpageContent model."""
    
    def test_webpage_content_creation(self):
        """Test creating webpage content."""
        content = WebpageContent(
            url="https://example.com",
            title="Test Page",
            content="Page content here",
            author="John Doe",
            published_date="2024-01-15",
        )
        
        assert content.url == "https://example.com"
        assert content.title == "Test Page"
        assert content.content == "Page content here"
        assert content.author == "John Doe"
        assert content.published_date == "2024-01-15"
        assert content.success is True
        assert content.error is None
    
    def test_webpage_content_with_error(self):
        """Test webpage content with error."""
        content = WebpageContent(
            url="https://example.com",
            title="",
            content="",
            success=False,
            error="404 Not Found",
        )
        
        assert content.success is False
        assert content.error == "404 Not Found"
    
    def test_webpage_content_to_dict(self):
        """Test converting webpage content to dict."""
        content = WebpageContent(
            url="https://example.com",
            title="Test",
            content="Content",
        )
        
        content_dict = content.to_dict()
        
        assert content_dict["url"] == "https://example.com"
        assert content_dict["title"] == "Test"
        assert content_dict["content"] == "Content"
        assert content_dict["success"] is True
        assert "extracted_at" in content_dict


class TestFinding:
    """Test Finding model."""
    
    def test_finding_creation(self):
        """Test creating a finding."""
        finding = Finding(
            claim="Vector databases are fast",
            evidence="According to benchmarks...",
            source_urls=["https://example.com/1", "https://example.com/2"],
            confidence=0.9,
        )
        
        assert finding.claim == "Vector databases are fast"
        assert finding.evidence == "According to benchmarks..."
        assert len(finding.source_urls) == 2
        assert finding.confidence == 0.9
    
    def test_finding_confidence_validation(self):
        """Test confidence field validation."""
        # Should work
        finding = Finding(
            claim="test",
            evidence="test",
            source_urls=[],
            confidence=0.5,
        )
        assert finding.confidence == 0.5
        
        # Should fail - too low
        with pytest.raises(ValidationError):
            Finding(
                claim="test",
                evidence="test",
                source_urls=[],
                confidence=-0.1,
            )
        
        # Should fail - too high
        with pytest.raises(ValidationError):
            Finding(
                claim="test",
                evidence="test",
                source_urls=[],
                confidence=1.5,
            )


class TestResearchResult:
    """Test ResearchResult model."""
    
    def test_research_result_creation(self):
        """Test creating a research result."""
        result = ResearchResult(
            query="test query",
            summary="This is the summary",
            research_depth=ResearchDepth.STANDARD,
            sources_consulted=["https://example.com/1"],
        )
        
        assert result.query == "test query"
        assert result.summary == "This is the summary"
        assert result.research_depth == ResearchDepth.STANDARD
        assert len(result.sources_consulted) == 1
        assert isinstance(result.timestamp, datetime)
    
    def test_research_result_with_findings(self):
        """Test research result with findings."""
        finding = Finding(
            claim="Test claim",
            evidence="Test evidence",
            source_urls=["https://example.com"],
        )
        
        result = ResearchResult(
            query="test",
            summary="summary",
            research_depth=ResearchDepth.QUICK,
            key_findings=[finding],
        )
        
        assert len(result.key_findings) == 1
        assert result.key_findings[0].claim == "Test claim"
    
    def test_research_result_to_dict(self):
        """Test converting research result to dict."""
        result = ResearchResult(
            query="test query",
            summary="summary",
            research_depth=ResearchDepth.STANDARD,
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["query"] == "test query"
        assert result_dict["summary"] == "summary"
        assert result_dict["research_depth"] == "standard"
        assert "timestamp" in result_dict

