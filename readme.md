# Klatooinian Huttese Audio CLI

A command-line tool that transforms English text into "Huttese-ish" speech with a Klatooinian timbre.

## Features

- **Interactive REPL mode**: Type sentences and hear them spoken immediately
- **Rule-based text rewriting**: Deterministic English → "Huttese-ish" transformation
- **Neural TTS**: Uses Coqui XTTS v2 for high-quality speech synthesis
- **Audio post-processing**: Pitch shifting, formant preservation, grit, chorus, and EQ
- **CLI interface**: Simple command-line tool with tunable parameters
- **Modern dependencies**: Uses actively maintained coqui-tts fork (0.27.2)

## Quick Start

The easiest way to use this tool is the **interactive REPL mode**:

```bash
# Install dependencies (first time only)
poetry install

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

## Setup

### Prerequisites

**macOS:**
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install system dependencies (audio processing tools)
brew install ffmpeg sox rubberband
```

**Ubuntu/Debian Linux:**
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install system dependencies
sudo apt update
sudo apt install -y ffmpeg sox rubberband-cli libsndfile1
```

### Install Python dependencies

```bash
# Install all Python dependencies (creates virtual environment automatically)
poetry install
```

## Usage

### Interactive Mode (Recommended!)

The interactive REPL is the easiest and most fun way to use the tool:

```bash
poetry run huttese-repl

# Or use the Makefile shortcut
make repl
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
- `seed <n>` - Change rewrite seed (for variation)
- `semitones <n>` - Change pitch shift

**Example Session:**

```
$ poetry run huttese-repl
============================================================
  🎙️  Klatooinian Huttese Speech Synthesizer
============================================================

Loading neural TTS model (this may take a moment)...
✓ Model loaded successfully!

Type a sentence and press Enter to hear it in Huttese.
Type 'help' for commands, 'quit' to exit.

Huttese> Bring me the plans
  → barinaag me teah palanas
  ⏱️  4.7s

Huttese> seed 100
✓ Seed set to 100

Huttese> Bring me the plans
  → barinaag meah te palanas
  ⏱️  4.5s

Huttese> quit
👋 Goodbye!
```

### Single Command Mode

For one-off synthesis or scripting:

```bash
# Synthesize and play a line
poetry run huttese 'Bring me the plans, quickly!' --play

# Save to a specific file
poetry run huttese 'Your text here' --out my_audio.wav

# Save and play
poetry run huttese 'Your text here' --out my_audio.wav --play

# Dry run (just show the rewritten text)
poetry run huttese 'Your text here' --dry-run

# Quiet mode (suppress verbose output)
```

**⚠️ Important: Use single quotes (`'`) for text with exclamation marks!**

The `!` character triggers history expansion in zsh/bash. Use single quotes to avoid issues:

```bash
# ✅ Correct - single quotes
poetry run huttese 'Now I can speak Huttese!' --play

# ❌ Wrong - double quotes with ! will cause "dquote>" prompt
poetry run huttese "Now I can speak Huttese!" --play

# ✅ Alternative - escape the exclamation mark
poetry run huttese "Now I can speak Huttese\!" --play
poetry run huttese 'Your text here' --out output.wav --quiet
```

### Tuning Parameters

Customize the voice characteristics:

```bash
# Adjust pitch (semitones, default: -3)
poetry run huttese 'Your text' --semitones -4 --play

# Adjust grit/saturation (default: drive=5, color=10)
poetry run huttese 'Your text' --grit-drive 7 --grit-color 12 --play

# Adjust chorus thickness (milliseconds, default: 55)
poetry run huttese 'Your text' --chorus-ms 70 --play

# Change rewrite seed for variation (default: 42)
poetry run huttese 'Your text' --seed 99 --play

# Combine multiple parameters
poetry run huttese 'Your text' --semitones -4 --grit-drive 7 --seed 100 --play
```

### Batch Processing

Process multiple lines from a file:

