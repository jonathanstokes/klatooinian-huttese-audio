import argparse
import sys
import time
from pathlib import Path
import sounddevice as sd
import soundfile as sf

from .rewrite import rewrite_to_huttese
from .synth_simple import synth_to_wav
from .fx import process_klatooinian

def play_wav(path: str):
    data, sr = sf.read(path, dtype="float32")
    sd.play(data, sr)
    sd.wait()

def main():
    ap = argparse.ArgumentParser(prog="huttese-simple", description="English -> Huttese-ish -> Klatooinian timbre (using macOS say)")
    ap.add_argument("text", nargs="*", help="Text to synthesize. If omitted, reads from stdin.")
    ap.add_argument("--seed", type=int, default=42, help="Deterministic rewrite seed")
    ap.add_argument("--semitones", type=int, default=-3, help="Pitch shift in semitones (formant-preserved)")
    ap.add_argument("--grit-drive", type=int, default=5, help="Saturation drive")
    ap.add_argument("--grit-color", type=int, default=10, help="Saturation color")
    ap.add_argument("--chorus-ms", type=int, default=55, help="Chorus delay (ms)")
    ap.add_argument("--dry-run", action="store_true", help="Only print rewritten text")
    ap.add_argument("--out", default="out_fx.wav", help="Output WAV path")
    ap.add_argument("--play", action="store_true", help="Play result after rendering")
    ap.add_argument("--verbose", action="store_true", help="Show timing information for each step")
    args = ap.parse_args()

    raw_text = " ".join(args.text) if args.text else sys.stdin.read().strip()
    if not raw_text:
        print("No input text.", file=sys.stderr); sys.exit(1)

    # Start timing
    total_start = time.time()

    # Rewrite step
    if args.verbose:
        print("⏱️  Starting rewrite...")
    step_start = time.time()
    hut = rewrite_to_huttese(raw_text, seed=args.seed)
    if args.verbose:
        print(f"⏱️  Rewrite: {time.time() - step_start:.3f}s")

    if args.dry_run:
        print(hut)
        sys.exit(0)

    tmp_raw = str(Path(args.out).with_suffix(".raw.wav"))

    # Synthesis step
    if args.verbose:
        print("⏱️  Starting synthesis (macOS say)...")
    step_start = time.time()
    synth_to_wav(hut, tmp_raw)  # 24kHz raw TTS using macOS 'say'
    if args.verbose:
        print(f"⏱️  Synthesis: {time.time() - step_start:.3f}s")

    # FX processing step
    if args.verbose:
        print("⏱️  Starting FX processing...")
    step_start = time.time()
    process_klatooinian(tmp_raw, args.out,
                        semitones=args.semitones,
                        grit_drive=args.grit_drive,
                        grit_color=args.grit_color,
                        chorus_ms=args.chorus_ms)
    if args.verbose:
        print(f"⏱️  FX processing: {time.time() - step_start:.3f}s")

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

