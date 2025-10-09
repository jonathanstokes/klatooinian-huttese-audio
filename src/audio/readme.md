# Audio Feature: Text-to-Translated-Audio

Transform English text into "Huttese-ish" speech with a Klatooinian timbre.

## Features

- **Interactive REPL mode**: Type sentences and hear them spoken immediately
- **Rule-based text rewriting**: Deterministic English → "Huttese-ish" transformation
- **Multiple TTS engines**: Kokoro (fast GPU), Coqui XTTS v2 (high quality), macOS 'say' (instant)
- **Audio post-processing**: Pitch shifting, formant preservation, grit, chorus, and EQ
- **CLI interface**: Simple command-line tool with tunable parameters

## Quick Start

The easiest way to use this tool is the **interactive REPL mode**:

```bash
# Start the interactive mode
poetry run huttese-repl
```

Then just type any sentence and press Enter to hear it spoken in Huttese!

```
Huttese> Bring me the plans
  → barinaag me teah palanas
  ⏱️  4.7s

Huttese> You will pay for this
  → you wilaal pay porah tis
  ⏱️  6.2s
```

## Usage

### Interactive Mode (Recommended!)

The interactive REPL is the easiest and most fun way to use the tool:

```bash
poetry run huttese-repl
```

**Features:**
- 🚀 **Fast** - Model loads once, then stays in memory
- 🎨 **Colored prompt** - Easy to see what you're typing
- 📝 **Shows translation** - See the Huttese text before hearing it
- ⏱️ **Timing info** - See how long each synthesis took
- 🎛️ **Configurable** - Change settings on the fly

**Commands:**
- `<text>` - Speak text in Huttese
- `help` - Show help
- `quit` / `exit` / `q` - Exit
- `engine <name>` - Set TTS engine: kokoro (default), coqui, simple
- `voice <name>` - Set voice (depends on engine)
- `seed <n>` - Change rewrite seed (for variation)
- `semitones <n>` - Change pitch shift
- `tempo <n>` - Set speed multiplier (1.0=normal, 0.9=10% slower)
- `verbose on/off` - Toggle verbose timing mode

### Single Command Mode

For one-off synthesis or scripting:

```bash
# Synthesize and play a line
poetry run huttese 'Bring me the plans, quickly!' --play

# Choose TTS engine
poetry run huttese 'Your text' --engine kokoro --play
poetry run huttese 'Your text' --engine coqui --play
poetry run huttese 'Your text' --engine simple --play

# Choose voice (engine-specific)
poetry run huttese 'Your text' --engine kokoro --voice am_michael --play
poetry run huttese 'Your text' --engine simple --voice Alex --play

# Save to a specific file
poetry run huttese 'Your text here' --out my_audio.wav

# Dry run (just show the rewritten text)
poetry run huttese 'Your text here' --dry-run

# Quiet mode (suppress verbose output)
poetry run huttese 'Your text here' --out output.wav --quiet
```

**⚠️ Important: Use single quotes (`'`) for text with exclamation marks!**

### Tuning Parameters

Customize the voice characteristics:

```bash
# Adjust pitch (semitones, default: -5)
poetry run huttese 'Your text' --semitones -4 --play

# Adjust grit/saturation (default: drive=5, color=10)
poetry run huttese 'Your text' --grit-drive 7 --grit-color 12 --play

# Adjust grit mode (default: combo)
poetry run huttese 'Your text' --grit-mode overdrive --play
poetry run huttese 'Your text' --grit-mode compression --play
poetry run huttese 'Your text' --grit-mode eq --play
poetry run huttese 'Your text' --grit-mode combo --play

# Adjust chorus thickness (milliseconds, default: 0)
poetry run huttese 'Your text' --chorus-ms 20 --play

# Adjust tempo/speed (default: 0.9 = 10% slower)
poetry run huttese 'Your text' --tempo 1.0 --play

# Change rewrite seed for variation (default: 42)
poetry run huttese 'Your text' --seed 99 --play

# Combine multiple parameters
poetry run huttese 'Your text' --semitones -4 --grit-drive 7 --seed 100 --play
```

