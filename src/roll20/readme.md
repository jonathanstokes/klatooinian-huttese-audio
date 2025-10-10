# Roll20 Integration

This module provides browser automation for Roll20 using the `nodriver` library, which can bypass Cloudflare's anti-bot protection.

## Features

- **Cloudflare Bypass**: Uses `nodriver` (successor to undetected-chromedriver) to avoid detection
- **Persistent Sessions**: Browser sessions can be persisted to avoid repeated logins
- **Headless/Headful Modes**: Can run headless for automation or headful for manual intervention
- **Chat UI Access**: Navigates to the game editor and verifies chat interface elements

## Configuration

Add these environment variables to your `.env` file:

```bash
ROLL20_USERNAME=your-email@example.com
ROLL20_PASSWORD=your-password
ROLL20_CAMPAIGN_ID=your-campaign-id
```

To find your campaign ID:
1. Go to your Roll20 campaign
2. Look at the URL: `https://app.roll20.net/campaigns/details/12345678`
3. The campaign ID is the number at the end (e.g., `12345678`)

## Usage

### Basic Usage

```python
import asyncio
from src.roll20.client import Roll20Client

async def main():
    client = Roll20Client()
    
    # Initialize (login, navigate, launch game)
    await client.initialize(headless=False)
    
    # Verify chat UI is ready
    await client.verify_chat_ui()
    
    # Do something with the chat...
    
    # Clean up
    await client.close()

asyncio.run(main())
```

### Testing

Run the test script to verify everything works:

```bash
python -m src.roll20.test_client
```

This will:
1. Start a browser window (non-headless for first run)
2. Log into Roll20
3. Navigate to your campaign
4. Click "Launch Game"
5. Wait for the editor to load
6. Verify all chat UI elements are present

**Note**: On the first run, you may need to manually complete Cloudflare challenges. After the first successful session, the browser profile should be persisted and subsequent runs should work automatically.

## Architecture

### Files

- **config.py**: Loads and validates environment variables
- **client.py**: Main browser automation client using nodriver
- **message.py**: (Future) Message formatting and sending logic
- **test_client.py**: Test script to verify the integration

### Client Methods

- `start(headless=True)`: Start the browser
- `login()`: Log into Roll20
- `navigate_to_campaign()`: Go to the campaign details page
- `launch_game()`: Click "Launch Game" and wait for editor to load
- `verify_chat_ui()`: Verify all required chat elements are present
- `initialize(headless=True)`: Complete initialization (all of the above)
- `close()`: Close the browser

## Chat UI Elements

Once the game is loaded, these elements are available:

- `#textchat-input`: Main chat input container
- `#textchat-input textarea`: Text input field
- `#speakingas`: Dropdown to select character/player
- `#chatSendBtn`: Send button

## Next Steps

The foundation is now in place. Future work will include:

1. **Message Sending**: Implement methods to send messages to the chat
2. **Private Messages**: Support for whispering to specific players/characters
3. **Character Selection**: Automatically select the correct character from the dropdown
4. **Error Handling**: Better handling of network issues, timeouts, etc.
5. **Session Persistence**: Improve session management to minimize re-logins

## Troubleshooting

### Cloudflare Challenges

If you encounter Cloudflare challenges:
1. Run with `headless=False`
2. Manually complete the challenge in the browser window
3. The session should persist for future runs

### Login Failures

If login fails:
1. Verify your credentials in `.env`
2. Check if Roll20 requires 2FA (not currently supported)
3. Try running with `headless=False` to see what's happening

### Game Not Loading

If the game doesn't load:
1. Verify your `ROLL20_CAMPAIGN_ID` is correct
2. Make sure you have access to the campaign
3. Check the browser console for errors (run with `headless=False`)

