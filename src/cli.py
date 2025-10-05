# Suppress warnings first
from .suppress_warnings import suppress_tts_loading_messages
suppress_tts_loading_messages()

import argparse
import sys
import os
from pathlib import Path
import sounddevice as sd
import soundfile as sf

from .rewrite import rewrite_to_huttese
from .synth import synth_to_wav
from .fx import process_klatooinian

def play_wav(path: str):
    data, sr = sf.read(path, dtype="float32")
    sd.play(data, sr)
    sd.wait()

def main():
    ap = argparse.ArgumentParser(prog="huttese", description="English -> Huttese-ish -> Klatooinian timbre")
    ap.add_argument("text", nargs="*", help="Text to synthesize. If omitted, reads from stdin.")
    ap.add_argument("--seed", type=int, default=42, help="Deterministic rewrite seed")
    ap.add_argument("--semitones", type=int, default=-5, help="Pitch shift in semitones (formant-preserved)")
    ap.add_argument("--grit-drive", type=int, default=5, help="Grit intensity (0=none, 1-10=amount)")
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
    args = ap.parse_args()

    raw_text = " ".join(args.text) if args.text else sys.stdin.read().strip()
    if not raw_text:
        print("No input text.", file=sys.stderr); sys.exit(1)

    hut = rewrite_to_huttese(raw_text, seed=args.seed)
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
        synth_to_wav(hut, tmp_raw)  # 24kHz raw TTS
        process_klatooinian(tmp_raw, str(out_path),
                            semitones=args.semitones,
                            grit_drive=args.grit_drive,
                            grit_color=args.grit_color,
                            grit_mode=args.grit_mode,
                            chorus_ms=args.chorus_ms, tempo=args.tempo)
    finally:
        if args.quiet:
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    Path(tmp_raw).unlink(missing_ok=True)

    print(f"Rendered: {args.out}")
    if args.play:
        play_wav(args.out)

if __name__ == "__main__":
    main()
