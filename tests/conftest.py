"""Pytest fixtures and configuration for tests."""

import os
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch
import pytest

from src.utils.config import Config
from src.models.data_models import SearchResult, WebpageContent


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return Config(
        openai_api_key="test-openai-key",
        tavily_api_key="test-tavily-key",
        agent_model="gpt-4-turbo",
        agent_temperature=0.3,
        max_search_results=5,
        request_timeout=30,
    )


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        SearchResult(
            url="https://example.com/article1",
            title="Introduction to Vector Databases",
            snippet="Vector databases are specialized databases...",
            score=0.95,
        ),
        SearchResult(
            url="https://example.com/article2",
            title="RAG Applications Guide",
            snippet="Retrieval Augmented Generation uses...",
            score=0.88,
        ),
        SearchResult(
            url="https://example.com/article3",
            title="Comparing Vector DB Solutions",
            snippet="Popular vector databases include...",
            score=0.82,
        ),
    ]


@pytest.fixture
def sample_webpage_content():
    """Sample webpage content for testing."""
    return WebpageContent(
        url="https://example.com/article1",
        title="Introduction to Vector Databases",
        content="This is a comprehensive guide to vector databases...",
        author="Jane Doe",
        published_date="2024-01-15",
        success=True,
    )


@pytest.fixture
def mock_tavily_client(sample_search_results):
    """Mock Tavily client for testing."""
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
    return mock_client


@pytest.fixture
def mock_runner():
    """Mock agents.Runner for testing."""
    with patch('agents.Runner') as mock:
        # Create a mock result object
        mock_result = MagicMock()
        mock_result.final_output = "Here is a summary of the research findings..."
        
        # Configure run_sync to return the mock result
        mock.run_sync.return_value = mock_result
        yield mock


@pytest.fixture
def mock_requests_get(sample_webpage_content):
    """Mock requests.get for webpage fetching."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"""
    <html>
    <head><title>Introduction to Vector Databases</title>
    <meta name="author" content="Jane Doe">
    <meta name="date" content="2024-01-15">
    </head>
    <body>
        <article>
            <h1>Introduction to Vector Databases</h1>
            <p>This is a comprehensive guide to vector databases...</p>
        </article>
    </body>
    </html>
    """
    return mock_response


@pytest.fixture(autouse=True)
def set_test_env_vars():
    """Set test environment variables."""
    os.environ["OPENAI_API_KEY"] = "test-openai-key"
    os.environ["TAVILY_API_KEY"] = "test-tavily-key"
    yield
    # Cleanup
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    if "TAVILY_API_KEY" in os.environ:
        del os.environ["TAVILY_API_KEY"]
