import subprocess
import shutil
import os
from pathlib import Path

def ensure_tool(name: str):
    if shutil.which(name) is None:
        raise RuntimeError(f"Required tool '{name}' not found in PATH")

def process_klatooinian(in_wav: str, out_wav: str, semitones: int = -3,
                        grit_drive: int = 5, grit_color: int = 10,
                        chorus_ms: int = 20, grit_mode: str = "overdrive",
                        tempo: float = 1.0, quiet: bool = True):
    """
    rubberband for pitch/formant, sox for grit/chorus/EQ.
    
    Note: Sox requires chorus delay to be > 20ms. If chorus_ms is 0, 
    the chorus effect is skipped entirely. If it's between 1-19, it's 
    clamped to 20ms (the minimum sox allows).
    
    If grit_drive is 0, the grit effect is skipped entirely for
    a cleaner, more natural sound.
    
    tempo: Speed multiplier (1.0 = normal, 1.1 = 10% faster, 0.9 = 10% slower)
    
    grit_mode options:
    - "overdrive": Classic distortion (creates harmonics, "doubled" effect)
    - "compression": Compression for punch without harmonics
    - "eq": Mid-range boost for presence/edge
    - "combo": Compression + EQ (gravelly without doubling)
    """
    ensure_tool("rubberband")
    ensure_tool("sox")
    tmp = str(Path(in_wav).with_suffix(".pitch.wav"))

    # Prepare subprocess kwargs for quiet mode
    subprocess_kwargs = {
        "check": True,
        "stdout": subprocess.DEVNULL if quiet else None,
        "stderr": subprocess.DEVNULL if quiet else None
    }

    # Pitch shift, preserve formants, adjust tempo
    subprocess.run([
        "rubberband", "-t", str(tempo), "-p", str(semitones), "-F",
        "--quiet",  # Suppress rubberband progress output
        in_wav, tmp
    ], **subprocess_kwargs)

    # Build sox command starting with input/output
    sox_cmd = ["sox", tmp, out_wav]
    
    # Add grit effect based on mode (only if grit_drive > 0)
    if grit_drive > 0:
        if grit_mode == "overdrive":
            # Classic overdrive distortion
            sox_cmd.extend(["overdrive", str(grit_drive), str(grit_color)])
        elif grit_mode == "compression":
            # Gentler compression for punch and presence
            # Format: attack,decay in-dB1,out-dB1,in-dB2,out-dB2
            # Changed from -60,-40,-10 to -60,-50,-10 for less aggressive boost
            sox_cmd.extend(["compand", "0.01,0.1", "-60,-50,-10"])
        elif grit_mode == "eq":
            # Mid-range boost for presence and edge
            # Boost around 2.5kHz (presence range)
            boost_db = min(grit_drive, 8)  # Cap at +8dB
            sox_cmd.extend(["equalizer", "2500", "1000q", f"+{boost_db}"])
        elif grit_mode == "combo":
            # Gentler compression + EQ for gravelly sound without doubling
            sox_cmd.extend(["compand", "0.01,0.1", "-60,-50,-10"])
            boost_db = min(grit_drive, 6)  # Slightly lower for combo
            sox_cmd.extend(["equalizer", "2500", "1000q", f"+{boost_db}"])
    
    # Add chorus only if chorus_ms > 0
    # Sox requires chorus delay > 20ms, so clamp to minimum if needed
    if chorus_ms > 0:
        effective_chorus = max(20, chorus_ms)  # Clamp to sox minimum
        # Sox chorus format: gain-in gain-out delay decay speed depth [ -s | -t ]
        sox_cmd.extend(["chorus", "0.6", "0.9", str(effective_chorus), "0.4", "0.25", "2", "-t"])


    # Add EQ (bass+3 treble-2)
    sox_cmd.extend(["bass", "+3", "treble", "-2"])
    
    # Reduce output volume by 4dB
    sox_cmd.extend(["gain", "-4"])
    
    subprocess.run(sox_cmd, **subprocess_kwargs)

    Path(tmp).unlink(missing_ok=True)
    return out_wav
