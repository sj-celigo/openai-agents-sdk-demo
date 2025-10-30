"""Research Assistant Agent using OpenAI Agents SDK."""

import logging
from typing import Optional
from agents import Agent, Runner

from .models.data_models import ResearchQuery, ResearchResult, ResearchDepth
from .tools import web_search, fetch_webpage, init_web_search_tool, init_webpage_fetcher_tool, set_citation_manager
from .utils.config import Config
from .utils.citation import CitationManager

logger = logging.getLogger(__name__)


class ResearchAgent:
    """AI agent for conducting research using OpenAI Agents SDK."""
    
    SYSTEM_PROMPT = """You are a professional research assistant. Your role is to:

1. Search for information on topics using web search
2. Fetch and read webpage content from search results
3. Synthesize information from multiple sources
4. Provide well-cited, accurate summaries

When conducting research:
- Use web_search to find relevant sources
- Use fetch_webpage to read the full content of promising sources
- Cite your sources using [1], [2], etc. format
- Cross-reference information across multiple sources
- Present balanced viewpoints when sources disagree
- Organize findings logically

Always be thorough, accurate, and transparent about your sources."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the research agent.
        
        Args:
            config: Application configuration (uses default if not provided)
        """
        from .utils.config import get_config
        
        self.config = config or get_config()
        self.citation_manager = CitationManager()
        
        # Initialize tools with configuration
        init_web_search_tool(self.config)
        init_webpage_fetcher_tool(self.config)
        set_citation_manager(self.citation_manager)
        
        # Create the agent with tools
        self.agent = None  # Will be created per research call with custom instructions
    
    def research(
        self,
        query: str,
        research_depth: ResearchDepth = ResearchDepth.STANDARD,
        max_sources: int = 5,
    ) -> ResearchResult:
        """
        Conduct research on a given query.
        
        Args:
            query: Research question or topic
            research_depth: How deep to research
            max_sources: Maximum number of sources to consult
            
        Returns:
            Research results with summary and citations
        """
        research_query = ResearchQuery(
            query=query,
            research_depth=research_depth,
            max_sources=max_sources,
        )
        
        logger.info(f"Starting research on: {query}")
        self.citation_manager.clear()
        
        # Create custom instructions for this research query
        instructions = self._create_research_instructions(research_query)
        
        # Create agent for this research
        agent = Agent(
            name="Research Assistant",
            instructions=instructions,
            tools=[web_search, fetch_webpage],
            model=self.config.agent_model,
            # Note: temperature is set via model_settings if needed
        )
        
        # Run the agent using Runner
        try:
            result = Runner.run_sync(
                agent,
                input=f"Research the following topic: {query}",
                max_turns=10,  # Equivalent to max_iterations
            )
            
            logger.info("Research complete")
            
            # Extract the final output
            summary = result.final_output if hasattr(result, 'final_output') else str(result)
            
            # Get sources from citation manager
            sources_consulted = [citation.url for citation in self.citation_manager.citations]
            
            return ResearchResult(
                query=query,
                summary=summary + "\n\n" + self.citation_manager.format_bibliography(),
                sources_consulted=sources_consulted,
                research_depth=research_depth,
            )
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            # Return error result
            return ResearchResult(
                query=query,
                summary=f"Research failed: {str(e)}",
                sources_consulted=[],
                research_depth=research_depth,
            )
    
    def _create_research_instructions(self, query: ResearchQuery) -> str:
        """Create the research instructions for the agent."""
        depth_instructions = {
            ResearchDepth.QUICK: "Do a quick search and provide a brief summary from 2-3 sources.",
            ResearchDepth.STANDARD: "Search multiple sources and provide a comprehensive summary.",
            ResearchDepth.COMPREHENSIVE: "Conduct in-depth research across many sources and provide detailed analysis.",
        }
        
        custom_instructions = f"""
{self.SYSTEM_PROMPT}

Research depth: {query.research_depth}
{depth_instructions.get(query.research_depth, "")}

Please:
1. Search for relevant information using web_search
2. Read the most relevant sources using fetch_webpage (up to {query.max_sources} sources)
3. Synthesize the information into a clear, well-organized summary
4. Cite all sources using [1], [2], etc. format
5. Provide a sources section at the end

Begin your research now."""
        
        return custom_instructions
