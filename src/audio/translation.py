import re
import random
import os
from typing import Callable
from dotenv import load_dotenv

# Load .env file
load_dotenv()

VOWELS = "aeiou"
CONS = "bcdfghjklmnpqrstvwxz"

# Common English stop words that can be safely omitted
STOP_WORDS = {
    "a", "an", "the",  # Articles
    "is", "are", "was", "were", "be", "been", "being",  # Be verbs
    "have", "has", "had", "having",  # Have verbs
    "do", "does", "did", "doing",  # Do verbs
    "will", "would", "shall", "should", "may", "might", "must", "can", "could",  # Modals
    "am",  # First person be
    "i", "you", "he", "she", "it", "we", "they",  # Pronouns
    "me", "him", "her", "us", "them",  # Object pronouns
    "my", "your", "his", "its", "our", "their",  # Possessive pronouns
    "this", "that", "these", "those",  # Demonstratives
    "of", "to", "in", "on", "at", "by", "for", "with", "from", "as",  # Prepositions
    "into", "onto", "upon", "about", "above", "below", "between", "through",  # More prepositions
    "and", "but", "or", "nor", "so", "yet",  # Conjunctions
    "if", "then", "than", "when", "where", "while", "because",  # Subordinating conjunctions
    "not", "no",  # Negations
    "all", "any", "some", "each", "every", "both", "few", "more", "most", "other", "such",  # Quantifiers
    "just", "only", "very", "too", "also",  # Adverbs
    "what", "which", "who", "whom", "whose", "why", "how",  # Question words
}

def _rng(seed: int):
    rnd = random.Random(seed)
    return rnd

def _len_vowel(m, rnd):
    ch = m.group(0)
    # ~15% chance lengthen a/o
    if ch in "ao" and rnd.random() < 0.15:
        return ch * 2
    return ch

def _get_literal_phrases():
    """Get list of literal phrases from environment variable."""
    literal_str = os.getenv("LITERAL_PHRASES", "")
    if not literal_str:
        return []
    
    # Parse comma-delimited list and strip whitespace
    phrases = [p.strip() for p in literal_str.split(",") if p.strip()]
    
    # Sort by length (longest first) to match longer phrases before shorter ones
    # e.g., "Star Wars" before "Star"
    phrases.sort(key=len, reverse=True)
    
    return phrases

def _strip_words(text: str, strip_stop_words: bool = True, strip_every_nth: int = 0, original_starts_with_literal: bool = False, original_ends_with_literal: bool = False) -> str:
    """
    Strip words from text to make it shorter.

    Args:
        text: Input text (may contain placeholders like §§§0§§§)
        strip_stop_words: If True, remove common English stop words
        strip_every_nth: If > 0, also remove every Nth word from remaining words
        original_starts_with_literal: True if original text started with a literal phrase
        original_ends_with_literal: True if original text ended with a literal phrase

    Returns:
        Text with words stripped, preserving placeholders and punctuation
    """
    if not strip_stop_words and strip_every_nth == 0:
        return text  # No stripping needed

    # Extract trailing punctuation
    trailing_punct = ""
    text_stripped = text.rstrip()
    if text_stripped and text_stripped[-1] in ".,!?;:":
        i = len(text_stripped) - 1
        while i >= 0 and text_stripped[i] in ".,!?;:":
            i -= 1
        trailing_punct = text_stripped[i+1:]
        text_stripped = text_stripped[:i+1]

    # Split into words
    words = text_stripped.split()

    if len(words) == 0:
        return text

    # Helper function to check if a word is a placeholder
    def is_placeholder(word):
        word_clean = word.strip(".,!?;:")
        return word_clean.startswith("§§§") and word_clean.endswith("§§§")

    # Use the passed-in information about whether original text had literals at start/end
    # (This was determined before placeholder replacement in rewrite_to_huttese)
    
    # Keep track of original words and which ones get stripped
    original_words = words.copy()
    stripped_words = []

    # Filter out stop words (but keep placeholders)
    if strip_stop_words:
        filtered_words = []
        for word in words:
            # Check if this is a placeholder (§§§N§§§)
            if word.startswith("§§§") and word.endswith("§§§"):
                filtered_words.append(word)
            else:
                # Remove punctuation for stop word check
                word_clean = word.strip(".,!?;:").lower()
                if word_clean not in STOP_WORDS:
                    filtered_words.append(word)
                else:
                    stripped_words.append(word)
        words = filtered_words

    # Apply Nth word stripping if requested
    if strip_every_nth > 0 and len(words) > 0:
        filtered_words = []
        for i, word in enumerate(words):
            # Keep placeholders always (check for §§§ pattern, ignoring punctuation)
            word_clean = word.strip(".,!?;:")
            if word_clean.startswith("§§§") and word_clean.endswith("§§§"):
                filtered_words.append(word)
            # Skip every Nth word (1-indexed, so i+1)
            elif (i + 1) % strip_every_nth != 0:
                filtered_words.append(word)
            else:
                stripped_words.append(word)
        words = filtered_words

    # Prevent literals from moving to start/end if they weren't there originally
    if len(words) > 0:
        result_starts_with_placeholder = is_placeholder(words[0])
        result_ends_with_placeholder = is_placeholder(words[-1])
        
        # If placeholder moved to start, add back a word before it
        if result_starts_with_placeholder and not original_starts_with_literal:
            # Find first non-placeholder word from original that was stripped
            for orig_word in original_words:
                if not is_placeholder(orig_word) and orig_word in stripped_words:
                    words.insert(0, orig_word)
                    stripped_words.remove(orig_word)
                    break
        
        # If placeholder moved to end, add back a word after it
        if result_ends_with_placeholder and not original_ends_with_literal:
            # Find last non-placeholder word from original that was stripped
            for orig_word in reversed(original_words):
                if not is_placeholder(orig_word) and orig_word in stripped_words:
                    words.append(orig_word)
                    stripped_words.remove(orig_word)
                    break

    return " ".join(words) + trailing_punct



