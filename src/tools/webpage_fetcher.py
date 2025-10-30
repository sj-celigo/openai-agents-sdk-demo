"""Webpage fetching and content extraction tool."""

import logging
from typing import Any, Dict, Optional
import requests
from bs4 import BeautifulSoup

from .base import BaseTool
from ..models.data_models import WebpageContent
from ..utils.config import Config

logger = logging.getLogger(__name__)


class WebpageFetcherTool(BaseTool):
    """Tool for fetching and extracting content from webpages."""
    
    def __init__(self, config: Config):
        """
        Initialize the webpage fetcher tool.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.user_agent,
        })
    
    @property
    def name(self) -> str:
        """Tool name."""
        return "fetch_webpage"
    
    @property
    def description(self) -> str:
        """Tool description."""
        return (
            "Fetch and extract the main content from a webpage. "
            "Given a URL, this tool retrieves the page and extracts "
            "the title and main text content, removing navigation, ads, etc."
        )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get parameters schema."""
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to fetch",
                },
            },
            "required": ["url"],
        }
    
    def execute(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Fetch and extract webpage content.
        
        Args:
            url: URL to fetch
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with extracted content
        """
        if not url or not url.strip():
            return {
                "success": False,
                "error": "URL cannot be empty",
            }
        
        try:
            logger.info(f"Fetching webpage: {url}")
            
            # Fetch the page
            response = self.session.get(
                url,
                timeout=self.config.request_timeout,
                allow_redirects=True,
            )
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, "lxml")
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_content(soup)
            
            # Extract metadata
            author = self._extract_author(soup)
            published_date = self._extract_published_date(soup)
            
            webpage_content = WebpageContent(
                url=url,
                title=title,
                content=content,
                author=author,
                published_date=published_date,
                success=True,
            )
            
            logger.info(f"Successfully extracted content from {url}")
            
            return webpage_content.to_dict()
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
            return {
                "success": False,
                "error": "Request timeout",
                "url": url,
            }
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "url": url,
            }
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try <title> tag first
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Try h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()
        
        return "Untitled"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page."""
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()
        
        # Try to find main content area
        main_content = (
            soup.find("main") or
            soup.find("article") or
            soup.find("div", class_=lambda x: x and "content" in x.lower()) or
            soup.find("body")
        )
        
        if not main_content:
            return ""
        
        # Extract text
        text = main_content.get_text(separator="\n", strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        text = "\n".join(lines)
        
        # Limit length (keep first 5000 characters to avoid token limits)
        if len(text) > 5000:
            text = text[:5000] + "..."
        
        return text
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from metadata."""
        # Try meta tags
        author_meta = soup.find("meta", attrs={"name": "author"})
        if author_meta and author_meta.get("content"):
            return author_meta["content"].strip()
        
        # Try schema.org
        author_span = soup.find("span", attrs={"itemprop": "author"})
        if author_span:
            return author_span.get_text().strip()
        
        return None
    
    def _extract_published_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract published date from metadata."""
        # Try various meta tags
        date_tags = [
            ("property", "article:published_time"),
            ("name", "publishdate"),
            ("name", "date"),
            ("itemprop", "datePublished"),
        ]
        
        for attr_name, attr_value in date_tags:
            meta = soup.find("meta", attrs={attr_name: attr_value})
            if meta and meta.get("content"):
                return meta["content"].strip()
        
        # Try time tag
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            return time_tag["datetime"].strip()
        
        return None

