import pytest
import tempfile
import subprocess
from pathlib import Path
from src.fx import process_klatooinian


@pytest.fixture
def sample_audio():
    """Create a simple test audio file using sox."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name
    
    # Generate a simple 1-second sine wave at 440Hz
    subprocess.run([
        "sox", "-n", "-r", "24000", "-c", "1", wav_path,
        "synth", "1", "sine", "440"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    yield wav_path
    
    # Cleanup
    Path(wav_path).unlink(missing_ok=True)


def test_fx_with_default_chorus(sample_audio):
    """Test audio processing with default chorus settings (should work)."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_path = f.name
    
    try:
        # This should work with the original default (55ms)
        result = process_klatooinian(
            sample_audio, 
            out_path, 
            chorus_ms=55,
            quiet=True
        )
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
    finally:
        Path(out_path).unlink(missing_ok=True)


def test_fx_with_low_chorus(sample_audio):
    """Test audio processing with low chorus value (10ms) - this currently fails."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_path = f.name
    
    try:
        # This should work but currently fails with chorus_ms=10
        result = process_klatooinian(
            sample_audio, 
            out_path, 
            chorus_ms=10,
            quiet=True
        )
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
    finally:
        Path(out_path).unlink(missing_ok=True)


def test_fx_with_zero_chorus(sample_audio):
    """Test audio processing with no chorus (0ms)."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_path = f.name
    
    try:
        # Test with no chorus effect
        result = process_klatooinian(
            sample_audio, 
            out_path, 
            chorus_ms=0,
            quiet=True
        )
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
    finally:
        Path(out_path).unlink(missing_ok=True)


def test_fx_with_various_chorus_values(sample_audio):
    """Test audio processing with various chorus values."""
    test_values = [20, 30, 40, 50]
    
    for chorus_ms in test_values:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            out_path = f.name
        
        try:
            result = process_klatooinian(
                sample_audio, 
                out_path, 
                chorus_ms=chorus_ms,
                quiet=True
            )
            assert Path(result).exists(), f"Failed with chorus_ms={chorus_ms}"
            assert Path(result).stat().st_size > 0, f"Empty output with chorus_ms={chorus_ms}"
        finally:
            Path(out_path).unlink(missing_ok=True)



def test_fx_with_no_overdrive(sample_audio):
    """Test audio processing with no overdrive (grit_drive=0) for natural sound."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_path = f.name
    
    try:
        # Test with no overdrive effect for cleaner, more natural sound
        result = process_klatooinian(
            sample_audio, 
            out_path, 
            grit_drive=0,
            chorus_ms=0,
            quiet=True
        )
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
    finally:
        Path(out_path).unlink(missing_ok=True)


def test_fx_with_compression_mode(sample_audio):
    """Test audio processing with compression grit mode."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_path = f.name
    
    try:
        result = process_klatooinian(
            sample_audio, 
            out_path, 
            grit_drive=5,
            grit_mode="compression",
            chorus_ms=0,
            quiet=True
        )
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
    finally:
        Path(out_path).unlink(missing_ok=True)


def test_fx_with_eq_mode(sample_audio):
    """Test audio processing with EQ grit mode."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_path = f.name
    
    try:
        result = process_klatooinian(
            sample_audio, 
            out_path, 
            grit_drive=5,
            grit_mode="eq",
            chorus_ms=0,
            quiet=True
        )
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
    finally:
        Path(out_path).unlink(missing_ok=True)


def test_fx_with_combo_mode(sample_audio):
    """Test audio processing with combo grit mode (compression + EQ)."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_path = f.name
    
    try:
        result = process_klatooinian(
            sample_audio, 
            out_path, 
            grit_drive=5,
            grit_mode="combo",
            chorus_ms=0,
            quiet=True
        )
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
    finally:
        Path(out_path).unlink(missing_ok=True)
