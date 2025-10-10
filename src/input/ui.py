#!/usr/bin/env python3
"""
Text input UI for Klatooinian Huttese speech synthesis.

A small, always-on-top window with:
- Log of last 30 things said
- Input field
- Say button
- Settings menu
"""
# Set process title FIRST (for dock tooltip on macOS)
try:
    import setproctitle
    setproctitle.setproctitle('Klatooinian Huttese Synthesizer')
except ImportError:
    pass

# Set macOS application name (for menu bar and dock)
import sys
import platform

if platform.system() == 'Darwin':  # macOS
    try:
        from Foundation import NSBundle, NSProcessInfo
        from AppKit import NSApplication, NSApplicationActivationPolicyRegular
        
        # Set bundle names (for menu)
        bundle = NSBundle.mainBundle()
        if bundle:
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            if info:
                info['CFBundleName'] = 'Klatooinian Huttese Synthesizer'
                info['CFBundleDisplayName'] = 'Klatooinian Huttese Synthesizer'
                info['CFBundleExecutable'] = 'Klatooinian Huttese Synthesizer'
        
        # Set process name
        processInfo = NSProcessInfo.processInfo()
        processInfo.setProcessName_('Klatooinian Huttese Synthesizer')
        
        # Force NSApplication to use our name
        nsapp = NSApplication.sharedApplication()
        nsapp.setActivationPolicy_(NSApplicationActivationPolicyRegular)
    except ImportError:
        pass  # PyObjC not available

# Suppress warnings
from ..common.suppress_warnings import suppress_tts_loading_messages
suppress_tts_loading_messages()

import time
import asyncio
from pathlib import Path
from collections import deque
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QDialog, QLabel, QMenuBar, QTextBrowser,
    QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtGui import QAction, QKeyEvent, QTextCursor, QIcon, QPixmap
import sounddevice as sd
import soundfile as sf

from ..audio.translation import rewrite_to_huttese
from ..audio.effects import process_klatooinian
from ..audio.engines.simple import synth_to_wav
from ..roll20.service import Roll20Service, ServiceState
from ..roll20.config import config as roll20_config
from ..roll20.verbose import vprint


# Unique identifier for single instance
SINGLE_INSTANCE_ID = "klatooinian-huttese-ui-single-instance"

# Maximum number of history items to keep
MAX_HISTORY_ITEMS = 30


class HistoryLineEdit(QLineEdit):
    """Custom QLineEdit with up arrow history recall."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_history = []  # History of sent texts
        self.recall_stack = []   # Stack for texts that were in the field when history was clicked
        self.history_index = -1  # Current position in history (-1 = not browsing)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events, especially up arrow for history recall."""
        if event.key() == Qt.Key.Key_Up:
            self.recall_previous()
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            self.recall_next()
            event.accept()
        else:
            # For any other key, reset history browsing
            if event.key() not in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.history_index = -1
            super().keyPressEvent(event)
    
    def recall_previous(self):
        """Recall previous item from history (up arrow)."""
        if not self.input_history and not self.recall_stack:
            return
        
        # First check recall stack (items pushed when clicking history)
        if self.recall_stack and self.history_index == -1:
            text = self.recall_stack.pop()
            self.setText(text)
            return
        
        # Then browse through input history
        if not self.input_history:
            return
        
        if self.history_index == -1:
            # Starting to browse history
            self.history_index = len(self.input_history) - 1
        elif self.history_index > 0:
            # Move back in history
            self.history_index -= 1
        
        if 0 <= self.history_index < len(self.input_history):
            self.setText(self.input_history[self.history_index])
    
    def recall_next(self):
        """Recall next item from history (down arrow)."""
        if self.history_index == -1:
            return
        
        self.history_index += 1
        
        if self.history_index >= len(self.input_history):
            # Reached the end, clear field
            self.history_index = -1
            self.clear()
        else:
            self.setText(self.input_history[self.history_index])
    
    def add_to_history(self, text):
        """Add text to input history."""
        if text and (not self.input_history or self.input_history[-1] != text):
            self.input_history.append(text)
        self.history_index = -1
    
    def push_to_recall_stack(self, text):
        """Push current text to recall stack (for when clicking history)."""
        if text:
            self.recall_stack.append(text)