## TTS Engines

### Kokoro (Default - Fast GPU)

Fast, high-quality TTS using PyTorch with MPS (Apple Silicon GPU) support.

**Available voices:**
- `am_michael` (default) - Best male voice
- `am_fenrir`, `am_puck` - Good alternatives
- `af_bella` - Highest quality female
- `af_heart` - High quality female

```bash
poetry run huttese 'Your text' --engine kokoro --voice am_michael --play
```

### Coqui XTTS v2 (High Quality)

High-quality neural TTS with multi-speaker support.

```bash
poetry run huttese 'Your text' --engine coqui --play
```

### Simple (macOS 'say' - Instant)

Uses macOS built-in `say` command. No model download required.

**Available voices:**
- `Alex` (default) - Male voice
- `Zoe` - Female voice (premium)
- `Samantha` - Female voice
- `Daniel` - Male voice (British)

```bash
poetry run huttese 'Your text' --engine simple --voice Alex --play
```

## How It Works

### 1. Text Translation (translation.py)

English text is transformed using rule-based patterns:

- **Stop word removal**: Common words like "the", "a", "is" are removed to shorten output
- **Word swapping**: Systematic word order changes to sound less English-like
- **Consonant cluster breaking**: "bring" → "barinaag"
- **Vowel lengthening**: "me" → "meah"
- **Character substitutions**: 
  - th → t ("the" → "te")
  - f → p ("for" → "porah")
  - v → b ("very" → "bery")
- **Word ending variations**: Adding -ah, -oo suffixes
- **Deterministic with seed**: Same input + seed = same output
- **Literal phrase preservation**: Text in quotes or LITERAL_PHRASES env var is preserved

### 2. Neural TTS Synthesis (engines/)

The rewritten text is synthesized using one of three engines:

**Kokoro** (engines/kokoro.py):
- PyTorch with MPS (Metal Performance Shaders) for GPU acceleration on Apple Silicon
- 24kHz output
- Multiple voice options

**Coqui XTTS v2** (engines/coqui.py):
- Multilingual, multi-speaker model
- "Claribel Dervla" speaker (default)
- 24kHz output
- CPU-based (Apple Silicon optimized)

**Simple** (engines/simple.py):
- macOS built-in `say` command
- No model download required
- Instant synthesis
- Multiple system voices

### 3. Audio Post-Processing (effects.py)

Multiple effects are applied to create the Klatooinian timbre:

1. **Pitch shift** (rubberband): Lower pitch while preserving formants
2. **Grit effects** (sox):
   - `overdrive`: Classic distortion (creates harmonics, "doubled" effect)
   - `compression`: Compression for punch without harmonics
   - `eq`: Mid-range boost for presence/edge
   - `combo`: Compression + EQ (gravelly without doubling)
3. **Chorus** (sox): Add thickness and depth (optional)
4. **EQ** (sox): Boost bass, cut treble for deeper tone

## Recommended Settings

After testing, these parameters produce a convincing Klatooinian timbre:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--engine` | `kokoro` | TTS engine (kokoro/coqui/simple) |
| `--voice` | `am_michael` | Voice (engine-specific) |
| `--semitones` | `-5` | Deeper voice (try -2 to -7) |
| `--grit-drive` | `5` | Moderate saturation (try 0-10) |
| `--grit-color` | `10` | Warm tone (try 8-12) |
| `--grit-mode` | `combo` | Grit mode (overdrive/compression/eq/combo) |
| `--chorus-ms` | `0` | Chorus thickness (try 0-70) |
| `--tempo` | `0.9` | Speed (1.0=normal, 0.9=10% slower) |
| `--seed` | `42` | Text variation (any integer) |

### Voice Presets

**Deep & Gravelly:**
```bash
poetry run huttese 'Your text' --semitones -5 --grit-drive 7 --grit-mode combo --play
```

**Smooth & Resonant:**
```bash
poetry run huttese 'Your text' --semitones -2 --grit-drive 3 --grit-mode compression --chorus-ms 20 --play
```

**Clean & Natural:**
```bash
poetry run huttese 'Your text' --semitones -3 --grit-drive 0 --chorus-ms 0 --play
```

## Environment Variables

### LITERAL_PHRASES

Comma-separated list of phrases to preserve as-is during translation:

```bash
# In .env file
LITERAL_PHRASES="Star Wars,Hendo,Millennium Falcon"

