"""Web search tool using Tavily API."""

import logging
from typing import Any, Dict, List, Optional
from tavily import TavilyClient

from .base import BaseTool
from ..models.data_models import SearchResult
from ..utils.config import Config

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """Tool for searching the web using Tavily API."""
    
    def __init__(self, config: Config):
        """
        Initialize the web search tool.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.client = TavilyClient(api_key=config.tavily_api_key)
    
    @property
    def name(self) -> str:
        """Tool name."""
        return "web_search"
    
    @property
    def description(self) -> str:
        """Tool description."""
        return (
            "Search the web for information on a given query. "
            "Returns a list of relevant web pages with titles, URLs, and snippets. "
            "Use this to gather information from across the internet."
        )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get parameters schema."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10,
                },
            },
            "required": ["query"],
        }
    
    def execute(
        self,
        query: str,
        max_results: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute web search.
        
        Args:
            query: Search query
            max_results: Maximum number of results (optional)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with search results
        """
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty",
                "results": []
            }
        
        max_results = max_results or self.config.max_search_results
        
        try:
            logger.info(f"Executing web search for: {query}")
            
            # Execute Tavily search
            response = self.client.search(
                query=query,
                max_results=max_results,
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
            
            return {
                "success": True,
                "query": query,
                "results": [r.to_dict() for r in results],
                "count": len(results),
            }
            
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
            }

