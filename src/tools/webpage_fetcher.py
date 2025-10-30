"""Webpage fetching and content extraction tool with OpenAI Agents SDK."""

import json
import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup
from agents import function_tool

from ..models.data_models import WebpageContent
from ..utils.config import Config
from ..utils.citation import Citation

logger = logging.getLogger(__name__)

# Global references (will be set by init function)
_config: Optional[Config] = None
_session: Optional[requests.Session] = None
_citation_manager = None  # Will be set by agent


def init_webpage_fetcher_tool(config: Config):
    """Initialize the webpage fetcher tool with configuration."""
    global _config, _session
    _config = config
    _session = requests.Session()
    _session.headers.update({
        "User-Agent": config.user_agent,
    })


def set_citation_manager(citation_manager):
    """Set the citation manager for tracking sources."""
    global _citation_manager
    _citation_manager = citation_manager


def _extract_title(soup: BeautifulSoup) -> str:
    """Extract page title."""
    # Try <title> tag first
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    
    # Try h1
    h1 = soup.find("h1")
    if h1:
        return h1.get_text().strip()
    
    return "Untitled"


def _extract_content(soup: BeautifulSoup) -> str:
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


def _extract_author(soup: BeautifulSoup) -> Optional[str]:
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


def _extract_published_date(soup: BeautifulSoup) -> Optional[str]:
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


def _fetch_webpage_impl(url: str) -> str:
    """
    Implementation of fetch_webpage (not decorated, for testing).
    
    Args:
        url: The URL of the webpage to fetch
        
    Returns:
        JSON string with extracted content
    """
    if not url or not url.strip():
        return json.dumps({
            "success": False,
            "error": "URL cannot be empty",
        })
    
    # Get config and session
    config = _config
    session = _session
    
    if not config or not session:
        # Fallback: create if not initialized
        from ..utils.config import get_config
        config = get_config()
        session = requests.Session()
        session.headers.update({"User-Agent": config.user_agent})
    
    try:
        logger.info(f"Fetching webpage: {url}")
        
        # Fetch the page
        response = session.get(
            url,
            timeout=config.request_timeout,
            allow_redirects=True,
        )
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, "lxml")
        
        # Extract title
        title = _extract_title(soup)
        
        # Extract main content
        content = _extract_content(soup)
        
        # Extract metadata
        author = _extract_author(soup)
        published_date = _extract_published_date(soup)
        
        webpage_content = WebpageContent(
            url=url,
            title=title,
            content=content,
            author=author,
            published_date=published_date,
            success=True,
        )
        
        logger.info(f"Successfully extracted content from {url}")
        
        # Track citation if manager is available
        if _citation_manager:
            citation = Citation(
                url=url,
                title=title,
                snippet=content[:200] if content else None,
                author=author,
                published_date=published_date,
            )
            _citation_manager.add_citation(citation)
        
        return json.dumps(webpage_content.to_dict())
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching {url}")
        return json.dumps({
            "success": False,
            "error": "Request timeout",
            "url": url,
        })
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e}")
        return json.dumps({
            "success": False,
            "error": f"HTTP {e.response.status_code}",
            "url": url,
        })
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "url": url,
        })


@function_tool
def fetch_webpage(url: str) -> str:
    """
    Fetch and extract the main content from a webpage.
    
    Given a URL, this tool retrieves the page and extracts the title and main text content,
    removing navigation, ads, scripts, and other non-content elements.
    
    Args:
        url: The URL of the webpage to fetch
        
    Returns:
        JSON string with extracted content including success status, URL, title, content,
        author, and published_date
    """
    return _fetch_webpage_impl(url)
