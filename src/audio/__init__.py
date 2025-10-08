"""
Audio generation feature: Text-to-translated-audio.

This package handles:
- Translation of English text to Huttese-ish language
- Text-to-speech synthesis using various engines
- Audio effects processing for Klatooinian voice timbre
"""

from .translation import rewrite_to_huttese
from .effects import process_klatooinian

__all__ = ['rewrite_to_huttese', 'process_klatooinian']

