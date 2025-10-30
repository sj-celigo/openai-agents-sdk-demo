"""Tests for webpage fetcher tool."""

from unittest.mock import MagicMock, patch
import pytest
import requests

from src.tools.webpage_fetcher import WebpageFetcherTool
from src.utils.config import Config


class TestWebpageFetcherTool:
    """Test WebpageFetcherTool class."""
    
    def test_tool_name(self, mock_config):
        """Test tool name property."""
        tool = WebpageFetcherTool(mock_config)
        assert tool.name == "fetch_webpage"
    
    def test_tool_description(self, mock_config):
        """Test tool description property."""
        tool = WebpageFetcherTool(mock_config)
        assert "fetch" in tool.description.lower()
        assert "webpage" in tool.description.lower()
    
    def test_get_parameters_schema(self, mock_config):
        """Test getting parameters schema."""
        tool = WebpageFetcherTool(mock_config)
        schema = tool.get_parameters_schema()
        
        assert schema["type"] == "object"
        assert "url" in schema["properties"]
        assert "url" in schema["required"]
    
    def test_get_schema(self, mock_config):
        """Test getting full tool schema."""
        tool = WebpageFetcherTool(mock_config)
        schema = tool.get_schema()
        
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "fetch_webpage"
        assert "description" in schema["function"]
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_execute_success(self, mock_get, mock_config):
        """Test successful webpage fetch."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
        <head>
            <title>Test Page</title>
            <meta name="author" content="John Doe">
            <meta name="date" content="2024-01-15">
        </head>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>This is test content.</p>
            </article>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="https://example.com/article")
        
        assert result["success"] is True
        assert result["url"] == "https://example.com/article"
        assert result["title"] == "Test Page"
        assert "test content" in result["content"].lower()
        assert result["author"] == "John Doe"
        assert result["published_date"] == "2024-01-15"
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_execute_empty_url(self, mock_get, mock_config):
        """Test execution with empty URL."""
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="")
        
        assert result["success"] is False
        assert "empty" in result["error"].lower()
        mock_get.assert_not_called()
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_execute_timeout(self, mock_get, mock_config):
        """Test execution when request times out."""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="https://example.com")
        
        assert result["success"] is False
        assert "timeout" in result["error"].lower()
        assert result["url"] == "https://example.com"
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_execute_http_error(self, mock_get, mock_config):
        """Test execution when HTTP error occurs."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="https://example.com/notfound")
        
        assert result["success"] is False
        assert "404" in result["error"]
        assert result["url"] == "https://example.com/notfound"
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_execute_general_error(self, mock_get, mock_config):
        """Test execution when general error occurs."""
        mock_get.side_effect = Exception("Network error")
        
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="https://example.com")
        
        assert result["success"] is False
        assert "Network error" in result["error"]
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_extract_title_from_h1(self, mock_get, mock_config):
        """Test extracting title from h1 when no title tag."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
        <body>
            <h1>Article Title</h1>
            <p>Content</p>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="https://example.com")
        
        assert result["title"] == "Article Title"
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_extract_title_fallback(self, mock_get, mock_config):
        """Test fallback title when no title found."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html><body><p>Content</p></body></html>
        """
        mock_get.return_value = mock_response
        
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="https://example.com")
        
        assert result["title"] == "Untitled"
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_content_extraction_removes_scripts(self, mock_get, mock_config):
        """Test that scripts and styles are removed from content."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
        <head><title>Test</title></head>
        <body>
            <script>alert('test');</script>
            <style>.test { color: red; }</style>
            <article>
                <p>Main content here</p>
            </article>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="https://example.com")
        
        assert "alert" not in result["content"]
        assert "color: red" not in result["content"]
        assert "Main content here" in result["content"]
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_content_length_limit(self, mock_get, mock_config):
        """Test that content is limited to 5000 characters."""
        long_content = "A" * 10000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = f"""
        <html>
        <body><article><p>{long_content}</p></article></body>
        </html>
        """.encode()
        mock_get.return_value = mock_response
        
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="https://example.com")
        
        # Content should be truncated
        assert len(result["content"]) <= 5003  # 5000 + "..."
        assert result["content"].endswith("...")
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_extract_author_from_schema(self, mock_get, mock_config):
        """Test extracting author from schema.org markup."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
        <body>
            <span itemprop="author">Jane Smith</span>
            <p>Content</p>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="https://example.com")
        
        assert result["author"] == "Jane Smith"
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_extract_published_date_from_time_tag(self, mock_get, mock_config):
        """Test extracting published date from time tag."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
        <body>
            <time datetime="2024-01-20">January 20, 2024</time>
            <p>Content</p>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        tool = WebpageFetcherTool(mock_config)
        result = tool.execute(url="https://example.com")
        
        assert result["published_date"] == "2024-01-20"
    
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_session_has_user_agent(self, mock_get, mock_config):
        """Test that session has user agent header."""
        tool = WebpageFetcherTool(mock_config)
        
        assert "User-Agent" in tool.session.headers
        assert tool.session.headers["User-Agent"] == mock_config.user_agent