# Or set directly
export LITERAL_PHRASES="Star Wars,Hendo"
poetry run huttese "I love Star Wars movies" --dry-run
# Output: love Star Wars movies
```

Phrases are case-insensitive for matching but preserve original case in output.

## Module Structure

```
src/audio/
├── __init__.py              # Package exports
├── translation.py           # Huttese translation logic
├── effects.py               # Audio post-processing
├── engines/                 # TTS engine implementations
│   ├── __init__.py
│   ├── kokoro.py           # Kokoro TTS (fast GPU)
│   ├── coqui.py            # Coqui XTTS v2 (high quality)
│   └── simple.py           # macOS 'say' (instant)
└── README.md               # This file
```

## Performance

- **First synthesis (Kokoro)**: ~3-5 seconds (includes model loading)
- **First synthesis (Coqui)**: ~5-8 seconds (includes model loading)
- **First synthesis (Simple)**: ~1-2 seconds (no model loading)
- **Subsequent syntheses (REPL)**: ~2-4 seconds (model stays loaded)
- **Model size (Kokoro)**: ~200MB
- **Model size (Coqui)**: ~1.8GB (cached after first download)
- **Memory usage**: ~2-3GB during synthesis

## Troubleshooting

### Audio Tools Not Found

**"rubberband not found" / "sox not found"**

macOS:
```bash
brew install ffmpeg sox rubberband
```

Linux:
```bash
sudo apt install -y ffmpeg sox rubberband-cli libsndfile1
```

### Network Issues / HuggingFace Blocked

If you're on a corporate network that blocks HuggingFace, use the simple engine:

```bash
poetry run huttese "Your text" --engine simple --play
```

### Audio Quality Issues

**Harsh or metallic tone:**
- Reduce pitch shift: `--semitones -2`
- Reduce grit: `--grit-drive 3`
- Try different grit mode: `--grit-mode compression`

**Too quiet or distorted:**
- Check system volume
- Try different grit settings
- Reduce overdrive: `--grit-drive 3`

**Doubled/echoing effect:**
- Use `--grit-mode combo` instead of `overdrive`
- Reduce chorus: `--chorus-ms 0`

## Examples

### Example 1: Basic Usage

```bash
$ poetry run huttese "Bring me Solo and the Wookiee" --play
Rendered: out/out_fx.wav
```

### Example 2: Custom Voice

```bash
$ poetry run huttese "You will pay for this" \
    --engine kokoro \
    --voice am_michael \
    --semitones -5 \
    --grit-drive 8 \
    --out jabba_voice.wav \
    --play
```

### Example 3: Interactive Session

```bash
$ poetry run huttese-repl
Huttese> This bounty hunter is my kind of scum
  → bounty hunatarare kinaad scum
  ⏱️  3.3s

Huttese> engine simple
✓ Engine set to simple (macOS say)

Huttese> voice Zoe
✓ Voice set to Zoe

Huttese> This bounty hunter is my kind of scum
  → bounty hunatarare kinaad scum
  ⏱️  1.8s
```

### Example 4: Batch Processing

```bash
# Process multiple variations
for seed in 42 100 200; do
  poetry run huttese "Bring me the plans" \
    --seed $seed \
    --out "plans_${seed}.wav"
done
```

## Future Enhancements

