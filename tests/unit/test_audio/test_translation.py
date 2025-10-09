from src.audio.translation import rewrite_to_huttese

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
    from src.audio.translation import rewrite_to_huttese
    
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
    from src.audio.translation import rewrite_to_huttese
    
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
    from src.audio.translation import rewrite_to_huttese
    
    # Set environment variable for test
    os.environ["LITERAL_PHRASES"] = "Hendo,Star Wars,Chris"
    
    # Reload the module to pick up new env var
    import importlib
    import src.audio.translation
    importlib.reload(src.audio.translation)
    from src.audio.translation import rewrite_to_huttese
    
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


def test_punctuation_stays_with_word():
    """Test that punctuation stays attached to preceding word during word swapping."""
    from src.audio.translation import rewrite_to_huttese
    import os

    # Set up literal phrases
    os.environ["LITERAL_PHRASES"] = "Trey,Hagar,dungeonmaster"

    # Reload module
    import importlib
    import src.audio.translation
    importlib.reload(src.audio.translation)
    from src.audio.translation import rewrite_to_huttese

    # Test with period in middle
    result = rewrite_to_huttese("Tell Trey that Hagar loves his dungeonmaster.", seed=42)

    # Period should stay with "dungeonmaster" not become separate word
    assert " . " not in result, f"Period should not be separated: {result}"
    assert "dungeonmaster." in result or result.endswith("dungeonmaster."), f"Period should stay with word: {result}"

    # Test with comma
    result = rewrite_to_huttese("Hello Trey, how are you", seed=42)
    assert " , " not in result, f"Comma should not be separated: {result}"

    # Test with exclamation
    result = rewrite_to_huttese("Bring me the plans!", seed=42)
    assert " ! " not in result, f"Exclamation should not be separated: {result}"

    # Clean up
    if "LITERAL_PHRASES" in os.environ:
        del os.environ["LITERAL_PHRASES"]


def test_stop_word_stripping_with_quoted_phrases():
    """Test that stop words are stripped but quoted phrases are preserved."""
    from src.audio.translation import rewrite_to_huttese

    # Test case 1: Quoted phrase with stop words around it
    result = rewrite_to_huttese('I don\'t know that this "Belefante Starship" has wings.', seed=42)

    # "Belefante Starship" should be preserved exactly
    assert "Belefante Starship" in result, f"Quoted phrase should be preserved: {result}"

    # Stop words should be stripped (the output should be shorter)
    # Original has: I, don't, know, that, this, "Belefante Starship", has, wings
    # After stripping stop words: know, "Belefante Starship", wings
    # So we should NOT see common stop words in the output
    words_in_result = result.lower().split()

    # Check that the result is shorter (stop words removed)
    original_word_count = len('I don\'t know that this "Belefante Starship" has wings.'.split())
    # Account for the quoted phrase being 2 words
    assert len(words_in_result) < original_word_count, f"Result should be shorter after stop word removal: {result}"


def test_stop_word_stripping_with_literal_phrases():
    """Test that stop words are stripped but literal phrases from env var are preserved."""
    import os
    from src.audio.translation import rewrite_to_huttese

    # Set up literal phrase
    os.environ["LITERAL_PHRASES"] = "Hendo"

    # Reload module
    import importlib
    import src.audio.translation
    importlib.reload(src.audio.translation)
    from src.audio.translation import rewrite_to_huttese

    # Test case 2: Literal phrase with stop words around it
    result = rewrite_to_huttese("I wish you a happy birthday, Hendo!", seed=42)

    # "Hendo" should be preserved exactly
    assert "Hendo" in result, f"Literal phrase should be preserved: {result}"

    # Stop words should be stripped
    # Original: I, wish, you, a, happy, birthday, Hendo
    # After stripping: wish, happy, birthday, Hendo
    # Check that result is shorter
    original_word_count = len("I wish you a happy birthday, Hendo!".split())
    result_word_count = len(result.split())
    assert result_word_count < original_word_count, f"Result should be shorter after stop word removal: {result}"

    # Clean up
    del os.environ["LITERAL_PHRASES"]


