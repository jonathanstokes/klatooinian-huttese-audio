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
from .fx import process_klatooinian


def play_wav(path: str):
    """Play a WAV file."""
    data, sr = sf.read(path, dtype="float32")
    sd.play(data, sr)
    sd.wait()


def print_banner(engine_name):
    """Print welcome banner."""
    print("=" * 60)
    print("  🎙️  Klatooinian Huttese Speech Synthesizer")
    print("=" * 60)
    print()
    print(f"Engine: {engine_name}")
    print("Loading TTS model (this may take a moment)...")


def print_help():
    """Print help message."""
    print()
    print("Commands:")
    print("  <text>         - Speak text in Huttese")
    print("  help           - Show this help")
    print("  quit/exit/q    - Exit the program")
    print("  engine <name>  - Set TTS engine: kokoro (default), coqui, simple")
    print("  voice <name>   - Set voice (depends on engine)")
    print("  seed <n>       - Set rewrite seed (default: 42)")
    print("  semitones <n>  - Set pitch shift (default: -5)")
    print("  tempo <n>      - Set speed multiplier (default: 0.9, 1.0=normal)")
    print("  verbose on/off - Toggle verbose timing mode (default: off)")
    print()


def main():
    """Run interactive REPL."""
    # REPL state
    engine = "kokoro"  # Default engine
    voice = "am_michael"  # Default voice for kokoro
    engine_name = "Kokoro TTS"
    synth_to_wav = None

    # Print banner
    print_banner(engine_name)

    # Pre-load TTS model
    try:
        from .synth_f5 import synth_to_wav as kokoro_synth
        synth_to_wav = kokoro_synth
        print("✓ Model loaded successfully!")
        print()
        print("Type a sentence and press Enter to hear it in Huttese.")
        print("Type 'help' for commands, 'quit' to exit.")
        print()
    except Exception as e:
        print(f"✗ Error loading TTS model: {e}")
        sys.exit(1)

    # Other REPL state
    seed = 42
    semitones = -5
    grit_drive = 5
    grit_color = 10
    chorus_ms = 0
    grit_mode = "combo"  # Default to combo mode for gravelly without doubling
    tempo = 0.9  # default: 10% faster
    verbose = False  # verbose timing mode
    
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

            if text.lower().startswith("engine "):
                try:
                    new_engine = text.split()[1].lower()
                    if new_engine not in ["kokoro", "coqui", "simple"]:
                        print("✗ Invalid engine. Choose: kokoro, coqui, simple")
                        continue

                    engine = new_engine

                    # Load appropriate synth module
                    if engine == "kokoro":
                        from .synth_f5 import synth_to_wav as kokoro_synth
                        synth_to_wav = kokoro_synth
                        engine_name = "Kokoro TTS"
                        voice = "am_michael"  # Reset to default kokoro voice
                    elif engine == "coqui":
                        from .synth import synth_to_wav as coqui_synth
                        synth_to_wav = coqui_synth
                        engine_name = "Coqui XTTS v2"
                        voice = None  # Coqui doesn't use voice parameter
                    else:  # simple
                        from .synth_simple import synth_to_wav as simple_synth
                        synth_to_wav = simple_synth
                        engine_name = "macOS say"
                        voice = "Alex"  # Reset to default macOS voice

                    print(f"✓ Engine set to {engine_name}")
                except (ValueError, IndexError):
                    print("✗ Usage: engine kokoro|coqui|simple")
                continue

            if text.lower().startswith("voice "):
                try:
                    voice = text.split(maxsplit=1)[1]
                    print(f"✓ Voice set to {voice}")
                except IndexError:
                    print("✗ Usage: voice <name>")
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

            if text.lower().startswith("verbose "):
                try:
                    mode = text.split()[1].lower()
                    if mode == "on":
                        verbose = True
                        print("✓ Verbose timing mode enabled")
                    elif mode == "off":
                        verbose = False
                        print("✓ Verbose timing mode disabled")
                    else:
                        print("✗ Usage: verbose on|off")
                except IndexError:
                    print("✗ Usage: verbose on|off")
                continue

            # Process text
            start_time = time.time()

            # Rewrite
            if verbose:
                print("  \033[2m⏱️  Starting rewrite...\033[0m")
            step_start = time.time()
            huttese = rewrite_to_huttese(text, seed=seed)
            if verbose:
                print(f"  \033[2m⏱️  Rewrite: {time.time() - step_start:.3f}s\033[0m")
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
                    if verbose:
                        # Temporarily restore stdout for verbose message
                        sys.stdout.close()
                        sys.stdout = old_stdout
                        print("  \033[2m⏱️  Starting synthesis...\033[0m")
                        sys.stdout = open("/dev/null", "w")

                    step_start = time.time()
                    # Pass voice parameter for kokoro and simple engines
                    if engine == "kokoro" or engine == "simple":
                        synth_to_wav(huttese, str(tmp_raw), voice=voice)
                    else:  # coqui
                        synth_to_wav(huttese, str(tmp_raw))
                    synth_time = time.time() - step_start

                    if verbose:
                        sys.stdout.close()
                        sys.stdout = old_stdout
                        print(f"  \033[2m⏱️  Synthesis: {synth_time:.3f}s\033[0m")
                        print("  \033[2m⏱️  Starting FX processing...\033[0m")
                        sys.stdout = open("/dev/null", "w")

                    step_start = time.time()
                    process_klatooinian(
                        str(tmp_raw), str(tmp_fx),
                        semitones=semitones,
                        grit_drive=grit_drive,
                        grit_color=grit_color,
                        chorus_ms=chorus_ms,
                        grit_mode=grit_mode,
                        tempo=tempo,
                    )
                    fx_time = time.time() - step_start

                    if verbose:
                        sys.stdout.close()
                        sys.stdout = old_stdout
                        print(f"  \033[2m⏱️  FX processing: {fx_time:.3f}s\033[0m")
                        sys.stdout = open("/dev/null", "w")
                finally:
                    sys.stdout.close()
                    sys.stderr.close()
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

                # Play
                if verbose:
                    print("  \033[2m⏱️  Playing audio...\033[0m")
                step_start = time.time()
                play_wav(str(tmp_fx))
                play_time = time.time() - step_start

                elapsed = time.time() - start_time
                if verbose:
                    print(f"  \033[2m⏱️  Playback: {play_time:.3f}s\033[0m")
                    print(f"  \033[2m⏱️  Total: {elapsed:.3f}s\033[0m")
                else:
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