class SynthesisWorker(QThread):
    """Background thread for audio synthesis and playback."""
    translation_ready = pyqtSignal(str, str)  # english, huttese - emitted immediately after translation
    finished = pyqtSignal(float)  # elapsed_time - emitted after playback
    error = pyqtSignal(str)
    
    def __init__(self, text, settings):
        super().__init__()
        self.text = text
        self.settings = settings
        self.tmp_dir = Path("/tmp/huttese_ui")
        self.tmp_dir.mkdir(exist_ok=True)
    
    def run(self):
        """Run synthesis in background thread."""
        try:
            start_time = time.time()
            
            # Rewrite to Huttese
            huttese = rewrite_to_huttese(
                self.text,
                seed=self.settings.get('seed', 42),
                strip_every_nth=self.settings.get('strip_every_nth', 3)
            )
            
            # Emit translation ready signal immediately after rewrite
            # This allows the UI to update right away, before synthesis
            self.translation_ready.emit(self.text, huttese)
            
            # Generate temporary file paths
            tmp_raw = self.tmp_dir / f"raw_{int(time.time() * 1000)}.wav"
            tmp_fx = self.tmp_dir / f"fx_{int(time.time() * 1000)}.wav"
            
            try:
                # Suppress TTS output
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = open("/dev/null", "w")
                sys.stderr = open("/dev/null", "w")
                
                try:
                    # Synthesize
                    synth_to_wav(
                        huttese,
                        str(tmp_raw),
                        voice=self.settings.get('voice', 'Lee')
                    )
                    
                    # Apply effects
                    process_klatooinian(
                        str(tmp_raw), str(tmp_fx),
                        semitones=self.settings.get('semitones', -2),
                        grit_drive=self.settings.get('grit_drive', 0),
                        grit_color=self.settings.get('grit_color', 10),
                        chorus_ms=self.settings.get('chorus_ms', 0),
                        grit_mode=self.settings.get('grit_mode', 'combo'),
                        tempo=self.settings.get('tempo', 0.9),
                    )
                finally:
                    sys.stdout.close()
                    sys.stderr.close()
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                
                # Play audio
                # Use larger blocksize to prevent buffer underruns in UI environment
                # which can cause crackling on laptop speakers
                data, sr = sf.read(str(tmp_fx), dtype="float32")
                sd.play(data, sr, blocksize=4096)
                sd.wait()
                
                elapsed = time.time() - start_time
                self.finished.emit(elapsed)
                
            finally:
                # Cleanup
                tmp_raw.unlink(missing_ok=True)
                tmp_fx.unlink(missing_ok=True)
                
        except Exception as e:
            self.error.emit(str(e))


class Roll20Worker(QThread):
    """Background thread for managing Roll20 service."""
    state_changed = pyqtSignal(str)  # state_name
    error = pyqtSignal(str)

    def __init__(self, headless: bool = True):
        super().__init__()
        self.service = None
        self.loop = None
        self._running = True
        self._last_state = None
        self._headless = headless

    def run(self):
        """Run the Roll20 service in an asyncio event loop."""
        try:
            # Create a new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Run the async main function
            self.loop.run_until_complete(self._async_main())

        except Exception as e:
            self.error.emit(f"Roll20 error: {e}")
        finally:
            if self.loop:
                self.loop.close()

    async def _monitor_state(self):
        """Monitor service state changes and emit signals."""
        while self._running and self.service:
            current_state = self.service.state
            if current_state != self._last_state:
                self._last_state = current_state
                self.state_changed.emit(current_state.value)

            # Check every 100ms for more responsive updates
            await asyncio.sleep(0.1)

    async def _async_main(self):
        """Main async function that manages the service."""
        try:
            # Create the service
            self.service = Roll20Service()

            # Emit initial state
            self._last_state = ServiceState.CLOSED
            self.state_changed.emit(self._last_state.value)

            # Start monitoring state changes in the background
            monitor_task = asyncio.create_task(self._monitor_state())

            # Open the service
            # The monitor task will catch state changes during this
            await self.service.open(headless=self._headless)

            # Wait for the monitor task (it runs until _running is False)
            await monitor_task

        except Exception as e:
            self.error.emit(f"Roll20 service error: {e}")
        finally:
            # Clean up
            if self.service:
                try:
                    await self.service.close()
                except:
                    pass

    def send_message(self, to_users: list[str], message: str):
        """
        Send a message to Roll20 users (thread-safe).

        This can be called from the main UI thread and will safely
        schedule the message to be sent on the worker's event loop.

        Args:
            to_users: List of Roll20 usernames to send to
            message: The message text to send
        """
        if self.loop and self.service:
            # Schedule the coroutine on the worker's event loop
            asyncio.run_coroutine_threadsafe(
                self.service.send(to_users, message),
                self.loop
            )

    def stop(self):
        """Stop the worker thread."""
        self._running = False