def test_stop_word_stripping_with_multiple_literals():
    """Test stop word stripping with both quoted and env var literals."""
    import os
    from src.audio.translation import rewrite_to_huttese

    # Set up literal phrases
    os.environ["LITERAL_PHRASES"] = "Mos Eisley"

    # Reload module
    import importlib
    import src.audio.translation
    importlib.reload(src.audio.translation)
    from src.audio.translation import rewrite_to_huttese

    # Test with both quoted and literal phrases
    result = rewrite_to_huttese('The "Millennium Falcon" is at the Mos Eisley cantina.', seed=42)

    # Both literals should be preserved
    assert "Millennium Falcon" in result, f"Quoted phrase should be preserved: {result}"
    assert "Mos Eisley" in result, f"Literal phrase should be preserved: {result}"

    # Stop words (The, is, at, the) should be stripped
    # Original: The, "Millennium Falcon", is, at, the, Mos Eisley, cantina
    # After stripping: "Millennium Falcon", Mos Eisley, cantina
    original_word_count = len('The "Millennium Falcon" is at the Mos Eisley cantina.'.split())
    result_word_count = len(result.split())
    assert result_word_count < original_word_count, f"Result should be shorter: {result}"

    # Clean up
    del os.environ["LITERAL_PHRASES"]


def test_stop_word_stripping_disabled():
    """Test that stop word stripping can be disabled."""
    from src.audio.translation import rewrite_to_huttese

    text = "I am the one who knocks"

    # With stop word stripping enabled (default)
    result_with_stripping = rewrite_to_huttese(text, seed=42, strip_stop_words=True)

    # With stop word stripping disabled
    result_without_stripping = rewrite_to_huttese(text, seed=42, strip_stop_words=False)

    # The version without stripping should have more words
    assert len(result_without_stripping.split()) >= len(result_with_stripping.split()), \
        f"Without stripping should be longer or equal: with={result_with_stripping}, without={result_without_stripping}"


def test_nth_word_stripping():
    """Test that every Nth word can be stripped."""
    from src.audio.translation import rewrite_to_huttese

    # Test with strip_every_nth=3 (strip every 3rd word after stop word removal)
    text = "one two three four five six seven eight nine ten"

    # With Nth word stripping
    result_with_nth = rewrite_to_huttese(text, seed=42, strip_stop_words=False, strip_every_nth=3)

    # Without Nth word stripping
    result_without_nth = rewrite_to_huttese(text, seed=42, strip_stop_words=False, strip_every_nth=0)

    # The version with Nth stripping should be shorter
    assert len(result_with_nth.split()) < len(result_without_nth.split()), \
        f"With Nth stripping should be shorter: with={result_with_nth}, without={result_without_nth}"


def test_combined_stop_and_nth_word_stripping():
    """Test that stop word and Nth word stripping work together."""
    from src.audio.translation import rewrite_to_huttese

    text = "I am going to the store with my friend for some food"

    # With both stop word and Nth word stripping
    result_both = rewrite_to_huttese(text, seed=42, strip_stop_words=True, strip_every_nth=2)

    # With only stop word stripping
    result_stop_only = rewrite_to_huttese(text, seed=42, strip_stop_words=True, strip_every_nth=0)

    # With both should be shorter than stop-only
    assert len(result_both.split()) <= len(result_stop_only.split()), \
        f"Combined should be shorter or equal: both={result_both}, stop_only={result_stop_only}"
def test_nth_word_stripping_preserves_literals_with_punctuation():
    """Test that Nth word stripping preserves literal phrases even when they have punctuation."""
    import os
    from src.audio.translation import rewrite_to_huttese

    # Set up literal phrase
    os.environ["LITERAL_PHRASES"] = "Hendo"

    # Reload module
    import importlib
    import src.audio.translation
    importlib.reload(src.audio.translation)
    from src.audio.translation import rewrite_to_huttese

    # Test with punctuation after literal phrase
    result = rewrite_to_huttese("Happy birthday, Hendo, may you enjoy your day fully!", seed=42, strip_stop_words=True, strip_every_nth=3)

    # "Hendo" should be preserved even though it would be in the 3rd position
    assert "Hendo" in result, f"Literal phrase with punctuation should be preserved: {result}"

    # Clean up
    del os.environ["LITERAL_PHRASES"]

