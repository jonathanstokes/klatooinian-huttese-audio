# Suppress warnings before importing TTS
from .suppress_warnings import suppress_tts_loading_messages
suppress_tts_loading_messages()

from TTS.api import TTS
import soundfile as sf
import numpy as np
from pathlib import Path

# Lazy singleton so the model loads once per process
_TTS_MODEL = None

def get_tts():
    global _TTS_MODEL
    if _TTS_MODEL is None:
        _TTS_MODEL = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
    return _TTS_MODEL

def synth_to_wav(text: str, wav_path: str, sample_rate: int = 24000):
    tts = get_tts()
    # XTTS v2 is multi-speaker and requires a speaker reference
    # We'll use the default "Claribel Dervla" speaker for now
    audio = tts.tts(text=text, language="en", speaker="Claribel Dervla")
    sf.write(wav_path, np.array(audio), sample_rate)
    return wav_path
