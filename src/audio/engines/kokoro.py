"""
Kokoro TTS synthesis using PyTorch with MPS (Apple Silicon GPU) support.
This provides fast, high-quality TTS on Apple Silicon.
"""
from kokoro import KPipeline
import soundfile as sf
import os

# Lazy singleton so the model loads once per process
_KOKORO_PIPELINE = None

def get_kokoro_pipeline():
    """Get or initialize the Kokoro pipeline."""
    global _KOKORO_PIPELINE
    if _KOKORO_PIPELINE is None:
        # Initialize with American English
        # Explicitly specify repo_id to suppress warning
        _KOKORO_PIPELINE = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
    return _KOKORO_PIPELINE

def synth_to_wav(text: str, wav_path: str, sample_rate: int = 24000, voice: str = 'am_michael'):
    """
    Synthesize speech using Kokoro TTS.
    This uses PyTorch with MPS (Metal Performance Shaders) for GPU acceleration on Apple Silicon.
    Set PYTORCH_ENABLE_MPS_FALLBACK=1 environment variable to enable GPU acceleration.

    Available male voices (American English):
    - am_michael (C+, recommended) - Best male voice
    - am_fenrir (C+) - Good alternative
    - am_puck (C+) - Good alternative
    - am_echo, am_eric, am_liam, am_onyx (D) - Lower quality

    Available female voices (American English):
    - af_bella (A-) - Highest quality female
    - af_heart (A) - High quality female (original default)
    - af_nicole (B-) - Good quality
    """
    pipeline = get_kokoro_pipeline()

    # Generate audio
    # Kokoro outputs at 24kHz by default
    generator = pipeline(text, voice=voice, speed=1)

    # Kokoro returns a generator, we take the first (and usually only) result
    for _, _, audio in generator:
        # Write to file
        sf.write(wav_path, audio, sample_rate)
        break  # Only take the first result

    return wav_path

