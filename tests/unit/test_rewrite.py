from src.rewrite import rewrite_to_huttese

def test_basic():
    out = rewrite_to_huttese("Bring me the plans, quickly!", seed=1)
    assert isinstance(out, str)
    assert len(out) > 0

def test_deterministic():
    text = "Hello world"
    out1 = rewrite_to_huttese(text, seed=42)
    out2 = rewrite_to_huttese(text, seed=42)
    assert out1 == out2

def test_different_seeds():
    text = "Hello world"
    out1 = rewrite_to_huttese(text, seed=1)
    out2 = rewrite_to_huttese(text, seed=99)
    # Should be different (with high probability)
    assert out1 != out2 or len(text) < 5  # edge case for very short text



def test_quoted_text_preserved():
    """Test that text in quotes is preserved as-is."""
    from src.rewrite import rewrite_to_huttese
    
    # Single quotes
    result = rewrite_to_huttese("Bring me 'Solo' quickly", seed=42)
    assert "Solo" in result or "solo" in result  # Should preserve Solo
    assert "bring" not in result.lower()  # "bring" should be transformed
    
    # Double quotes
    result = rewrite_to_huttese('The droid named "R2-D2" is here', seed=42)
    assert "R2-D2" in result  # Should preserve R2-D2 exactly
    
    # Multiple quoted sections
    result = rewrite_to_huttese("Tell 'Han' that 'Leia' is waiting", seed=42)
    assert "Han" in result
    assert "Leia" in result
    assert "tell" not in result.lower()  # Should be transformed
    
    # Mixed quotes
    result = rewrite_to_huttese("'Jabba' says \"bring the spice\"", seed=42)
    assert "Jabba" in result
    assert "bring the spice" in result


def test_word_swapping():
    """Test that words are swapped systematically."""
    from src.rewrite import rewrite_to_huttese
    
    # Simple test: "one two three four five six seven eight"
    # Should swap: (2,3) and (7,8)
    # Result: "one three two four five six eight seven"
    # Then apply transformations
    
    # Test with a sentence long enough to have multiple swaps
    result = rewrite_to_huttese("bring me the plans quickly from the ship", seed=42)
    
    # The original order is: bring me the plans quickly from the ship
    # After swapping (2,3) and (7,8): bring the me plans quickly from ship the
    # We can't easily test the exact output due to transformations,
    # but we can verify it's different from no-swap version
    
    # At minimum, verify the function runs without error
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Test with short sentence (should still work)
    result_short = rewrite_to_huttese("hello world", seed=42)
    assert isinstance(result_short, str)
    assert len(result_short) > 0
    
    # Test that swapping is deterministic
    result1 = rewrite_to_huttese("one two three four five", seed=42)
    result2 = rewrite_to_huttese("one two three four five", seed=42)
    assert result1 == result2


def test_literal_phrases_from_env():
    """Test that phrases from LITERAL_PHRASES env var are preserved."""
    import os
    from src.rewrite import rewrite_to_huttese
    
    # Set environment variable for test
    os.environ["LITERAL_PHRASES"] = "Hendo,Star Wars,Chris"
    
    # Reload the module to pick up new env var
    import importlib
    import src.rewrite
    importlib.reload(src.rewrite)
    from src.rewrite import rewrite_to_huttese
    
    # Test single word
    result = rewrite_to_huttese("Tell Hendo to bring the plans", seed=42)
    assert "Hendo" in result
    assert "tell" not in result.lower()  # Should be transformed
    
    # Test multi-word phrase
    result = rewrite_to_huttese("I love Star Wars movies", seed=42)
    assert "Star Wars" in result
    assert "love" not in result.lower()  # Should be transformed
    
    # Test case insensitivity
    result = rewrite_to_huttese("chris is here", seed=42)
    assert "chris" in result  # Preserves original case
    
    # Clean up
    del os.environ["LITERAL_PHRASES"]
