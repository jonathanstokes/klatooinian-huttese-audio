"""Test that all modules can be imported without syntax errors."""

def test_import_cli():
    """Test that cli module can be imported."""
    try:
        import src.cli
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.cli: {e}"

def test_import_interactive():
    """Test that interactive module can be imported."""
    try:
        import src.interactive
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.interactive: {e}"

def test_import_rewrite():
    """Test that rewrite module can be imported."""
    try:
        import src.rewrite
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.rewrite: {e}"

def test_import_synth():
    """Test that synth module can be imported."""
    try:
        import src.synth
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.synth: {e}"

def test_import_fx():
    """Test that fx module can be imported."""
    try:
        import src.fx
        assert True
    except SyntaxError as e:
        assert False, f"SyntaxError in src.fx: {e}"