def _swap_words(text: str, original_starts_with_literal: bool = False, original_ends_with_literal: bool = False) -> str:
    """
    Swap words systematically to make word order less English-like.
    Swaps positions (2,3), (7,8), (12,13), etc. - every 5th word starting from position 2.

    Punctuation stays attached to the preceding word, except for trailing punctuation
    at the end of the string.
    
    Args:
        text: Input text (may contain placeholders like §§§0§§§)
        original_starts_with_literal: True if original text started with a literal phrase
        original_ends_with_literal: True if original text ended with a literal phrase
    """
    # Extract trailing punctuation from the end
    trailing_punct = ""
    text_stripped = text.rstrip()
    if text_stripped and text_stripped[-1] in ".,!?;:":
        # Find all trailing punctuation
        i = len(text_stripped) - 1
        while i >= 0 and text_stripped[i] in ".,!?;:":
            i -= 1
        trailing_punct = text_stripped[i+1:]
        text_stripped = text_stripped[:i+1]
    
    # Split into words (this will keep punctuation attached to words)
    words = text_stripped.split()
    
    if len(words) < 2:
        return text_stripped + trailing_punct
    
    # Helper function to check if a word is a placeholder
    def is_placeholder(word):
        word_clean = word.strip(".,!?;:")
        return word_clean.startswith("§§§") and word_clean.endswith("§§§")
    
    # Remember original positions of placeholders
    original_words = words.copy()
    
    # Swap pairs: (1,2), (6,7), (11,12), (16,17), ... (0-indexed)
    # Pattern: positions 1+5n and 2+5n for n=0,1,2,...
    i = 1  # Start at position 1 (second word, 0-indexed)
    while i + 1 < len(words):
        # Swap words[i] and words[i+1]
        words[i], words[i+1] = words[i+1], words[i]
        i += 5  # Move to next swap position (5 words later)
    
    # After swapping, check if placeholders are in the right positions
    if len(words) > 0:
        result_starts_with_placeholder = is_placeholder(words[0])
        result_ends_with_placeholder = is_placeholder(words[-1])
        
        # If placeholder moved to start but shouldn't be there, swap it back with next word
        if result_starts_with_placeholder and not original_starts_with_literal and len(words) > 1:
            if not is_placeholder(words[1]):
                words[0], words[1] = words[1], words[0]
        
        # If placeholder moved to end but shouldn't be there, swap it back with previous word
        if result_ends_with_placeholder and not original_ends_with_literal and len(words) > 1:
            if not is_placeholder(words[-2]):
                words[-1], words[-2] = words[-2], words[-1]
        
        # If original ended with literal but result doesn't, find the placeholder and move it to end
        if original_ends_with_literal and not result_ends_with_placeholder:
            for i in range(len(words)):
                if is_placeholder(words[i]):
                    # Move this placeholder to the end
                    placeholder = words.pop(i)
                    words.append(placeholder)
                    break
        
        # If original started with literal but result doesn't, find the placeholder and move it to start
        if original_starts_with_literal and not result_starts_with_placeholder:
            for i in range(len(words)):
                if is_placeholder(words[i]):
                    # Move this placeholder to the start
                    placeholder = words.pop(i)
                    words.insert(0, placeholder)
                    break
    
    return " ".join(words) + trailing_punct


