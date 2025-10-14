# Screenshot and DOM Capture on Failure

## Overview

The Roll20 client now automatically captures both screenshots and DOM (HTML) when initialization fails, which is especially useful for debugging issues in headless mode where you can't see what's happening in the browser.

**Note:** As of the latest version, **headful mode (browser visible) is now the default** because Cloudflare's anti-bot detection is more reliable when the browser is visible. Headless mode is still available but may be blocked by Cloudflare.

## Changes Made

### 1. Screenshot Capture Method

Added `capture_screenshot()` method to `Roll20Client`:

```python
async def capture_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
    """
    Capture a screenshot of the current page.
    
    Args:
        filename: Optional filename. If not provided, uses timestamp.
        
    Returns:
        Path to the saved screenshot, or None if capture failed.
    """
```

- Screenshots are saved to `screenshots/` directory (created automatically)
- Default filename format: `roll20_error_YYYYMMDD_HHMMSS.png`
- Returns the path to the saved screenshot

### 2. DOM Capture Method

Added `capture_dom()` method to `Roll20Client`:

```python
async def capture_dom(self, filename: Optional[str] = None) -> Optional[str]:
    """
    Capture the DOM (HTML) of the current page.

    Args:
        filename: Optional filename. If not provided, uses timestamp.

    Returns:
        Path to the saved HTML file, or None if capture failed.
    """
```

- DOM files are saved to `screenshots/` directory (same as screenshots)
- Default filename format: `roll20_error_YYYYMMDD_HHMMSS.html`
- Returns the path to the saved HTML file

### 3. Error Handling in Initialize

The `initialize()` method now wraps all initialization steps in a try-except block:

- On any exception, it captures both a screenshot AND the DOM before re-raising
- Both files use the same timestamp for easy correlation
- Prints clear error messages and the file paths
- The exception is still raised so callers know initialization failed

### 4. Increased Retry Counts

To handle the faster execution in headless mode:

- `_dismiss_dialog_with_retry`: Increased from 8 to 15 attempts
- `verify_chat_ui`: Increased from 20 to 40 attempts

These changes help prevent premature timeout failures in headless mode where rendering can be unpredictable.

### 5. Improved Headless Browser Arguments

Added several browser arguments to improve Cloudflare bypass in headless mode:

- `--headless=new` - Uses newer headless mode (harder to detect)
- `--disable-blink-features=AutomationControlled` - Hides automation
- `--disable-web-security` - Disables web security checks
- Additional anti-detection flags

**Note:** Despite these improvements, Cloudflare still often blocks headless browsers, which is why headful mode is now the default.

### 6. Default Mode Changed to Headful

The default mode is now **headful (browser visible)** instead of headless:

- `initialize(headless=False)` - Default is now False
- `start(headless=False)` - Default is now False
- Test scripts default to headful mode
- Use `--headless` flag to run in headless mode (instead of `--headful`)

## Usage

### Running in Headful Mode (Default)

```bash
# Run with browser visible (default)
python -m src.roll20.test_client

# Or in code
await client.initialize()  # headless=False is the default
```

### Running in Headless Mode

```bash
# Run in headless mode (may be blocked by Cloudflare)
python -m src.roll20.test_client --headless

# Or in code
await client.initialize(headless=True)
```

### Automatic Screenshot and DOM Capture on Failure

When running any Roll20 client code, screenshots and DOM are captured automatically on failure:

```python
client = Roll20Client()
try:
    await client.initialize()
except Exception as e:
    # Screenshot and DOM already captured and saved to screenshots/
    print(f"Check screenshots/ directory for debugging")
```

Output on failure:
```
❌ INITIALIZATION FAILED
Error: Chat UI elements not found after 40 attempts

Attempting to capture screenshot and DOM for debugging...
✓ Screenshot saved: screenshots/roll20_error_20251014_143022.png
✓ DOM saved: screenshots/roll20_error_20251014_143022.html
These can help diagnose what went wrong.
```

### Manual Screenshot Capture

You can also manually capture screenshots at any point:

```python
client = Roll20Client()
await client.initialize(headless=True)

# Capture a screenshot manually
screenshot_path = await client.capture_screenshot("my_debug_screenshot.png")
print(f"Screenshot saved to: {screenshot_path}")
```

### Testing Screenshot Capture

Use the test script to verify screenshot capture works:

```bash
python -m src.roll20.test_screenshot
```

This will attempt initialization and capture a screenshot if it fails.

## Screenshot Location

All screenshots are saved to:
```
screenshots/roll20_error_YYYYMMDD_HHMMSS.png
```

The `screenshots/` directory is created automatically in the project root if it doesn't exist.

## Debugging with Screenshots

When initialization fails in headless mode:

1. Check the console output for the screenshot path
2. Open the screenshot to see the exact state of the browser when it failed
3. Look for:
   - Login errors or Cloudflare challenges
   - Missing UI elements
   - Unexpected dialogs or popups
   - Page load failures

## Benefits

- **Headless Debugging**: See what's happening in headless mode without running headful
- **Faster Iteration**: Quickly identify issues without manual browser inspection
- **CI/CD Integration**: Screenshots can be saved as artifacts in automated testing
- **Historical Record**: Timestamped screenshots provide a record of failures

## Notes

- Screenshots are only captured if a page is loaded (i.e., `self.page` exists)
- The screenshot capture itself is wrapped in error handling to prevent cascading failures
- Screenshots use PNG format for clarity and compatibility

