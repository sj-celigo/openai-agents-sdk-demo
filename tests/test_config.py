"""Tests for configuration management."""

import os
import pytest

from src.utils.config import Config, get_config


class TestConfig:
    """Test Config class."""
    
    def test_config_from_env_vars(self):
        """Test loading config from environment variables."""
        os.environ["OPENAI_API_KEY"] = "test-openai-key"
        os.environ["TAVILY_API_KEY"] = "test-tavily-key"
        os.environ["AGENT_MODEL"] = "gpt-4"
        os.environ["AGENT_TEMPERATURE"] = "0.5"
        os.environ["MAX_SEARCH_RESULTS"] = "10"
        
        config = Config()
        
        assert config.openai_api_key == "test-openai-key"
        assert config.tavily_api_key == "test-tavily-key"
        assert config.agent_model == "gpt-4"
        assert config.agent_temperature == 0.5
        assert config.max_search_results == 10
    
    def test_config_defaults(self):
        """Test default configuration values."""
        # Clear env vars to test true defaults
        import os
        env_vars_to_clear = ["AGENT_MODEL", "AGENT_TEMPERATURE", "MAX_SEARCH_RESULTS", "REQUEST_TIMEOUT"]
        old_values = {}
        
        for var in env_vars_to_clear:
            old_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        
        try:
            config = Config(
                openai_api_key="test-key",
                tavily_api_key="test-key",
            )
            
            assert config.agent_model == "gpt-4-turbo"
            assert config.agent_temperature == 0.3
            assert config.max_search_results == 5
            assert config.request_timeout == 30
            assert config.user_agent.startswith("Mozilla/5.0")
        finally:
            # Restore
            for var, value in old_values.items():
                if value is not None:
                    os.environ[var] = value
    
    def test_config_validation_missing_openai_key(self):
        """Test validation fails when OpenAI key is missing."""
        config = Config(openai_api_key="", tavily_api_key="test-key")
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            config.validate_required_keys()
    
    def test_config_validation_missing_tavily_key(self):
        """Test validation fails when Tavily key is missing."""
        config = Config(openai_api_key="test-key", tavily_api_key="")
        
        with pytest.raises(ValueError, match="TAVILY_API_KEY"):
            config.validate_required_keys()
    
    def test_config_validation_success(self):
        """Test validation succeeds with all required keys."""
        config = Config(
            openai_api_key="test-openai-key",
            tavily_api_key="test-tavily-key",
        )
        
        # Should not raise
        config.validate_required_keys()
    
    def test_get_config(self):
        """Test get_config function."""
        os.environ["OPENAI_API_KEY"] = "test-openai-key"
        os.environ["TAVILY_API_KEY"] = "test-tavily-key"
        
        config = get_config()
        
        assert isinstance(config, Config)
        assert config.openai_api_key == "test-openai-key"
        assert config.tavily_api_key == "test-tavily-key"
    
    def test_config_immutable(self):
        """Test that config is immutable (frozen)."""
        config = Config(
            openai_api_key="test-key",
            tavily_api_key="test-key",
        )
        
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            config.agent_model = "gpt-3.5-turbo"

