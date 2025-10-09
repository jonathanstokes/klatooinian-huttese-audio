"""
Unit tests for the Huttese UI.

Tests the UI logic without requiring a display (using QTest).
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

# We need a QApplication instance for Qt widgets
@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_history_line_edit_recall(qapp):
    """Test that HistoryLineEdit can recall previous inputs."""
    from src.input.ui import HistoryLineEdit
    
    line_edit = HistoryLineEdit()
    
    # Add some history
    line_edit.add_to_history("first text")
    line_edit.add_to_history("second text")
    line_edit.add_to_history("third text")
    
    # Verify history was added
    assert len(line_edit.input_history) == 3
    assert line_edit.input_history[-1] == "third text"
    
    # Test recall with up arrow
    line_edit.recall_previous()
    assert line_edit.text() == "third text"
    
    line_edit.recall_previous()
    assert line_edit.text() == "second text"
    
    line_edit.recall_previous()
    assert line_edit.text() == "first text"
    
    # Test recall with down arrow
    line_edit.recall_next()
    assert line_edit.text() == "second text"


def test_history_line_edit_recall_stack(qapp):
    """Test that recall stack works when clicking history."""
    from src.input.ui import HistoryLineEdit
    
    line_edit = HistoryLineEdit()
    
    # Set some text
    line_edit.setText("current text")
    
    # Push to recall stack (simulating clicking history)
    line_edit.push_to_recall_stack("current text")
    
    # Set new text
    line_edit.setText("from history")
    
    # Recall should get back the pushed text
    line_edit.recall_previous()
    assert line_edit.text() == "current text"


def test_history_line_edit_no_duplicates(qapp):
    """Test that duplicate consecutive entries are not added to history."""
    from src.input.ui import HistoryLineEdit
    
    line_edit = HistoryLineEdit()
    
    line_edit.add_to_history("same text")
    line_edit.add_to_history("same text")
    line_edit.add_to_history("different text")
    line_edit.add_to_history("different text")
    
    # Should only have 2 items (duplicates removed)
    assert len(line_edit.input_history) == 2
    assert line_edit.input_history == ["same text", "different text"]


@patch('src.input.ui.synth_to_wav')
@patch('src.input.ui.process_klatooinian')
@patch('src.input.ui.sd.play')
@patch('src.input.ui.sd.wait')
@patch('src.input.ui.sf.read')
def test_synthesis_worker(mock_sf_read, mock_sd_wait, mock_sd_play, 
                          mock_process, mock_synth, qapp):
    """Test that SynthesisWorker processes text correctly."""
    from src.input.ui import SynthesisWorker
    import numpy as np
    
    # Mock the audio file reading
    mock_sf_read.return_value = (np.zeros(1000, dtype=np.float32), 24000)
    
    settings = {
        'seed': 42,
        'strip_every_nth': 3,
        'voice': 'Lee',
        'semitones': -2,
        'grit_drive': 0,
        'grit_color': 10,
        'chorus_ms': 0,
        'grit_mode': 'combo',
        'tempo': 0.9,
    }
    
    worker = SynthesisWorker("Hello world", settings)
    
    # Track if signals were emitted
    translation_ready_called = []
    finished_called = []
    
    worker.translation_ready.connect(
        lambda eng, hut: translation_ready_called.append((eng, hut))
    )
    worker.finished.connect(
        lambda elapsed: finished_called.append(elapsed)
    )
    
    # Run the worker
    worker.run()
    
    # Verify synthesis was called
    assert mock_synth.called
    assert mock_process.called
    assert mock_sd_play.called
    
    # Verify translation_ready signal was emitted
    assert len(translation_ready_called) == 1
    english, huttese = translation_ready_called[0]
    assert english == "Hello world"
    assert isinstance(huttese, str)
    
    # Verify finished signal was emitted
    assert len(finished_called) == 1
    elapsed = finished_called[0]
    assert elapsed >= 0


def test_huttese_ui_initialization(qapp):
    """Test that HutteseUI initializes correctly."""
    from src.input.ui import HutteseUI
    
    window = HutteseUI()
    
    # Check that settings are initialized
    assert window.settings['voice'] == 'Lee'
    assert window.settings['semitones'] == -2
    assert window.settings['strip_every_nth'] == 3
    
    # Check that history is empty
    assert len(window.history) == 0
    
    # Check that UI elements exist
    assert window.input_field is not None
    assert window.say_button is not None
    assert window.history_log is not None
    
    # Check window properties
    assert window.windowTitle() == "🎙️ Huttese Synthesizer"
    
    window.close()


def test_huttese_ui_history_update(qapp):
    """Test that history display updates correctly."""
    from src.input.ui import HutteseUI
    
    window = HutteseUI()
    
    # Add some history
    window.history.append(("Hello", "halo"))
    window.history.append(("Goodbye", "choodbye"))
    
    # Update display
    window.update_history_display()
    
    # Check that HTML was generated
    html = window.history_log.toHtml()
    assert "Hello" in html
    assert "halo" in html
    assert "Goodbye" in html
    assert "choodbye" in html
    
    window.close()


def test_huttese_ui_translation_ready_updates_history(qapp):
    """Test that history is updated when translation is ready (before playback)."""
    from src.input.ui import HutteseUI
    
    window = HutteseUI()
    
    # Simulate translation_ready signal
    window.on_translation_ready("Test input", "testa inaputa")
    
    # Check that history was updated
    assert len(window.history) == 1
    assert window.history[0] == ("Test input", "testa inaputa")
    
    # Check that display was updated
    html = window.history_log.toHtml()
    assert "Test input" in html
    assert "testa inaputa" in html
    
    window.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
