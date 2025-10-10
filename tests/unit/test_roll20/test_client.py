"""Unit tests for Roll20 client."""

import pytest
import os
from unittest.mock import Mock, AsyncMock, patch


class TestRoll20ClientImport:
    """Test that the Roll20 client module can be imported and compiled."""
    
    def test_import_client_module(self):
        """Test that the client module imports without syntax errors."""
        try:
            import src.roll20.client
            assert True
        except SyntaxError as e:
            pytest.fail(f"SyntaxError in src.roll20.client: {e}")
    
    def test_import_config_module(self):
        """Test that the config module imports without syntax errors."""
        try:
            import src.roll20.config
            assert True
        except SyntaxError as e:
            pytest.fail(f"SyntaxError in src.roll20.config: {e}")
    
    def test_client_class_exists(self):
        """Test that Roll20Client class exists and can be referenced."""
        from src.roll20.client import Roll20Client
        assert Roll20Client is not None
        assert callable(Roll20Client)


class TestRoll20ClientStructure:
    """Test the structure and interface of Roll20Client class."""
    
    @pytest.fixture
    def mock_env(self):
        """Mock environment variables for testing."""
        with patch.dict(os.environ, {
            'ROLL20_USERNAME': 'test@example.com',
            'ROLL20_PASSWORD': 'testpass123',
            'ROLL20_CAMPAIGN_ID': '12345678'
        }):
            yield
    
    def test_client_instantiation(self, mock_env):
        """Test that Roll20Client can be instantiated."""
        from src.roll20.client import Roll20Client
        client = Roll20Client()
        assert client is not None
        assert client.browser is None
        assert client.page is None
        assert client._logged_in is False
        assert client._game_loaded is False
    
    def test_client_has_required_methods(self, mock_env):
        """Test that Roll20Client has all required methods."""
        from src.roll20.client import Roll20Client
        client = Roll20Client()
        
        # Check that all required methods exist and are callable
        assert hasattr(client, 'start')
        assert callable(client.start)
        
        assert hasattr(client, 'login')
        assert callable(client.login)
        
        assert hasattr(client, 'launch_game')
        assert callable(client.launch_game)
        
        assert hasattr(client, 'verify_chat_ui')
        assert callable(client.verify_chat_ui)
        
        assert hasattr(client, 'initialize')
        assert callable(client.initialize)
        
        assert hasattr(client, 'close')
        assert callable(client.close)
    
    def test_client_methods_are_async(self, mock_env):
        """Test that client methods are async coroutines."""
        from src.roll20.client import Roll20Client
        import inspect
        
        client = Roll20Client()
        
        # These methods should be async
        assert inspect.iscoroutinefunction(client.start)
        assert inspect.iscoroutinefunction(client.login)
        assert inspect.iscoroutinefunction(client.launch_game)
        assert inspect.iscoroutinefunction(client.verify_chat_ui)
        assert inspect.iscoroutinefunction(client.initialize)
        assert inspect.iscoroutinefunction(client.close)


class TestRoll20Config:
    """Test the Roll20Config class."""
    
    def test_config_requires_env_vars(self):
        """Test that config raises error when env vars are missing."""
        from src.roll20.config import Roll20Config
        
        # Clear any existing env vars
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ROLL20_USERNAME"):
                Roll20Config()
    
    def test_config_with_valid_env_vars(self):
        """Test that config works with valid environment variables."""
        from src.roll20.config import Roll20Config
        
        with patch.dict(os.environ, {
            'ROLL20_USERNAME': 'test@example.com',
            'ROLL20_PASSWORD': 'testpass123',
            'ROLL20_CAMPAIGN_ID': '12345678'
        }):
            config = Roll20Config()
            assert config.username == 'test@example.com'
            assert config.password == 'testpass123'
            assert config.campaign_id == '12345678'
    
    def test_config_campaign_url_property(self):
        """Test that campaign_url property generates correct URL."""
        from src.roll20.config import Roll20Config
        
        with patch.dict(os.environ, {
            'ROLL20_USERNAME': 'test@example.com',
            'ROLL20_PASSWORD': 'testpass123',
            'ROLL20_CAMPAIGN_ID': '12345678'
        }):
            config = Roll20Config()
            expected_url = "https://app.roll20.net/campaigns/details/12345678"
            assert config.campaign_url == expected_url
    
    def test_config_login_url_property(self):
        """Test that login_url property returns correct URL."""
        from src.roll20.config import Roll20Config
        
        with patch.dict(os.environ, {
            'ROLL20_USERNAME': 'test@example.com',
            'ROLL20_PASSWORD': 'testpass123',
            'ROLL20_CAMPAIGN_ID': '12345678'
        }):
            config = Roll20Config()
            expected_url = "https://app.roll20.net/sessions/new"
            assert config.login_url == expected_url


