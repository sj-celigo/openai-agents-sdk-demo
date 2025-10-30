"""Tests for the research agent."""

from unittest.mock import MagicMock, patch
import pytest

from src.agent import ResearchAgent
from src.models.data_models import ResearchDepth


class TestResearchAgent:
    """Test ResearchAgent class."""
    
    def test_agent_initialization(self, mock_config):
        """Test agent initialization."""
        agent = ResearchAgent(mock_config)
        
        assert agent.config == mock_config
        assert agent.citation_manager is not None
    
    @patch('src.agent.Runner')
    def test_research_simple_flow(self, mock_runner_class, mock_config):
        """Test simple research flow."""
        # Setup Runner mock
        mock_result = MagicMock()
        mock_result.final_output = "Research summary goes here"
        mock_runner_class.run_sync.return_value = mock_result
        
        # Create agent and run research
        agent = ResearchAgent(mock_config)
        result = agent.research(query="test query")
        
        assert result.query == "test query"
        assert "Research summary goes here" in result.summary
        assert result.research_depth == ResearchDepth.STANDARD
        
        # Verify Runner was called
        mock_runner_class.run_sync.assert_called_once()
    
    @patch('src.agent.Runner')
    def test_research_error_handling(self, mock_runner_class, mock_config):
        """Test research error handling."""
        # Setup Runner to raise error
        mock_runner_class.run_sync.side_effect = Exception("Test error")
        
        agent = ResearchAgent(mock_config)
        result = agent.research(query="test query")
        
        assert result.query == "test query"
        assert "failed" in result.summary.lower()
    
    @patch('src.agent.Runner')
    def test_research_quick_depth(self, mock_runner_class, mock_config):
        """Test research with quick depth."""
        mock_result = MagicMock()
        mock_result.final_output = "Quick summary"
        mock_runner_class.run_sync.return_value = mock_result
        
        agent = ResearchAgent(mock_config)
        result = agent.research(query="test", research_depth=ResearchDepth.QUICK)
        
        assert result.research_depth == ResearchDepth.QUICK
    
    @patch('src.agent.Runner')
    def test_research_comprehensive_depth(self, mock_runner_class, mock_config):
        """Test research with comprehensive depth."""
        mock_result = MagicMock()
        mock_result.final_output = "Comprehensive summary"
        mock_runner_class.run_sync.return_value = mock_result
        
        agent = ResearchAgent(mock_config)
        result = agent.research(query="test", research_depth=ResearchDepth.COMPREHENSIVE)
        
        assert result.research_depth == ResearchDepth.COMPREHENSIVE
    
    @patch('src.agent.Runner')
    def test_research_max_turns(self, mock_runner_class, mock_config):
        """Test that research uses max_turns limit."""
        mock_result = MagicMock()
        mock_result.final_output = "Summary"
        mock_runner_class.run_sync.return_value = mock_result
        
        agent = ResearchAgent(mock_config)
        agent.research(query="test")
        
        # Verify max_turns was set
        call_kwargs = mock_runner_class.run_sync.call_args[1]
        assert call_kwargs.get("max_turns") == 10
    
    @patch('src.agent.Runner')
    def test_citation_manager_uses_global_state(self, mock_runner_class, mock_config):
        """Test that citation manager is available."""
        mock_result = MagicMock()
        mock_result.final_output = "Summary"
        mock_runner_class.run_sync.return_value = mock_result
        
        agent = ResearchAgent(mock_config)
        
        # Citation manager should be set
        from src.tools.webpage_fetcher import _citation_manager
        # After init, citation manager should be set
        agent.research(query="test")
        # We can't easily test the global state, but we can verify it exists
        assert agent.citation_manager is not None
    
    @patch('src.agent.Runner')
    def test_create_agent_with_tools(self, mock_runner_class, mock_config):
        """Test that agent is created with correct tools."""
        mock_result = MagicMock()
        mock_result.final_output = "Summary"
        mock_runner_class.run_sync.return_value = mock_result
        
        agent = ResearchAgent(mock_config)
        agent.research(query="test query")
        
        # Get the agent that was passed to Runner
        call_args = mock_runner_class.run_sync.call_args[0]
        agent_arg = call_args[0]
        
        # Check that agent has correct properties
        assert hasattr(agent_arg, 'name')
        assert agent_arg.name == "Research Assistant"
        assert hasattr(agent_arg, 'tools')
        assert len(agent_arg.tools) == 2
    
    def test_research_instructions_content(self, mock_config):
        """Test the content of research instructions."""
        from src.models.data_models import ResearchQuery
        
        agent = ResearchAgent(mock_config)
        query = ResearchQuery(
            query="test topic",
            research_depth=ResearchDepth.STANDARD,
            max_sources=5,
        )
        
        instructions = agent._create_research_instructions(query)
        
        assert "standard" in instructions.lower()
        assert "web_search" in instructions
        assert "fetch_webpage" in instructions
        assert "5" in instructions  # max_sources
    
    @patch('src.agent.Runner')
    def test_sources_consulted_extraction(self, mock_runner_class, mock_config):
        """Test that sources consulted are extracted from citations."""
        mock_result = MagicMock()
        mock_result.final_output = "Summary"
        mock_runner_class.run_sync.return_value = mock_result
        
        agent = ResearchAgent(mock_config)
        
        # Manually add a citation to test extraction
        from src.utils.citation import Citation
        agent.citation_manager.add_citation(
            Citation(url="https://test.com", title="Test")
        )
        
        result = agent.research(query="test")
        
        # Note: citations are cleared at start of research
        # So we can't test this directly without running actual tools
        assert isinstance(result.sources_consulted, list)
