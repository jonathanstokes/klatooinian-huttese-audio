# Codebase Refactoring Summary

## Overview

The codebase has been refactored to support three distinct features with clear separation of concerns:

1. **Text-to-translated-audio** - Convert English text to Huttese-ish speech with Klatooinian voice effects
2. **Post-text-to-Roll20** - Post messages to Roll20 chat (future implementation)
3. **Input text feature** - Text input UI (future implementation)

## New Directory Structure

```
src/
├── __init__.py
├── audio/                          # Feature 1: Text-to-translated-audio
│   ├── __init__.py
│   ├── translation.py              # Huttese translation (was: rewrite.py)
│   ├── effects.py                  # Audio effects (was: fx.py)
│   └── engines/                    # TTS engine implementations
│       ├── __init__.py
│       ├── kokoro.py              # Kokoro TTS (was: synth_f5.py)
│       ├── coqui.py               # Coqui XTTS v2 (was: synth.py)
│       └── simple.py              # macOS 'say' (was: synth_simple.py)
├── roll20/                         # Feature 2: Post-text-to-Roll20
│   ├── __init__.py
│   ├── client.py                   # Headless browser automation (new)
│   ├── message.py                  # Message formatting (new)
│   └── config.py                   # Roll20 configuration (new)
├── input/                          # Feature 3: Input text feature (future)
│   ├── __init__.py
│   └── ui.py                       # Text input UI (new)
├── cli/                            # Command-line interfaces
│   ├── __init__.py
│   ├── audio_cli.py               # Main CLI (was: cli.py)
│   ├── interactive.py             # REPL interface (unchanged)
│   └── simple_cli.py              # Simple CLI (was: cli_simple.py)
└── common/                         # Shared utilities
    ├── __init__.py
    └── suppress_warnings.py       # Warning suppression (unchanged)

tests/
├── unit/
│   ├── test_imports.py            # Import tests (updated)
│   └── test_audio/
│       └── test_translation.py    # Translation tests (was: test_rewrite.py)
└── integration/
    └── test_audio/
        └── test_effects.py        # Effects tests (was: test_fx.py)
```

## Key Changes

### File Migrations

| Old Location | New Location | Notes |
|-------------|--------------|-------|
| `src/rewrite.py` | `src/audio/translation.py` | Core translation logic |
| `src/fx.py` | `src/audio/effects.py` | Audio effects processing |
| `src/synth_f5.py` | `src/audio/engines/kokoro.py` | Kokoro TTS engine |
| `src/synth.py` | `src/audio/engines/coqui.py` | Coqui TTS engine |
| `src/synth_simple.py` | `src/audio/engines/simple.py` | Simple TTS engine |
| `src/cli.py` | `src/cli/audio_cli.py` | Main CLI |
| `src/cli_simple.py` | `src/cli/simple_cli.py` | Simple CLI |
| `src/suppress_warnings.py` | `src/common/suppress_warnings.py` | Shared utility |

### Import Updates

All imports have been updated to reflect the new structure:

**Before:**
```python
from .rewrite import rewrite_to_huttese
from .fx import process_klatooinian
from .synth_f5 import synth_to_wav
```

**After:**
```python
from ..audio.translation import rewrite_to_huttese
from ..audio.effects import process_klatooinian
from ..audio.engines.kokoro import synth_to_wav
```

### Entry Points

Updated in `pyproject.toml`:

**Before:**
```toml
[tool.poetry.scripts]
huttese = "src.cli:main"
huttese-repl = "src.interactive:main"
```

**After:**
```toml
[tool.poetry.scripts]
huttese = "src.cli.audio_cli:main"
huttese-repl = "src.cli.interactive:main"
```

### Test Organization

Tests are now organized by feature:

- `tests/unit/test_audio/` - Audio feature unit tests
- `tests/integration/test_audio/` - Audio feature integration tests
- `tests/unit/test_roll20/` - Roll20 feature tests (future)
- `tests/unit/test_input/` - Input feature tests (future)

**Note:** Test directories do NOT have `__init__.py` files to avoid import conflicts with source packages.

## Benefits

1. **Clear Feature Separation** - Each feature has its own package
2. **Easy Navigation** - Related code is grouped together
3. **Scalable** - Easy to add new features or sub-modules
4. **Standard Python Practice** - Follows PEP conventions
5. **Independent Evolution** - Features can be developed/tested separately
6. **Clear Imports** - Import paths clearly indicate feature boundaries

## Testing

All tests pass after refactoring:
- ✅ 31 tests passing
- ✅ All imports working correctly
- ✅ CLI commands functional
- ✅ No breaking changes to existing functionality

## Next Steps

1. Implement Roll20 headless browser automation in `src/roll20/`
2. Implement text input UI in `src/input/`
3. Add integration tests for Roll20 feature
4. Add CLI for Roll20 posting

