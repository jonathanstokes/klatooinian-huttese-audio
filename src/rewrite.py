import re
import random
import os
from typing import Callable
from dotenv import load_dotenv

# Load .env file
load_dotenv()

VOWELS = "aeiou"
CONS = "bcdfghjklmnpqrstvwxz"

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

def _swap_words(text: str) -> str:
    """
    Swap words systematically to make word order less English-like.
    Swaps positions (2,3), (7,8), (12,13), etc. - every 5th word starting from position 2.
    """
    # Split on whitespace while preserving it
    words = text.split()
    
    if len(words) < 2:
        return text
    
    # Swap pairs: (1,2), (6,7), (11,12), (16,17), ... (0-indexed)
    # Pattern: positions 1+5n and 2+5n for n=0,1,2,...
    i = 1  # Start at position 1 (second word, 0-indexed)
    while i + 1 < len(words):
        # Swap words[i] and words[i+1]
        words[i], words[i+1] = words[i+1], words[i]
        i += 5  # Move to next swap position (5 words later)
    
    return " ".join(words)

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

def rewrite_to_huttese(text: str, seed: int = 42) -> str:
    """
    Deterministic rewrite -> "Huttese-ish"
    Keep (C)V(C) bias, break clusters, map th/f/v/j, roll r, add '-ah/-oo' endings sometimes.
    
    Words or phrases in single quotes ('word') or double quotes ("phrase") are 
    preserved as-is (without the quotes).
    
    Words or phrases in the LITERAL_PHRASES environment variable are also preserved.
    
    Word order is also swapped systematically to sound less English-like.
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
        return " " + placeholder_pattern.format(idx) + " "
    
    # First, replace quoted text with placeholders
    # Match both 'text' and "text"
    s = re.sub(r"'([^']+)'|\"([^\"]+)\"", save_preserved, text)
    
    # Second, replace literal phrases from environment variable
    literal_phrases = _get_literal_phrases()
    for phrase in literal_phrases:
        # Case-insensitive match with word boundaries
        pattern = r'\b' + re.escape(phrase) + r'\b'
        
        def save_literal(match):
            idx = len(preserved_sections)
            preserved_sections.append(match.group(0))  # Preserve original case
            return " " + placeholder_pattern.format(idx) + " "
        
        s = re.sub(pattern, save_literal, s, flags=re.IGNORECASE)
    
    # Swap word order before phonetic transformations
    s = _swap_words(s)
    
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
