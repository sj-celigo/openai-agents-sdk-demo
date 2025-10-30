"""Web search tool using Tavily API with OpenAI Agents SDK."""

import json
import logging
from typing import Optional
from tavily import TavilyClient
from agents import function_tool

from ..models.data_models import SearchResult
from ..utils.config import Config

logger = logging.getLogger(__name__)

# Global reference to config and client (will be set by init function)
_config: Optional[Config] = None
_tavily_client: Optional[TavilyClient] = None


def init_web_search_tool(config: Config):
    """Initialize the web search tool with configuration."""
    global _config, _tavily_client
    _config = config
    _tavily_client = TavilyClient(api_key=config.tavily_api_key)


def _web_search_impl(query: str, max_results: int = 5) -> str:
    """
    Implementation of web search (not decorated, for testing).
    
    Args:
        query: The search query to execute
        max_results: Maximum number of results to return
        
    Returns:
        JSON string with search results
    """
    if not query or not query.strip():
        return json.dumps({
            "success": False,
            "error": "Query cannot be empty",
            "results": []
        })
    
    # Use global config if available, otherwise use defaults
    if _config:
        max_results = max_results or _config.max_search_results
    
    try:
        logger.info(f"Executing web search for: {query}")
        
        # Get or create client
        client = _tavily_client
        if not client:
            # Fallback: create client if not initialized
            from ..utils.config import get_config
            config = get_config()
            client = TavilyClient(api_key=config.tavily_api_key)
        
        # Execute Tavily search
        response = client.search(
            query=query,
            max_results=min(max(1, max_results), 10),  # Clamp between 1 and 10
            search_depth="basic",
            include_answer=False,
        )
        
        # Parse results
        results = []
        for item in response.get("results", []):
            result = SearchResult(
                url=item.get("url", ""),
                title=item.get("title", ""),
                snippet=item.get("content", ""),
                score=item.get("score"),
            )
            results.append(result)
        
        logger.info(f"Found {len(results)} results")
        
        return json.dumps({
            "success": True,
            "query": query,
            "results": [r.to_dict() for r in results],
            "count": len(results),
        })
        
    except Exception as e:
        logger.error(f"Web search failed: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "results": [],
        })


@function_tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for information on a given query.
    
    Returns a list of relevant web pages with titles, URLs, and snippets.
    Use this to gather information from across the internet.
    
    Args:
        query: The search query to execute
        max_results: Maximum number of results to return (default: 5, min: 1, max: 10)
        
    Returns:
        JSON string with search results containing success status, query, results list, and count
    """
    return _web_search_impl(query, max_results)
