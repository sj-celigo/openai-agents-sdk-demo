"""Tests for web search tool."""

import json
from unittest.mock import MagicMock, patch
import pytest

from src.tools.web_search import _web_search_impl
from src.utils.config import Config


class TestWebSearchTool:
    """Test web_search function tool implementation."""
    
    def test_execute_empty_query(self):
        """Test execution with empty query."""
        result_json = _web_search_impl(query="")
        result = json.loads(result_json)
        
        assert result["success"] is False
        assert "empty" in result["error"].lower()
        assert result["results"] == []
    
    def test_execute_whitespace_query(self):
        """Test execution with whitespace-only query."""
        result_json = _web_search_impl(query="   ")
        result = json.loads(result_json)
        
        assert result["success"] is False
        assert result["results"] == []