class SettingsDialog(QDialog):
    """Settings modal dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        # Placeholder content
        label = QLabel("Settings will be added here")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class HutteseUI(QMainWindow):
    """Main UI window for Klatooinian Huttese speech synthesis."""

    def __init__(self, headless: bool = True):
        super().__init__()

        # Settings (using defaults from REPL)
        self.settings = {
            'engine': 'simple',
            'voice': 'Lee',
            'seed': 42,
            'semitones': -2,
            'grit_drive': 0,
            'grit_color': 10,
            'chorus_ms': 0,
            'grit_mode': 'combo',
            'tempo': 0.9,
            'strip_every_nth': 3,
        }

        # History of last N things said
        self.history = deque(maxlen=MAX_HISTORY_ITEMS)

        # Worker thread for synthesis
        self.worker = None

        # Roll20 worker thread
        self.roll20_worker = None

        self.init_ui()
        self.init_roll20(headless=headless)
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🎙️ Klatooinian Huttese Synthesizer")
        
        # Set application icon
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Set window to always stay on top
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Create menu bar
        menubar = self.menuBar()
        
        # Settings menu (macOS standard)
        settings_action = QAction("Settings...", self)
        settings_action.setMenuRole(QAction.MenuRole.PreferencesRole)
        settings_action.triggered.connect(self.show_settings)
        
        # On macOS, this will appear in the application menu
        app_menu = menubar.addMenu("File")
        app_menu.addAction(settings_action)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # History log (use QTextBrowser for clickable links) - expands to fill space
        self.history_log = QTextBrowser()
        self.history_log.setReadOnly(True)
        self.history_log.setPlaceholderText("History will appear here...")
        self.history_log.setOpenExternalLinks(False)  # Handle clicks internally
        self.history_log.anchorClicked.connect(self.on_history_item_clicked)
        layout.addWidget(self.history_log, stretch=1)  # stretch=1 makes it expand
        
        # Input field and Say button on same row - pinned to bottom
        input_layout = QHBoxLayout()
        
        self.input_field = HistoryLineEdit()
        self.input_field.setPlaceholderText("Type something to say in Klatooinian Huttese...")
        self.input_field.returnPressed.connect(self.say_text)
        self.input_field.textChanged.connect(self.on_input_changed)
        input_layout.addWidget(self.input_field)
        
        self.say_button = QPushButton("Say")
        self.say_button.clicked.connect(self.say_text)
        self.say_button.setDefault(True)
        self.say_button.setEnabled(False)  # Disabled by default when field is empty
        input_layout.addWidget(self.say_button)
        
        layout.addLayout(input_layout, stretch=0)  # stretch=0 keeps it fixed height
        
        central_widget.setLayout(layout)
        
        # Set window size (20% taller than original 300 = 360, and resizable)
        self.resize(400, 360)
        self.setMinimumSize(350, 250)
        
        # Show loading message
        self.statusBar().showMessage("Loading TTS model...")

    def init_roll20(self, headless: bool = True):
        """Initialize Roll20 service integration."""
        # Create and start the Roll20 worker
        self.roll20_worker = Roll20Worker(headless=headless)
        self.roll20_worker.state_changed.connect(self.on_roll20_state_changed)
        self.roll20_worker.error.connect(self.on_roll20_error)
        self.roll20_worker.start()

    def on_roll20_state_changed(self, state_name: str):
        """Handle Roll20 service state changes."""
        # Map state names to user-friendly messages
        state_messages = {
            "Closed": "Roll20: Not connected",
            "Connecting": "Roll20: Connecting...",
            "Ready": "Roll20: Ready",
            "Sending": "Roll20: Sending message...",
        }

        message = state_messages.get(state_name, f"Roll20: {state_name}")
        self.statusBar().showMessage(message)

    def on_roll20_error(self, error_msg: str):
        """Handle Roll20 service errors."""
        # Show critical error dialog
        QMessageBox.critical(
            self,
            "Roll20 Service Error",
            f"Failed to initialize Roll20 service:\n\n{error_msg}\n\n"
            "The application cannot function without the Roll20 service and will now close.",
            QMessageBox.StandardButton.Ok
        )
        # Exit the application
        QApplication.quit()

    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def on_input_changed(self, text):
        """Handle input field text changes to enable/disable Say button."""
        self.say_button.setEnabled(bool(text.strip()))
    
    def on_history_item_clicked(self, url: QUrl):
        """Handle clicking on a history item link."""
        # Extract the index from the URL (format: #item-N)
        fragment = url.fragment()
        if fragment.startswith("item-"):
            try:
                index = int(fragment[5:])
                if 0 <= index < len(self.history):
                    english, _ = self.history[index]
                    
                    # If there's already text in the input field, push it to recall stack
                    current_text = self.input_field.text().strip()
                    if current_text:
                        self.input_field.push_to_recall_stack(current_text)
                    
                    # Set the input field to the selected history item
                    self.input_field.setText(english)
                    self.input_field.setFocus()
            except (ValueError, IndexError):
                pass
    
    def say_text(self):
        """Process and speak the input text."""
        text = self.input_field.text().strip()

        if not text:
            return

        # Add to input history
        self.input_field.add_to_history(text)

        # Clear input field immediately for better responsiveness
        self.input_field.clear()
        self.input_field.setFocus()

        # Show processing status
        self.statusBar().showMessage("Processing...")

        # Send to Roll20 in parallel with audio synthesis
        if self.roll20_worker and roll20_config.target_users:
            # Format the message for Roll20 (currently just the raw text)
            formatted_message = text
            vprint(f"\n[UI] Sending to Roll20:")
            vprint(f"  Target users: {roll20_config.target_users}")
            vprint(f"  Original text: {repr(text)}")
            vprint(f"  Formatted message: {repr(formatted_message)}")
            self.roll20_worker.send_message(roll20_config.target_users, formatted_message)

        # Start synthesis in background thread
        self.worker = SynthesisWorker(text, self.settings)
        self.worker.translation_ready.connect(self.on_translation_ready)
        self.worker.finished.connect(self.on_synthesis_finished)
        self.worker.error.connect(self.on_synthesis_error)
        self.worker.start()
    
    def on_translation_ready(self, english, huttese):
        """Handle translation ready (immediately after rewrite, before synthesis)."""
        # Add to history immediately, before audio synthesis/playback
        self.history.append((english, huttese))
        self.update_history_display()
        
        # Update status to show it's synthesizing
        self.statusBar().showMessage("Synthesizing...")
    
    def on_synthesis_finished(self, elapsed):
        """Handle synthesis and playback completion."""
        # Update status with timing
        self.statusBar().showMessage(f"Done ({elapsed:.1f}s)", 3000)
    
    def on_synthesis_error(self, error_msg):
        """Handle synthesis error."""
        self.statusBar().showMessage(f"Error: {error_msg}", 5000)
    
    def update_history_display(self):
        """Update the history log display."""
        html_parts = []
        for i, (english, huttese) in enumerate(self.history):
            # Make each history item a clickable link
            html_parts.append(
                f'<div style="margin-bottom: 8px;">'
                f'<a href="#item-{i}" style="text-decoration: none; color: inherit;">'
                f'<b>{english}</b><br>'
                f'<span style="color: #666;">→ {huttese}</span>'
                f'</a>'
                f'</div>'
            )

        self.history_log.setHtml(''.join(html_parts))

        # Scroll to bottom
        scrollbar = self.history_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        """Handle window close event to clean up Roll20 service."""
        if self.roll20_worker:
            self.roll20_worker.stop()
            self.roll20_worker.wait(2000)  # Wait up to 2 seconds for cleanup
        event.accept()


class SingleInstanceApplication(QApplication):
    """Application that ensures only one instance is running."""
    
    show_window_signal = pyqtSignal()
    
    def __init__(self, argv):
        super().__init__(argv)
        self.server = None
        self.window = None
        
        # Set application name and icon
        self.setApplicationName("Klatooinian Huttese Synthesizer")
        self.setApplicationDisplayName("Klatooinian Huttese Synthesizer")
        
        # Set application icon
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Try to connect to existing instance
        socket = QLocalSocket()
        socket.connectToServer(SINGLE_INSTANCE_ID)
        
        if socket.waitForConnected(500):
            # Another instance is running, send message to show window
            socket.write(b"show")
            socket.waitForBytesWritten()
            socket.disconnectFromServer()
            self.is_running = True
        else:
            # No other instance, create server
            self.is_running = False
            self.server = QLocalServer()
            # Remove any stale server
            QLocalServer.removeServer(SINGLE_INSTANCE_ID)
            self.server.listen(SINGLE_INSTANCE_ID)
            self.server.newConnection.connect(self.handle_new_connection)
    
    def handle_new_connection(self):
        """Handle connection from another instance trying to launch."""
        socket = self.server.nextPendingConnection()
        if socket:
            socket.waitForReadyRead(1000)
            data = socket.readAll()
            if data == b"show" and self.window:
                # Show and raise the existing window
                self.window.show()
                self.window.raise_()
                self.window.activateWindow()
            socket.disconnectFromServer()


def main():
    """Run the Klatooinian Huttese UI application."""
    # Parse command line arguments
    headless = True
    verbose = False

    if "--headful" in sys.argv:
        headless = False
        print("Running Roll20 service in HEADFUL mode (browser visible)")
        print("This is for debugging purposes.\n")

    if "--verbose" in sys.argv:
        verbose = True
        print("Running in VERBOSE mode (detailed logging enabled)")
        print("This is for debugging purposes.\n")
        # Enable verbose logging in the roll20 module
        from ..roll20.verbose import set_verbose
        set_verbose(True)

    app = SingleInstanceApplication(sys.argv)

    # If another instance is already running, exit
    if app.is_running:
        print("Klatooinian Huttese UI is already running. Focusing existing window...")
        sys.exit(0)

    # Create and show main window
    window = HutteseUI(headless=headless)
    app.window = window  # Store reference for single instance handling
    window.show()

    # Update status after window is shown
    window.statusBar().showMessage("Ready", 2000)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
