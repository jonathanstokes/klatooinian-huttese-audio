# Klatooinian Huttese Audio

A multi-feature toolkit for working with Huttese-style text and audio.

## Features

This project contains three main features:

### 1. 🎙️ Audio: Text-to-Translated-Audio
Transform English text into "Huttese-ish" speech with a Klatooinian timbre.
- Interactive REPL mode
- Multiple TTS engines (Kokoro, Coqui XTTS v2, macOS 'say')
- Rule-based text translation
- Audio post-processing effects
- **[See detailed documentation →](src/audio/README.md)**

### 2. 🎮 Roll20: Post-Text-to-Roll20 (Coming Soon)
Post messages to Roll20 virtual tabletop chat.
- Headless browser automation
- Automatic message formatting
- Integration with audio feature

### 3. 📝 Input: Text Input UI (Coming Soon)
Native text input interface for composing messages.
- Simple text input UI
- Integration with other features

## Quick Start

### Audio Feature

The easiest way to use the audio feature is the **interactive REPL mode**:

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
```

For more details, see the [Audio Feature Documentation](src/audio/README.md).

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

## Project Structure

```
.
├── src/
│   ├── audio/              # Feature 1: Text-to-translated-audio
│   │   ├── translation.py  # Huttese translation logic
│   │   ├── effects.py      # Audio post-processing
│   │   ├── engines/        # TTS engine implementations
│   │   └── README.md       # Audio feature documentation
│   │
│   ├── roll20/             # Feature 2: Post-text-to-Roll20
│   │   ├── client.py       # Headless browser automation
│   │   ├── message.py      # Message formatting
│   │   └── config.py       # Configuration
│   │
│   ├── input/              # Feature 3: Input text UI
│   │   └── ui.py           # Text input interface
│   │
│   ├── cli/                # Command-line interfaces
│   │   ├── audio_cli.py    # Main audio CLI
│   │   ├── interactive.py  # REPL mode
│   │   └── simple_cli.py   # Simple CLI variant
│   │
│   └── common/             # Shared utilities
│       └── suppress_warnings.py
│
├── tests/
│   ├── unit/
│   │   ├── test_audio/     # Audio feature tests
│   │   └── test_imports.py
│   └── integration/
│       └── test_audio/     # Audio integration tests
│
├── samples/
│   └── lines.txt           # Sample lines for testing
├── pyproject.toml          # Poetry configuration
├── Makefile
└── README.md               # This file
```

## Usage

### Audio Feature

```bash
# Interactive REPL (recommended)
poetry run huttese-repl

# Single command
poetry run huttese 'Bring me the plans' --play

# Choose TTS engine
poetry run huttese 'Your text' --engine kokoro --play
poetry run huttese 'Your text' --engine coqui --play
poetry run huttese 'Your text' --engine simple --play

# Customize voice
poetry run huttese 'Your text' --semitones -5 --grit-drive 7 --play
```

See [Audio Feature Documentation](src/audio/README.md) for complete usage details.

### Roll20 Feature (Coming Soon)

```bash
# Post message to Roll20 chat
poetry run roll20-post "Your message here"

# Post with audio
poetry run roll20-post "Your message" --with-audio
```

### Input Feature (Coming Soon)

```bash
# Launch text input UI
poetry run huttese-input
```

## Makefile Shortcuts

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

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific feature tests
poetry run pytest tests/unit/test_audio/
poetry run pytest tests/integration/test_audio/
```

### Code Organization

The codebase is organized by feature:
- **src/audio/**: Audio translation and synthesis
- **src/roll20/**: Roll20 integration (placeholder)
- **src/input/**: Text input UI (placeholder)
- **src/cli/**: Command-line interfaces
- **src/common/**: Shared utilities

Each feature is self-contained and can be developed independently.

## Technical Details

### Dependencies

- **Python**: 3.11-3.13
- **TTS Engines**: Kokoro, Coqui XTTS v2
- **Audio Processing**: Sox, Rubberband, FFmpeg
- **Testing**: pytest, pytest-cov

### System Requirements

- **macOS**: 10.15+ (Catalina or later)
- **Linux**: Ubuntu 20.04+ or equivalent
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB for model cache
- **Audio**: Working audio output device

## Troubleshooting

### Audio Tools Not Found

**macOS:**
```bash
brew install ffmpeg sox rubberband
```

**Linux:**
```bash
sudo apt install -y ffmpeg sox rubberband-cli libsndfile1
```

### Poetry Issues

**Poetry not found:**
```bash
# Add Poetry to your PATH (add to ~/.zshrc or ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc  # or ~/.bashrc
```

**Dependency conflicts:**
```bash
# Clean install
rm -rf poetry.lock
poetry install
```

### Network Issues

If you're on a corporate network that blocks HuggingFace, use the simple TTS engine:

```bash
poetry run huttese "Your text" --engine simple --play
```

For more troubleshooting, see the [Audio Feature Documentation](src/audio/README.md).

## Future Enhancements

### Audio Feature
- [ ] Add preset system (`--preset jabba`, `--preset klatooinian`)
- [ ] Fine-tune TTS model on Star Wars audio
- [ ] Voice cloning from audio samples
- [ ] Real-time audio streaming

### Roll20 Feature
- [ ] Headless browser automation with Selenium/Playwright
- [ ] Message formatting and templating
- [ ] Integration with audio feature
- [ ] Configuration management

### Input Feature
- [ ] Native text input UI
- [ ] Integration with audio and Roll20 features
- [ ] Message history and templates

### General
- [ ] Web interface with real-time synthesis
- [ ] Mobile app
- [ ] Support for other alien languages (Rodian, Geonosian, etc.)

## Credits

- **TTS Models**: Kokoro, Coqui XTTS v2 (maintained fork by Idiap Research Institute)
- **Audio Processing**: Sox, Rubberband, FFmpeg
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