```bash
# Create a file with lines to process
cat > my_lines.txt << 'END'
Bring me the plans
You will pay for this
The negotiations were short
END

# Process all lines
while read line; do
  poetry run huttese "$line" --out "output_$(echo $line | tr ' ' '_').wav"
done < my_lines.txt

# Or use the sample processing
make sample
```

### Makefile Shortcuts

```bash
# Start interactive REPL
make repl

# Run a quick test
make run

# Process all sample lines
make sample

# Run tests
make test

# Clean up generated audio files
make clean
```

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── rewrite.py          # Text rewriting rules
│   ├── synth.py            # TTS synthesis
│   ├── fx.py               # Audio post-processing
│   ├── cli.py              # CLI entry point
│   ├── interactive.py      # Interactive REPL mode
│   ├── suppress_warnings.py # Warning suppression utilities
│   └── cli_simple.py       # Fallback using macOS 'say' command
├── tests/
│   └── test_rewrite.py
├── samples/
│   └── lines.txt           # Sample lines for testing
├── pyproject.toml          # Poetry configuration
├── Makefile
└── readme.md
```

## How It Works

### 1. Text Rewriting

English text is transformed using rule-based patterns:

- **Consonant cluster breaking**: "bring" → "barinaag"
- **Vowel lengthening**: "me" → "meah"
- **Character substitutions**: 
  - th → t ("the" → "te")
  - f → p ("for" → "porah")
  - v → b ("very" → "bery")
- **Word ending variations**: Adding -ah, -oo suffixes
- **Deterministic with seed**: Same input + seed = same output

### 2. Neural TTS Synthesis

The rewritten text is synthesized using:
- **Model**: Coqui XTTS v2 (multilingual, multi-speaker)
- **Speaker**: "Claribel Dervla" (default voice)
- **Sample rate**: 24kHz
- **Language**: English phonetics

### 3. Audio Post-Processing

Multiple effects are applied to create the Klatooinian timbre:

1. **Pitch shift** (rubberband): Lower pitch while preserving formants
2. **Saturation/grit** (sox overdrive): Add vocal roughness
3. **Chorus** (sox): Add thickness and depth
4. **EQ** (sox): Boost bass, cut treble for deeper tone

## Recommended Settings

After testing, these parameters produce a convincing Klatooinian timbre:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--semitones` | `-3` | Deeper voice (try -2 to -5) |
| `--grit-drive` | `5` | Moderate saturation (try 3-7) |
| `--grit-color` | `10` | Warm tone (try 8-12) |
| `--chorus-ms` | `55` | Subtle thickness (try 40-70) |
| `--seed` | `42` | Text variation (any integer) |

### Voice Presets

**Deep & Gravelly:**
```bash
poetry run huttese 'Your text' --semitones -5 --grit-drive 7 --play
```

**Smooth & Resonant:**
```bash
poetry run huttese 'Your text' --semitones -2 --grit-drive 3 --chorus-ms 70 --play
```

**Harsh & Aggressive:**
```bash
poetry run huttese 'Your text' --semitones -4 --grit-drive 8 --grit-color 15 --play
```

## Troubleshooting

### Audio Tools Not Found

**"rubberband not found" / "sox not found"**
- Ensure tools are installed and in PATH
- Run `which rubberband` and `which sox` to verify
- Reopen your shell after installation

**macOS:**
```bash
brew install ffmpeg sox rubberband
```

**Linux:**
```bash
sudo apt install -y ffmpeg sox rubberband-cli libsndfile1
```

### Poetry Issues

**Poetry not found**
```bash
# Add Poetry to your PATH (add to ~/.zshrc or ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc  # or ~/.bashrc
```

**Dependency conflicts**
```bash
# Clean install
rm -rf poetry.lock
poetry install
```

### Audio Quality Issues

**Harsh or metallic tone**
- Reduce pitch shift: `--semitones -2`
- Reduce grit: `--grit-drive 3`
- Reduce chorus: `--chorus-ms 40`

