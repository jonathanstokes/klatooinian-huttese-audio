"""Test that all modules can be imported without syntax errors."""

def test_import_audio_cli():
    """Test that audio CLI module can be imported."""
    try:
        import src.cli.audio_cli
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.cli.audio_cli: {e}"

def test_import_interactive():
    """Test that interactive module can be imported."""
    try:
        import src.cli.interactive
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.cli.interactive: {e}"

def test_import_translation():
    """Test that translation module can be imported."""
    try:
        import src.audio.translation
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.audio.translation: {e}"

def test_import_effects():
    """Test that effects module can be imported."""
    try:
        import src.audio.effects
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.audio.effects: {e}"

def test_import_kokoro_engine():
    """Test that kokoro engine module can be imported."""
    try:
        import src.audio.engines.kokoro
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.audio.engines.kokoro: {e}"

def test_import_coqui_engine():
    """Test that coqui engine module can be imported."""
    try:
        import src.audio.engines.coqui
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.audio.engines.coqui: {e}"

def test_import_simple_engine():
    """Test that simple engine module can be imported."""
    try:
        import src.audio.engines.simple
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.audio.engines.simple: {e}"

def test_import_roll20_client():
    """Test that roll20 client module can be imported."""
    try:
        import src.roll20.client
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.roll20.client: {e}"

def test_import_roll20_message():
    """Test that roll20 message module can be imported."""
    try:
        import src.roll20.message
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.roll20.message: {e}"

def test_import_input_ui():
    """Test that input UI module can be imported."""
    try:
        import src.input.ui
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.input.ui: {e}"

