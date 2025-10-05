"""
Simple TTS synthesis using macOS built-in 'say' command as a fallback.
This avoids the need to download large models from HuggingFace.
"""
import subprocess
import os
from pathlib import Path

def synth_to_wav(text: str, wav_path: str, sample_rate: int = 24000):
    """
    Synthesize speech using macOS 'say' command.
    This is a fallback that doesn't require downloading models.
    """
    # Use macOS 'say' command to generate audio
    # -o outputs to file, -r sets rate (words per minute)
    aiff_path = str(Path(wav_path).with_suffix(".aiff"))
    tmp_wav = str(Path(wav_path).with_suffix(".tmp.wav"))

    # Generate AIFF file with 'say'
    subprocess.run([
        "say", "-o", aiff_path,
        "-v", "Alex",  # Use Alex voice (deeper male voice)
        "-r", "180",   # Slightly slower speech rate
        text
    ], check=True)

    # Convert AIFF to WAV and add 0.5 seconds of silence padding at the end
    # This prevents the last word from being clipped during FX processing
    subprocess.run([
        "sox", aiff_path, "-r", str(sample_rate), tmp_wav, "pad", "0", "0.5"
    ], check=True)

    # Move temp file to final destination
    Path(tmp_wav).rename(wav_path)

    # Clean up AIFF file
    Path(aiff_path).unlink(missing_ok=True)

    return wav_path

