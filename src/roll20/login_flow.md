# Roll20 Login Flow

This document describes the login flow implemented in the Roll20 client.

## Flow Overview

1. **Navigate to https://app.roll20.net**
   - If session is persisted → redirects to dashboard (logged in)
   - If no session → redirects to `/login`

2. **Login Page** (if needed)
   - May show Cloudflare captcha (user must complete manually in headful mode)
   - Shows login form with:
     - Email field: `input#email` or `input[name='email']`
     - Password field: `input#password` or `input[name='password']`
     - Login button: `button#login` or `button[type='submit']`

3. **After Login**
   - Page redirects away from `/login`
   - Session is now established

4. **Launch Game**
   - Navigate to: `https://app.roll20.net/editor/setcampaign/<campaign-id>`
   - This directly launches/joins the game
   - Redirects to the editor: `https://app.roll20.net/editor/...`

5. **Verify Chat UI**
   - Check for required elements:
     - `#textchat-input` - main container
     - `#textchat-input textarea` - text input
     - `#speakingas` - character/player dropdown
     - `#chatSendBtn` - send button

## Implementation Details

### Client Methods

- `start(headless=True)` - Start browser, navigate to app.roll20.net, check if logged in
- `login()` - Fill login form and submit (only if not already logged in)
- `launch_game()` - Navigate to setcampaign URL to launch the game
- `verify_chat_ui()` - Confirm all chat elements are present
- `initialize(headless=True)` - Run all of the above in sequence

### Headless vs Headful

- **Headless** (default): Browser runs in background, faster, no GUI
- **Headful** (`--headful` flag): Browser window visible, needed for:
  - Debugging
  - Completing Cloudflare captchas
  - First-time login (to establish session)

### Session Persistence

The `nodriver` library automatically persists browser sessions, so:
- First run: May need headful mode for captcha
- Subsequent runs: Can use headless mode (session already established)

## Testing

Run the test script:

```bash
# Headful mode (recommended for first run and debugging)
python -m src.roll20.test_client --headful

# Headless mode (for automation after session is established)
python -m src.roll20.test_client
```

## Troubleshooting

### Stuck on Login Page

If the client reports "still on login page" after login attempt:
1. Run with `--headful` to see what's happening
2. Check if there's a captcha that needs manual completion
3. Verify credentials in `.env` are correct
4. Check for any error messages in the browser

### Cloudflare Challenges

If you see Cloudflare challenges:
1. Must run with `--headful` flag
2. Complete the challenge manually
3. The session will persist for future runs
4. Subsequent runs can use headless mode

### Game Not Loading

If the game doesn't load after login:
1. Verify `ROLL20_CAMPAIGN_ID` is correct
2. Make sure you have access to the campaign
3. Check the browser console for errors (run with `--headful`)

