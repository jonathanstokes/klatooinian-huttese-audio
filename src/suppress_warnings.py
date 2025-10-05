"""
Suppress noisy warnings from dependencies.
Import this module early to clean up console output.
"""
import warnings
import os
import sys

# Suppress specific warnings that are not actionable for end users
warnings.filterwarnings("ignore", category=UserWarning, module="jieba")
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

# Suppress TTS library's verbose console output
# The TTS library prints directly to stdout, so we need to redirect it
class SuppressTTSOutput:
    """Context manager to suppress TTS library's verbose output."""
    
    def __init__(self):
        self.original_stdout = None
        self.original_stderr = None
        
    def __enter__(self):
        # Save original stdout/stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        # Redirect to devnull
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original stdout/stderr
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        return False


def suppress_tts_loading_messages():
    """
    Suppress TTS library's loading messages.
    Call this before importing TTS modules.
    """
    # Set TTS environment variable to reduce verbosity
    os.environ['TTS_VERBOSE'] = '0'
    
    # Suppress TTS logger
    import logging
    logging.getLogger('TTS').setLevel(logging.ERROR)
    logging.getLogger('TTS.utils').setLevel(logging.ERROR)
    logging.getLogger('TTS.tts').setLevel(logging.ERROR)