def _apply_huttese_transforms(s: str, rnd) -> str:
    """Apply the Huttese transformation rules to a string."""
    # 1) cheap maps
    s = re.sub(r"th", "t", s)        # th -> t
    s = re.sub(r"f", "p", s)         # f -> p
    s = re.sub(r"v", "b", s)         # v -> b
    s = re.sub(rf"[gj](?=[ei])", "ch", s)  # soft g/j before e/i -> ch

    # 2) roll r between vowels
    s = re.sub(rf"([{VOWELS}])r([{VOWELS}])", r"\1rr\2", s)

    # 3) collapse/soften clusters: insert helper vowel 'a'
    s = re.sub(rf"([{CONS}])([{CONS}])", r"\1a\2", s)

    # 4) lengthen some vowels (a/o) stochastically but deterministically via rnd
    s = re.sub(r"[ao]", lambda m: _len_vowel(m, rnd), s)

    # 5) word endings: 30% '-ah' or '-oo'
    def ender(m):
        w = m.group(1)
        roll = rnd.random()
        if roll < 0.2:
            return w + "ah"
        elif roll < 0.3:
            return w + "oo"
        else:
            return w
    s = re.sub(r"\b(\w{2,})\b", ender, s)

    return s

def rewrite_to_huttese(
    text: str,
    seed: int = 42,
    strip_stop_words: bool = True,
    strip_every_nth: int = 0
) -> str:
    """
    Deterministic rewrite -> "Huttese-ish"
    Keep (C)V(C) bias, break clusters, map th/f/v/j, roll r, add '-ah/-oo' endings sometimes.

    Words or phrases in single quotes ('word') or double quotes ("phrase") are
    preserved as-is (without the quotes).

    Words or phrases in the LITERAL_PHRASES environment variable are also preserved.

    Word order is also swapped systematically to sound less English-like.

    Args:
        text: Input English text to transform
        seed: Random seed for deterministic transformations
        strip_stop_words: If True (default), remove common English stop words to shorten output
        strip_every_nth: If > 0, also strip every Nth word after stop word removal (0 = disabled)

    Returns:
        Transformed "Huttese-ish" text
    """
    rnd = _rng(seed)
    
    # Extract quoted sections and literal phrases
    preserved_sections = []
    # Use a placeholder with only special characters and numbers
    placeholder_pattern = "§§§{}§§§"
    
    def save_preserved(match):
        # Extract content from either single or double quotes
        content = match.group(1) if match.group(1) is not None else match.group(2)
        idx = len(preserved_sections)
        preserved_sections.append(content)
        # Don't add extra spaces - let the original spacing remain
        return placeholder_pattern.format(idx)
    
    # First, replace quoted text with placeholders
    # Match both 'text' and "text"
    s = re.sub(r"'([^']+)'|\"([^\"]+)\"", save_preserved, text)
    
    # Second, replace literal phrases from environment variable
    literal_phrases = _get_literal_phrases()
    
    # Before replacing literals with placeholders, check if original text starts/ends with a literal
    # This is needed so _strip_words can preserve the position of literals
    original_starts_with_literal = False
    original_ends_with_literal = False
    
    # Check for quoted text at start/end
    if re.match(r'^["\']', text):
        original_starts_with_literal = True
    if re.search(r'["\'][.,!?;:]*$', text):
        original_ends_with_literal = True
    
    # Check for literal phrases at start/end
    for phrase in literal_phrases:
        # Check start (case-insensitive, word boundary)
        if re.match(r'^' + re.escape(phrase) + r'\b', text, flags=re.IGNORECASE):
            original_starts_with_literal = True
        # Check end (case-insensitive, word boundary, allow trailing punctuation)
        if re.search(r'\b' + re.escape(phrase) + r'[.,!?;:]*$', text, flags=re.IGNORECASE):
            original_ends_with_literal = True
    
    for phrase in literal_phrases:
        # Case-insensitive match with word boundaries
        pattern = r'\b' + re.escape(phrase) + r'\b'
        
        def save_literal(match):
            idx = len(preserved_sections)
            preserved_sections.append(match.group(0))  # Preserve original case
            # Don't add extra spaces - let the original spacing remain
            return placeholder_pattern.format(idx)
        
        s = re.sub(pattern, save_literal, s, flags=re.IGNORECASE)

    # Strip words (stop words and/or every Nth word) before other transformations
    s = _strip_words(s, strip_stop_words=strip_stop_words, strip_every_nth=strip_every_nth,
                     original_starts_with_literal=original_starts_with_literal,
                     original_ends_with_literal=original_ends_with_literal)

    # Swap word order before phonetic transformations
    s = _swap_words(s, original_starts_with_literal=original_starts_with_literal, original_ends_with_literal=original_ends_with_literal)

    # Apply Huttese transformation to the remaining text
    s = s.lower()
    s = _apply_huttese_transforms(s, rnd)
    
    # Restore preserved sections (without quotes)
    for idx, preserved_text in enumerate(preserved_sections):
        placeholder = placeholder_pattern.format(idx)
        s = s.replace(placeholder, preserved_text)
    
    # spacing/punct tidy
    s = re.sub(r"\s+", " ", s).strip()
    return s
