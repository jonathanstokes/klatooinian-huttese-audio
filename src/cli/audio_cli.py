# Suppress warnings first
from ..common.suppress_warnings import suppress_tts_loading_messages
suppress_tts_loading_messages()

import argparse
import sys
import os
import time
from pathlib import Path
import sounddevice as sd
import soundfile as sf

from ..audio.translation import rewrite_to_huttese
from ..audio.effects import process_klatooinian

def play_wav(path: str):
    data, sr = sf.read(path, dtype="float32")
    sd.play(data, sr)
    sd.wait()

def main():
    ap = argparse.ArgumentParser(prog="huttese", description="English -> Huttese-ish -> Klatooinian timbre")
    ap.add_argument("text", nargs="*", help="Text to synthesize. If omitted, reads from stdin.")
    ap.add_argument("--engine", type=str, default="simple",
                    choices=["kokoro", "coqui", "simple"],
                    help="TTS engine: kokoro (Kokoro TTS, fast GPU), coqui (XTTS v2, high quality), simple (macOS say, instant)")
    ap.add_argument("--voice", type=str, default="Lee",
                    help="Voice to use. Kokoro: am_michael (default), hm_omega, jm_kumo, etc. Simple: Alex (default), Zoe, Samantha, Daniel, etc.")
    ap.add_argument("--seed", type=int, default=42, help="Deterministic rewrite seed")
    ap.add_argument("--no-strip-stop-words", action="store_true", help="Disable stop word removal (keep all words)")
    ap.add_argument("--strip-every-nth", type=int, default=3, help="Strip every Nth word (0=disabled, 3=every 3rd word, etc.)")
    ap.add_argument("--semitones", type=int, default=-2, help="Pitch shift in semitones (formant-preserved)")
    ap.add_argument("--grit-drive", type=int, default=0, help="Grit intensity (0=none, 1-10=amount)")
    ap.add_argument("--grit-color", type=int, default=10, help="Grit color/tone")
    ap.add_argument("--grit-mode", type=str, default="combo",
                    choices=["overdrive", "compression", "eq", "combo"],
                    help="Grit mode: overdrive (classic, doubled), compression (punch), eq (presence), combo (gravelly without doubling)")
    ap.add_argument("--chorus-ms", type=int, default=0, help="Chorus delay (ms)")
    ap.add_argument("--tempo", type=float, default=0.9, help="Speed multiplier (1.0=normal, 1.1=10%% faster)")
    ap.add_argument("--dry-run", action="store_true", help="Only print rewritten text")
    ap.add_argument("--out", default="out/out_fx.wav", help="Output WAV path")
    ap.add_argument("--play", action="store_true", help="Play result after rendering")
    ap.add_argument("--quiet", action="store_true", help="Suppress TTS output messages")
    ap.add_argument("--verbose", action="store_true", help="Show timing information for each step")
    args = ap.parse_args()

    raw_text = " ".join(args.text) if args.text else sys.stdin.read().strip()
    if not raw_text:
        print("No input text.", file=sys.stderr); sys.exit(1)

    # Import the appropriate synth module based on engine choice
    if args.engine == "kokoro":
        from ..audio.engines.kokoro import synth_to_wav
        engine_name = "Kokoro TTS"
    elif args.engine == "coqui":
        from ..audio.engines.coqui import synth_to_wav
        engine_name = "Coqui XTTS v2"
    else:  # simple
        from ..audio.engines.simple import synth_to_wav
        engine_name = "macOS say"

    # Start timing
    total_start = time.time()

    # Rewrite step
    if args.verbose:
        print("⏱️  Starting rewrite...")
    step_start = time.time()
    hut = rewrite_to_huttese(
        raw_text,
        seed=args.seed,
        strip_stop_words=not args.no_strip_stop_words,
        strip_every_nth=args.strip_every_nth
    )
    if args.verbose:
        print(f"⏱️  Rewrite: {time.time() - step_start:.3f}s")
        print(f"📝 Translated: {hut}")
        print()

    if args.dry_run:
        print(hut)
        sys.exit(0)

    # Ensure output directory exists
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_raw = str(out_path.with_suffix(".raw.wav"))

    # Optionally suppress TTS output
    if args.quiet:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    try:
        # Synthesis step
        if args.verbose:
            print(f"⏱️  Starting synthesis ({engine_name})...")
        step_start = time.time()
        # Pass voice parameter for Kokoro and Simple engines
        if args.engine == "kokoro":
            voice = args.voice if args.voice else "am_michael"
            synth_to_wav(hut, tmp_raw, voice=voice)
        elif args.engine == "simple":
            voice = args.voice if args.voice else "Alex"
            synth_to_wav(hut, tmp_raw, voice=voice)
        else:  # coqui
            synth_to_wav(hut, tmp_raw)  # 24kHz raw TTS
        if args.verbose:
            print(f"⏱️  Synthesis: {time.time() - step_start:.3f}s")

        # FX processing step
        if args.verbose:
            print("⏱️  Starting FX processing...")
        step_start = time.time()
        process_klatooinian(tmp_raw, str(out_path),
                            semitones=args.semitones,
                            grit_drive=args.grit_drive,
                            grit_color=args.grit_color,
                            grit_mode=args.grit_mode,
                            chorus_ms=args.chorus_ms, tempo=args.tempo)
        if args.verbose:
            print(f"⏱️  FX processing: {time.time() - step_start:.3f}s")
    finally:
        if args.quiet:
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    Path(tmp_raw).unlink(missing_ok=True)

    if args.verbose:
        print(f"⏱️  Total: {time.time() - total_start:.3f}s")
        print()

    print(f"Rendered: {args.out}")
    if args.play:
        if args.verbose:
            print("⏱️  Playing audio...")
        step_start = time.time()
        play_wav(args.out)
        if args.verbose:
            print(f"⏱️  Playback: {time.time() - step_start:.3f}s")

if __name__ == "__main__":
    main()

