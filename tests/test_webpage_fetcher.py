"""Tests for webpage fetcher tool."""

import json
from unittest.mock import MagicMock, patch
import pytest
import requests

from src.tools.webpage_fetcher import (_fetch_webpage_impl, init_webpage_fetcher_tool, 
                                        set_citation_manager)
import src.tools.webpage_fetcher as webpage_fetcher_module
from src.utils.config import Config
from src.utils.citation import CitationManager


class TestWebpageFetcherTool:
    """Test fetch_webpage function tool."""
    
    @patch.object(webpage_fetcher_module, '_session')
    @patch.object(webpage_fetcher_module, '_config')
    def test_execute_success(self, mock_config_global, mock_session_global, mock_config):
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
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        
        webpage_fetcher_module._session = mock_session
        webpage_fetcher_module._config = mock_config
        
        result_json = _fetch_webpage_impl(url="https://example.com/article")
        result = json.loads(result_json)
        
        assert result["success"] is True
        assert result["url"] == "https://example.com/article"
        assert result["title"] == "Test Page"
        assert "test content" in result["content"].lower()
        assert result["author"] == "John Doe"
        assert result["published_date"] == "2024-01-15"
    
    def test_execute_empty_url(self):
        """Test execution with empty URL."""
        result_json = _fetch_webpage_impl(url="")
        result = json.loads(result_json)
        
        assert result["success"] is False
        assert "empty" in result["error"].lower()
    
    @patch.object(webpage_fetcher_module, '_session')
    @patch.object(webpage_fetcher_module, '_config')
    def test_execute_timeout(self, mock_config_global, mock_session_global, mock_config):
        """Test execution when request times out."""
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.Timeout()
        
        webpage_fetcher_module._session = mock_session
        webpage_fetcher_module._config = mock_config
        
        result_json = _fetch_webpage_impl(url="https://example.com")
        result = json.loads(result_json)
        
        assert result["success"] is False
        assert "timeout" in result["error"].lower()
        assert result["url"] == "https://example.com"
    
    @patch.object(webpage_fetcher_module, '_session')
    @patch.object(webpage_fetcher_module, '_config')
    def test_execute_http_error(self, mock_config_global, mock_session_global, mock_config):
        """Test execution when HTTP error occurs."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        
        webpage_fetcher_module._session = mock_session
        webpage_fetcher_module._config = mock_config
        
        result_json = _fetch_webpage_impl(url="https://example.com/notfound")
        result = json.loads(result_json)
        
        assert result["success"] is False
        assert "404" in result["error"]
        assert result["url"] == "https://example.com/notfound"
    
    @patch.object(webpage_fetcher_module, '_session')
    @patch.object(webpage_fetcher_module, '_config')
    def test_execute_general_error(self, mock_config_global, mock_session_global, mock_config):
        """Test execution when general error occurs."""
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Network error")
        
        webpage_fetcher_module._session = mock_session
        webpage_fetcher_module._config = mock_config
        
        result_json = _fetch_webpage_impl(url="https://example.com")
        result = json.loads(result_json)
        
        assert result["success"] is False
        assert "Network error" in result["error"]
    
    @patch.object(webpage_fetcher_module, '_session')
    @patch.object(webpage_fetcher_module, '_config')
    def test_content_extraction_removes_scripts(self, mock_config_global, mock_session_global, mock_config):
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
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        
        webpage_fetcher_module._session = mock_session
        webpage_fetcher_module._config = mock_config
        
        result_json = _fetch_webpage_impl(url="https://example.com")
        result = json.loads(result_json)
        
        assert "alert" not in result["content"]
        assert "color: red" not in result["content"]
        assert "Main content here" in result["content"]
    
    @patch.object(webpage_fetcher_module, '_session')
    @patch.object(webpage_fetcher_module, '_config')
    def test_content_length_limit(self, mock_config_global, mock_session_global, mock_config):
        """Test that content is limited to 5000 characters."""
        long_content = "A" * 10000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = f"""
        <html>
        <body><article><p>{long_content}</p></article></body>
        </html>
        """.encode()
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        
        webpage_fetcher_module._session = mock_session
        webpage_fetcher_module._config = mock_config
        
        result_json = _fetch_webpage_impl(url="https://example.com")
        result = json.loads(result_json)
        
        # Content should be truncated
        assert len(result["content"]) <= 5003  # 5000 + "..."
        assert result["content"].endswith("...")
    
    @patch.object(webpage_fetcher_module, '_session')
    @patch.object(webpage_fetcher_module, '_config')
    @patch.object(webpage_fetcher_module, '_citation_manager')
    def test_citation_tracking(self, mock_citation_global, mock_config_global, mock_session_global, mock_config):
        """Test that citations are tracked when citation manager is set."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
        <head><title>Test</title></head>
        <body><p>Content</p></body>
        </html>
        """
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        
        citation_manager = CitationManager()
        
        webpage_fetcher_module._session = mock_session
        webpage_fetcher_module._config = mock_config
        webpage_fetcher_module._citation_manager = citation_manager
        
        _fetch_webpage_impl(url="https://example.com")
        
        # Check that citation was added
        assert citation_manager.count() == 1
        citation = citation_manager.get_citation(1)
        assert citation.url == "https://example.com"
    
    def test_init_webpage_fetcher_tool(self, mock_config):
        """Test initialization of webpage fetcher tool."""
        init_webpage_fetcher_tool(mock_config)
        
        # Check that globals were set
        assert webpage_fetcher_module._config is not None
        assert webpage_fetcher_module._session is not None
    
    def test_set_citation_manager(self):
        """Test setting citation manager."""
        citation_manager = CitationManager()
        set_citation_manager(citation_manager)
        
        assert webpage_fetcher_module._citation_manager is citation_manager
