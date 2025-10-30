"""Tests for web search tool."""

from unittest.mock import MagicMock, patch
import pytest

from src.tools.web_search import WebSearchTool
from src.utils.config import Config


class TestWebSearchTool:
    """Test WebSearchTool class."""
    
    def test_tool_name(self, mock_config):
        """Test tool name property."""
        tool = WebSearchTool(mock_config)
        assert tool.name == "web_search"
    
    def test_tool_description(self, mock_config):
        """Test tool description property."""
        tool = WebSearchTool(mock_config)
        assert "search" in tool.description.lower()
        assert "web" in tool.description.lower()
    
    def test_get_parameters_schema(self, mock_config):
        """Test getting parameters schema."""
        tool = WebSearchTool(mock_config)
        schema = tool.get_parameters_schema()
        
        assert schema["type"] == "object"
        assert "query" in schema["properties"]
        assert "max_results" in schema["properties"]
        assert "query" in schema["required"]
    
    def test_get_schema(self, mock_config):
        """Test getting full tool schema."""
        tool = WebSearchTool(mock_config)
        schema = tool.get_schema()
        
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "web_search"
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]
    
    @patch("src.tools.web_search.TavilyClient")
    def test_execute_success(self, mock_tavily_class, mock_config, sample_search_results):
        """Test successful search execution."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {
                    "url": r.url,
                    "title": r.title,
                    "content": r.snippet,
                    "score": r.score,
                }
                for r in sample_search_results
            ]
        }
        mock_tavily_class.return_value = mock_client
        
        tool = WebSearchTool(mock_config)
        result = tool.execute(query="test query", max_results=5)
        
        assert result["success"] is True
        assert result["query"] == "test query"
        assert len(result["results"]) == 3
        assert result["count"] == 3
        
        # Verify API was called correctly
        mock_client.search.assert_called_once()
        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs["query"] == "test query"
        assert call_kwargs["max_results"] == 5
    
    @patch("src.tools.web_search.TavilyClient")
    def test_execute_empty_query(self, mock_tavily_class, mock_config):
        """Test execution with empty query."""
        mock_client = MagicMock()
        mock_tavily_class.return_value = mock_client
        
        tool = WebSearchTool(mock_config)
        result = tool.execute(query="")
        
        assert result["success"] is False
        assert "empty" in result["error"].lower()
        assert result["results"] == []
        
        # Should not call API
        mock_client.search.assert_not_called()
    
    @patch("src.tools.web_search.TavilyClient")
    def test_execute_whitespace_query(self, mock_tavily_class, mock_config):
        """Test execution with whitespace-only query."""
        mock_client = MagicMock()
        mock_tavily_class.return_value = mock_client
        
        tool = WebSearchTool(mock_config)
        result = tool.execute(query="   ")
        
        assert result["success"] is False
        assert result["results"] == []
    
    @patch("src.tools.web_search.TavilyClient")
    def test_execute_api_error(self, mock_tavily_class, mock_config):
        """Test execution when API raises error."""
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("API Error")
        mock_tavily_class.return_value = mock_client
        
        tool = WebSearchTool(mock_config)
        result = tool.execute(query="test query")
        
        assert result["success"] is False
        assert "API Error" in result["error"]
        assert result["results"] == []
    
    @patch("src.tools.web_search.TavilyClient")
    def test_execute_default_max_results(self, mock_tavily_class, mock_config):
        """Test execution uses default max_results from config."""
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": []}
        mock_tavily_class.return_value = mock_client
        
        tool = WebSearchTool(mock_config)
        tool.execute(query="test query")
        
        # Should use config default
        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs["max_results"] == mock_config.max_search_results
    
    @patch("src.tools.web_search.TavilyClient")
    def test_execute_custom_max_results(self, mock_tavily_class, mock_config):
        """Test execution with custom max_results."""
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": []}
        mock_tavily_class.return_value = mock_client
        
        tool = WebSearchTool(mock_config)
        tool.execute(query="test query", max_results=10)
        
        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs["max_results"] == 10
    
    @patch("src.tools.web_search.TavilyClient")
    def test_execute_empty_results(self, mock_tavily_class, mock_config):
        """Test execution when API returns no results."""
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": []}
        mock_tavily_class.return_value = mock_client
        
        tool = WebSearchTool(mock_config)
        result = tool.execute(query="obscure query")
        
        assert result["success"] is True
        assert result["results"] == []
        assert result["count"] == 0