class TestRoll20ClientLogic:
    """Test the logic of Roll20Client methods (without actual browser)."""
    
    @pytest.fixture
    def mock_env(self):
        """Mock environment variables for testing."""
        with patch.dict(os.environ, {
            'ROLL20_USERNAME': 'test@example.com',
            'ROLL20_PASSWORD': 'testpass123',
            'ROLL20_CAMPAIGN_ID': '12345678'
        }):
            yield
    
    @pytest.mark.asyncio
    async def test_login_when_already_logged_in(self, mock_env):
        """Test that login returns early if already logged in."""
        from src.roll20.client import Roll20Client
        
        client = Roll20Client()
        client._logged_in = True
        
        # This should return immediately without error
        await client.login()
        
        # Should still be marked as logged in
        assert client._logged_in is True
    
    @pytest.mark.asyncio
    async def test_launch_game_requires_login(self, mock_env):
        """Test that launch_game raises error if not logged in."""
        from src.roll20.client import Roll20Client
        
        client = Roll20Client()
        client._logged_in = False
        
        with pytest.raises(Exception, match="Must be logged in"):
            await client.launch_game()
    
    @pytest.mark.asyncio
    async def test_launch_game_when_already_loaded(self, mock_env):
        """Test that launch_game returns early if game already loaded."""
        from src.roll20.client import Roll20Client
        
        client = Roll20Client()
        client._logged_in = True
        client._game_loaded = True
        
        # This should return immediately without error
        await client.launch_game()
        
        # Should still be marked as loaded
        assert client._game_loaded is True
    
    @pytest.mark.asyncio
    async def test_close_resets_state(self, mock_env):
        """Test that close() resets client state."""
        from src.roll20.client import Roll20Client
        
        client = Roll20Client()
        client._logged_in = True
        client._game_loaded = True
        client.browser = Mock()
        client.browser.stop = Mock()
        client.page = Mock()
        
        await client.close()
        
        # All state should be reset
        assert client.browser is None
        assert client.page is None
        assert client._logged_in is False
        assert client._game_loaded is False



class TestRoll20ClientNewMethods:
    """Test the new dialog dismissal and chat setup methods."""
    
    @pytest.fixture
    def mock_env(self):
        """Mock environment variables for testing."""
        with patch.dict(os.environ, {
            'ROLL20_USERNAME': 'test@example.com',
            'ROLL20_PASSWORD': 'testpass123',
            'ROLL20_CAMPAIGN_ID': '12345678'
        }):
            yield
    
    def test_client_has_new_methods(self, mock_env):
        """Test that Roll20Client has the new methods."""
        from src.roll20.client import Roll20Client
        client = Roll20Client()
        
        # Check that new methods exist and are callable
        assert hasattr(client, 'dismiss_dialogs')
        assert callable(client.dismiss_dialogs)
        
        assert hasattr(client, 'setup_chat_interface')
        assert callable(client.setup_chat_interface)
    
    def test_client_has_chat_element_attributes(self, mock_env):
        """Test that Roll20Client has attributes for chat elements."""
        from src.roll20.client import Roll20Client
        client = Roll20Client()
        
        # Check that chat element attributes exist
        assert hasattr(client, 'chat_textarea')
        assert hasattr(client, 'chat_send_button')
        assert hasattr(client, 'speaking_as_dropdown')
        
        # Initially they should be None
        assert client.chat_textarea is None
        assert client.chat_send_button is None
        assert client.speaking_as_dropdown is None
    
    def test_new_methods_are_async(self, mock_env):
        """Test that new methods are async coroutines."""
        from src.roll20.client import Roll20Client
        import inspect
        
        client = Roll20Client()
        
        # These methods should be async
        assert inspect.iscoroutinefunction(client.dismiss_dialogs)
        assert inspect.iscoroutinefunction(client.setup_chat_interface)
