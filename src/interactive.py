#!/usr/bin/env python3
"""
Interactive REPL for Huttese speech synthesis.
Type sentences and hear them spoken in Klatooinian-accented Huttese.
"""
# Suppress warnings first
from .suppress_warnings import suppress_tts_loading_messages
suppress_tts_loading_messages()

import sys
import time
from pathlib import Path
import sounddevice as sd
import soundfile as sf

from .rewrite import rewrite_to_huttese
from .synth import synth_to_wav
from .fx import process_klatooinian


def play_wav(path: str):
    """Play a WAV file."""
    data, sr = sf.read(path, dtype="float32")
    sd.play(data, sr)
    sd.wait()


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("  🎙️  Klatooinian Huttese Speech Synthesizer")
    print("=" * 60)
    print()
    print("Loading neural TTS model (this may take a moment)...")


def print_help():
    """Print help message."""
    print()
    print("Commands:")
    print("  <text>        - Speak text in Huttese")
    print("  help          - Show this help")
    print("  quit/exit/q   - Exit the program")
    print("  seed <n>      - Set rewrite seed (default: 42)")
    print("  semitones <n> - Set pitch shift (default: -5)")
    print("  tempo <n>     - Set speed multiplier (default: 0.9, 1.0=normal)")
    print()


def main():
    """Run interactive REPL."""
    # Print banner
    print_banner()
    
    # Pre-load TTS model
    try:
        from TTS.api import TTS
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        print("✓ Model loaded successfully!")
        print()
        print("Type a sentence and press Enter to hear it in Huttese.")
        print("Type 'help' for commands, 'quit' to exit.")
        print()
    except Exception as e:
        print(f"✗ Error loading TTS model: {e}")
        sys.exit(1)
    
    # REPL state
    seed = 42
    semitones = -5
    grit_drive = 5
    grit_color = 10
    chorus_ms = 0
    grit_mode = "combo"  # Default to combo mode for gravelly without doubling
    tempo = 0.9  # default: 10% faster
    
    # Temporary files
    tmp_dir = Path("/tmp/huttese_repl")
    tmp_dir.mkdir(exist_ok=True)
    
    while True:
        try:
            # Prompt
            text = input("\033[1;36mHuttese>\033[0m ")
            text = text.strip()
            
            if not text:
                continue
            
            # Commands
            if text.lower() in ("quit", "exit", "q"):
                print("👋 Goodbye!")
                break
            
            if text.lower() == "help":
                print_help()
                continue
            
            if text.lower().startswith("seed "):
                try:
                    seed = int(text.split()[1])
                    print(f"✓ Rewrite seed set to {seed}")
                except (ValueError, IndexError):
                    print("✗ Usage: seed <number>")
                continue
            
            if text.lower().startswith("semitones "):
                try:
                    semitones = int(text.split()[1])
                    print(f"✓ Pitch shift set to {semitones} semitones")
                except (ValueError, IndexError):
                    print("✗ Usage: semitones <number>")
                continue
            
            if text.lower().startswith("tempo "):
                try:
                    tempo = float(text.split()[1])
                    print(f"✓ Tempo set to {tempo}x (1.0=normal)")
                except (ValueError, IndexError):
                    print("✗ Usage: tempo <number>")
                continue
            
            # Process text
            start_time = time.time()
            
            # Rewrite
            huttese = rewrite_to_huttese(text, seed=seed)
            print(f"  \033[2m→ {huttese}\033[0m")
            
            # Synthesize
            tmp_raw = tmp_dir / f"raw_{int(time.time() * 1000)}.wav"
            tmp_fx = tmp_dir / f"fx_{int(time.time() * 1000)}.wav"
            
            try:
                # Suppress TTS output
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = open("/dev/null", "w")
                sys.stderr = open("/dev/null", "w")
                
                try:
                    synth_to_wav(huttese, str(tmp_raw))
                    
                    process_klatooinian(
                        str(tmp_raw), str(tmp_fx),
                        semitones=semitones,
                        grit_drive=grit_drive,
                        grit_color=grit_color,
                        chorus_ms=chorus_ms,
                        grit_mode=grit_mode,
                        tempo=tempo,
                    )
                finally:
                    sys.stdout.close()
                    sys.stderr.close()
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                
                # Play
                play_wav(str(tmp_fx))
                
                elapsed = time.time() - start_time
                print(f"  \033[2m⏱️  {elapsed:.1f}s\033[0m")
                print()
                
            finally:
                # Cleanup
                tmp_raw.unlink(missing_ok=True)
                tmp_fx.unlink(missing_ok=True)
        
        except KeyboardInterrupt:
            print()
            print("👋 Goodbye!")
            break
        except EOFError:
            print()
            print("👋 Goodbye!")
            break
        except Exception as e:
            print(f"✗ Error: {e}")
            continue


if __name__ == "__main__":
    main()