**Too quiet or distorted**
- Check your system volume
- Try different grit settings
- Reduce overdrive: `--grit-drive 3`

**No audio playback on macOS**
- Check System Settings → Privacy & Security → Microphone
- Grant terminal app microphone/speaker access

### Network Issues / HuggingFace Blocked

If you're on a corporate network or VPN that blocks HuggingFace, use the simple version that uses macOS's built-in `say` command instead:

```bash
# Use the simple version (no model download required)
poetry run python -m src.cli_simple "Your text here" --out output.wav --play
```

The simple version produces similar results but uses macOS's Alex voice instead of the neural TTS model.

**Troubleshooting HuggingFace Connection:**

If you see `ConnectionRefusedError` when trying to download the TTS model:

1. **Check if you're on a VPN** - Try disconnecting temporarily
2. **Check corporate firewall** - HuggingFace might be blocked
3. **Use the simple version** - `src.cli_simple` instead of `src.cli`
4. **Manual download** - Download the model manually and place it in `~/.cache/tts/`

### Model Loading Issues

**First run takes a long time**
- The XTTS v2 model is ~1.8GB and downloads on first use
- Subsequent runs are fast (model is cached)
- Use `--quiet` flag to suppress download progress

**Model fails to load**
```bash
# Clear the cache and re-download
rm -rf ~/.cache/tts/
poetry run huttese "test" --play
```

## Technical Details

### Dependencies

- **Python**: 3.11-3.13
- **coqui-tts**: 0.27.2 (maintained fork)
- **transformers**: 4.55.4
- **torch**: 2.8.0
- **numpy**: 2.3.3
- **soundfile**: 0.12.0
- **sounddevice**: 0.4.0

### System Requirements

- **macOS**: 10.15+ (Catalina or later)
- **Linux**: Ubuntu 20.04+ or equivalent
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB for model cache
- **Audio**: Working audio output device

### Performance

- **First synthesis**: ~5-8 seconds (includes model loading)
- **Subsequent syntheses**: ~3-6 seconds (model stays loaded in REPL)
- **Model size**: ~1.8GB (cached after first download)
- **Memory usage**: ~2-3GB during synthesis

## Examples

### Example 1: Basic Usage

```bash
$ poetry run huttese "Bring me Solo and the Wookiee" --play
Rendered: /tmp/huttese_abc123.wav
```

### Example 2: Custom Voice

```bash
$ poetry run huttese "You will pay for this" \
    --semitones -5 \
    --grit-drive 8 \
    --out jabba_voice.wav \
    --play
```

### Example 3: Interactive Session

```bash
$ poetry run huttese-repl
Huttese> This bounty hunter is my kind of scum
  → tis bounty hunatarare is my kinaad op scum
  ⏱️  5.3s

Huttese> semitones -5
✓ Semitones set to -5

Huttese> This bounty hunter is my kind of scum
  → tis bounty hunatarare is my kinaad op scum
  ⏱️  5.1s
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

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test
poetry run pytest tests/test_rewrite.py
```

### Code Structure

- **rewrite.py**: Text transformation logic
- **synth.py**: TTS model interface (lazy singleton pattern)
- **fx.py**: Audio processing pipeline
- **cli.py**: Command-line interface
- **interactive.py**: REPL implementation
- **suppress_warnings.py**: Warning suppression utilities

## Future Enhancements

- [ ] Add preset system (`--preset jabba`, `--preset klatooinian`)
- [ ] Web interface with real-time synthesis
- [ ] Fine-tune TTS model on Star Wars audio
- [ ] Support for other alien languages (Rodian, Geonosian, etc.)
- [ ] Voice cloning from audio samples
- [ ] Real-time audio streaming
- [ ] Mobile app

## Credits

- **TTS Model**: Coqui XTTS v2 (maintained fork by Idiap Research Institute)
- **Audio Processing**: Sox, Rubberband
- **Inspiration**: Star Wars universe, Jabba's palace scenes

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

---

**May the Force be with you!** 🌟
