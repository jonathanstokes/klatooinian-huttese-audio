"""
Roll20 browser automation client using nodriver.

This module handles:
- Logging into Roll20 using nodriver (bypasses Cloudflare anti-bot)
- Navigating to a specific campaign
- Launching the game
- Accessing the in-game chat interface
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

import nodriver as uc

from .config import config


class Roll20Client:
    """Client for automating Roll20 interactions using nodriver."""

    def __init__(self):
        self.browser: Optional[uc.Browser] = None
        self.page: Optional[uc.Tab] = None
        self._logged_in = False
        self._game_loaded = False
        self._headless = True  # Track headless mode for error handling

        # We don't need element references anymore - we use JavaScript directly

    async def capture_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Capture a screenshot of the current page.

        Args:
            filename: Optional filename. If not provided, uses timestamp.

        Returns:
            Path to the saved screenshot, or None if capture failed.
        """
        if not self.page:
            print("Cannot capture screenshot: no page loaded")
            return None

        try:
            # Create screenshots directory if it doesn't exist
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)

            # Generate filename with timestamp if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"roll20_error_{timestamp}.png"

            # Ensure .png extension
            if not filename.endswith('.png'):
                filename += '.png'

            filepath = screenshots_dir / filename

            print(f"Capturing screenshot to: {filepath}")
            await self.page.save_screenshot(str(filepath))
            print(f"✓ Screenshot saved: {filepath}")

            return str(filepath)

        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None

    async def capture_dom(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Capture the DOM (HTML) of the current page.

        Args:
            filename: Optional filename. If not provided, uses timestamp.

        Returns:
            Path to the saved HTML file, or None if capture failed.
        """
        if not self.page:
            print("Cannot capture DOM: no page loaded")
            return None

        try:
            # Create screenshots directory if it doesn't exist (reuse same dir)
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)

            # Generate filename with timestamp if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"roll20_error_{timestamp}.html"

            # Ensure .html extension
            if not filename.endswith('.html'):
                filename += '.html'

            filepath = screenshots_dir / filename

            print(f"Capturing DOM to: {filepath}")

            # Get the page HTML
            html = await self.page.get_content()

            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            print(f"✓ DOM saved: {filepath}")

            return str(filepath)

        except Exception as e:
            print(f"Failed to capture DOM: {e}")
            return None

    async def start(self, headless: bool = False):
        """
        Start the browser and navigate to Roll20.

        Args:
            headless: Whether to run in headless mode. Default is False (headful)
                     because Cloudflare detection is more reliable with a visible browser.
                     Set to True to run headless, but note that Cloudflare may block it.

        Returns:
            True if already logged in, False if login is needed
        """
        self._headless = headless

        if headless:
            print(f"Starting browser in HEADLESS mode...")
            print("Note: Cloudflare may block headless browsers. If you encounter issues,")
            print("try running in headful mode (headless=False).")
        else:
            print(f"Starting browser in HEADFUL mode (browser will be visible)...")

        # Chrome preferences to disable password manager
        prefs = {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
        }

        # Browser arguments for better headless mode and Cloudflare bypass
        browser_args = []

        if headless:
            # Use new headless mode which is harder to detect
            browser_args.extend([
                '--headless=new',
                # Additional args to make headless mode less detectable
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--allow-running-insecure-content',
            ])

        # Create config
        config = uc.Config(
            headless=headless,
            prefs=prefs,
            browser_args=browser_args if browser_args else None,
        )

        self.browser = await uc.start(config)

        # Always start by going to the main Roll20 page
        print("Navigating to https://app.roll20.net...")
        self.page = await self.browser.get("https://app.roll20.net")

        # Wait for page to load and potential redirect
        await asyncio.sleep(3)

        current_url = self.page.url
        print(f"Current URL: {current_url}")

        # Check if we were redirected to login
        if "/login" in current_url:
            print("Not logged in - on login page")
            return False

        # Even if we're at the main page, we might not be logged in
        # The page might just not redirect immediately
        # Let's check if we can see login-related elements
        print("Checking if actually logged in...")

        # Wait a bit more to see if page redirects
        await asyncio.sleep(2)
        current_url = self.page.url

        if "/login" in current_url:
            print("Redirected to login page")
            return False

        # If we're still on the main page, assume we're logged in
        # (We'll find out for sure when we try to access the campaign)
        print("Appears to be logged in (no redirect to login)")
        self._logged_in = True
        return True

    async def login(self):
        """Log into Roll20 using credentials from config."""
        if self._logged_in:
            print("Already logged in")
            return

        current_url = self.page.url

        # If we're not on the login page, navigate there
        if "/login" not in current_url:
            print("Navigating to login page...")
            await self.page.get("https://app.roll20.net/login")
            await asyncio.sleep(3)

        # Wait briefly for the form to be fully interactive
        await asyncio.sleep(2)

        # Find and fill the email field
        print("Looking for email field...")
        email_field = await self.page.select("input#email")
        if not email_field:
            email_field = await self.page.select("input[name='email']")

        if email_field:
            await email_field.click()
            await asyncio.sleep(0.3)
            await email_field.send_keys(config.username)
            print(f"✓ Entered email: {config.username}")
        else:
            raise Exception("Could not find email input field")

        # Find and fill the password field
        print("Looking for password field...")
        password_field = await self.page.select("input#password")
        if not password_field:
            password_field = await self.page.select("input[name='password']")

        if password_field:
            await password_field.click()
            await asyncio.sleep(0.2)
            await password_field.send_keys(config.password)
            print("✓ Entered password")
        else:
            raise Exception("Could not find password input field")

        # Find and click the login button
        print("Looking for login button...")
        login_button = await self.page.select("button#login")
        if not login_button:
            login_button = await self.page.select("button[type='submit']")

        if login_button:
            print("Clicking login button...")
            await login_button.click()
        else:
            raise Exception("Could not find login button")

        # Wait for login to complete and page to load
        print("Waiting for login to complete...")
        await asyncio.sleep(10)

        # Check if we're logged in
        current_url = self.page.url
        print(f"Current URL after login: {current_url}")

        if "/login" in current_url:
            raise Exception("Login may have failed - still on login page. Check credentials or captcha.")

        self._logged_in = True
        print("✓ Login successful!")

    async def launch_game(self):
        """Navigate directly to the game editor using the setcampaign URL."""
        if not self._logged_in:
            raise Exception("Must be logged in before launching game")

        if self._game_loaded:
            print("Game already loaded")
            return

        # Use the direct setcampaign URL to launch/join the game
        editor_url = f"https://app.roll20.net/editor/setcampaign/{config.campaign_id}"
        print(f"Launching game: {editor_url}")

        await self.page.get(editor_url)

        # Wait for the page to load
        await asyncio.sleep(15)

        # Check if we got redirected to login (means we weren't actually logged in)
        current_url = self.page.url
        if "/login" in current_url:
            print("Got redirected to login - we weren't actually logged in!")
            self._logged_in = False
            # Now perform the login
            await self.login()
            # Try launching the game again
            print(f"Retrying game launch: {editor_url}")
            await self.page.get(editor_url)
            await asyncio.sleep(15)
            current_url = self.page.url

        # Wait for the URL to change FROM setcampaign to the actual editor
        # The setcampaign URL is a redirect page, not the actual editor
        print("Waiting for redirect from setcampaign to actual editor...")
        max_wait = 60  # Increased wait time for headless mode
        waited = 0
        while waited < max_wait:
            current_url = self.page.url
            # We want the editor URL but NOT the setcampaign URL
            if "editor" in current_url and "setcampaign" not in current_url and "/login" not in current_url:
                print(f"✓ Editor loaded! URL: {current_url}")
                break
            if waited % 5 == 0:  # Print status every 5 seconds
                print(f"  Still waiting... Current URL: {current_url}")
            await asyncio.sleep(1)
            waited += 1

        current_url = self.page.url

        # Check if we're still on setcampaign (redirect didn't happen)
        if "setcampaign" in current_url:
            print(f"Warning: Still on setcampaign URL after {max_wait}s: {current_url}")
            print("The page may not have redirected automatically.")

            # Try to find and click a "Join Game" or "Launch" button
            print("Looking for a button to click to enter the game...")

            # Check for common button texts
            button_texts = ["Join Game", "Launch", "Play Now", "Enter Game", "Continue"]
            button_found = False

            for button_text in button_texts:
                try:
                    # Try to find button by text content
                    script = f"""
                        (function() {{
                            var buttons = Array.from(document.querySelectorAll('button, a, input[type="button"], input[type="submit"]'));
                            var button = buttons.find(b => b.textContent.includes('{button_text}') || b.value === '{button_text}');
                            if (button) {{
                                return {{ found: true, text: button.textContent || button.value }};
                            }}
                            return {{ found: false }};
                        }})()
                    """
                    result = await self.page.evaluate(script)
                    if result.get('found'):
                        print(f"  Found button: {result.get('text')}")
                        # Click it
                        click_script = f"""
                            (function() {{
                                var buttons = Array.from(document.querySelectorAll('button, a, input[type="button"], input[type="submit"]'));
                                var button = buttons.find(b => b.textContent.includes('{button_text}') || b.value === '{button_text}');
                                if (button) {{
                                    button.click();
                                    return true;
                                }}
                                return false;
                            }})()
                        """
                        clicked = await self.page.evaluate(click_script)
                        if clicked:
                            print(f"  ✓ Clicked button")
                            button_found = True
                            # Wait for redirect after clicking
                            await asyncio.sleep(10)
                            current_url = self.page.url
                            if "setcampaign" not in current_url:
                                print(f"  ✓ Redirected to: {current_url}")
                                break
                except Exception as e:
                    print(f"  Error checking for '{button_text}': {e}")

            if not button_found:
                print("  No button found. The page might load the editor in place.")
                print("  Continuing anyway - chat UI check will determine if we're ready.")

        elif "editor" not in current_url or "/login" in current_url:
            raise Exception(f"Editor did not load. Current URL: {current_url}")
        else:
            print(f"✓ Successfully redirected to editor: {current_url}")

        self._game_loaded = True
        print("✓ Game loaded successfully!")


    async def _dismiss_dialog_with_retry(self, dialog_name: str, content_selector: str, button_selector: str, max_attempts: int = 15):
        """
        Dismiss a dialog with retry logic.

        Args:
            dialog_name: Name of the dialog for logging
            content_selector: Selector for the dialog content to wait for
            button_selector: Selector for the button to click
            max_attempts: Maximum number of attempts (default 15, increased for headless mode)
        """
        for attempt in range(max_attempts):
            try:
                # (a) Wait for the content to appear
                print(f"  [{dialog_name}] Attempt {attempt + 1}/{max_attempts}: Waiting for dialog to appear...")
                content = None
                for wait_attempt in range(10):  # Wait up to 10 seconds
                    content = await self.page.select(content_selector)
                    if content:
                        break
                    await asyncio.sleep(1)

                if not content:
                    if attempt < max_attempts - 1:
                        print(f"  [{dialog_name}] Dialog did not appear, retrying...")
                        continue
                    else:
                        print(f"  [{dialog_name}] Dialog did not appear after {max_attempts} attempts, skipping")
                        return

                print(f"  [{dialog_name}] ✓ Dialog appeared")

                # (b) Wait for the target button to be clickable
                button = None
                for wait_attempt in range(5):  # Wait up to 5 seconds
                    button = await self.page.select(button_selector)
                    if button:
                        break
                    await asyncio.sleep(1)

                if not button:
                    print(f"  [{dialog_name}] Button not found, retrying...")
                    continue

                print(f"  [{dialog_name}] ✓ Button found and clickable")

                # (c) Click it
                await button.click()
                print(f"  [{dialog_name}] ✓ Clicked button")
                await asyncio.sleep(0.5)
                
                # Dialog should dismiss - stop retrying
                print(f"  [{dialog_name}] ✓ Button clicked, assuming dialog will dismiss")
                return
                
            except Exception as e:
                print(f"  [{dialog_name}] Error: {e}")
                if attempt < max_attempts - 1:
                    print(f"  [{dialog_name}] Retrying...")
                    await asyncio.sleep(1)

        print(f"  [{dialog_name}] Failed to dismiss after {max_attempts} attempts")

    async def dismiss_dialogs(self):
        """Dismiss various dialogs that may appear after game loads."""
        print("\nDismissing post-load dialogs (in background)...")

        # Start both dialog dismissal tasks in parallel immediately
        skip_tour_task = asyncio.create_task(
            self._dismiss_dialog_with_retry(
                "Skip Tour",
                ".shepherd-element",  # The tour dialog container
                "button.shepherd-button-secondary"  # The skip button
            )
        )

        welcome_modal_task = asyncio.create_task(
            self._dismiss_dialog_with_retry(
                "Welcome Modal",
                ".ui-dialog",  # The modal dialog container
                ".ui-dialog-titlebar-close"  # The close button
            )
        )

        # Wait for both tasks to complete
        await asyncio.gather(skip_tour_task, welcome_modal_task)

        print("✓ Dialog dismissal complete")

    async def setup_chat_interface(self):
        """Set up the chat interface by selecting the last character."""
        print("\nSetting up chat interface...")

        # Use JavaScript to get dropdown options and select the last one
        print("Selecting last character from dropdown...")

        script = """
            (function() {
                var select = document.getElementById("speakingas");
                if (!select) {
                    return { success: false, error: "Dropdown not found" };
                }

                var options = select.options;
                if (!options || options.length === 0) {
                    return { success: false, error: "No options found" };
                }

                // Get the last option
                var lastOption = options[options.length - 1];
                var lastValue = lastOption.value;
                var lastText = lastOption.text;

                // Select it
                select.value = lastValue;

                // Trigger change event
                var event = new Event('change', { bubbles: true });
                select.dispatchEvent(event);

                // Also try jQuery if available
                if (window.jQuery) {
                    jQuery(select).trigger('change');
                }

                return {
                    success: true,
                    value: lastValue,
                    text: lastText,
                    optionCount: options.length
                };
            })()
        """

        try:
            result = await self.page.evaluate(script)
            if result.get('success'):
                print(f"  ✓ Found {result.get('optionCount')} options")
                print(f"  ✓ Selected: {result.get('text')}")
            else:
                print(f"  Warning: {result.get('error')}")
                print(f"  Continuing anyway - default selection may be fine")
        except Exception as e:
            print(f"  Warning: Could not select dropdown option: {e}")
            print(f"  Continuing anyway - default selection may be fine")

        print("\n✓ Chat interface ready!")

    async def verify_chat_ui(self):
        """Verify that the chat UI elements are present, with retries."""
        print("\nVerifying chat UI elements...")
        print("(This may take a while as the page finishes loading...)")

        # Use JavaScript to check for elements - much faster and more reliable
        # Try multiple times with shorter waits
        # Increased for headless mode where things can be slower to render
        max_attempts = 40
        for attempt in range(max_attempts):
            try:
                # Check each element individually using JavaScript
                chat_input_exists = await self.page.evaluate('!!document.querySelector("#textchat-input")')
                textarea_exists = await self.page.evaluate('!!document.querySelector("#textchat-input textarea")')
                speaking_as_exists = await self.page.evaluate('!!document.querySelector("#speakingas")')
                send_btn_exists = await self.page.evaluate('!!document.querySelector("#chatSendBtn")')

                all_found = chat_input_exists and textarea_exists and speaking_as_exists and send_btn_exists

                if all_found:
                    # All elements found!
                    print("  ✓ Found #textchat-input")
                    print("  ✓ Found textarea")
                    print("  ✓ Found #speakingas dropdown")
                    print("  ✓ Found #chatSendBtn")
                    print("\n✓ All chat UI elements verified!")
                    return True
                else:
                    # Show which elements are missing
                    missing = []
                    if not chat_input_exists: missing.append('#textchat-input')
                    if not textarea_exists: missing.append('textarea')
                    if not speaking_as_exists: missing.append('#speakingas')
                    if not send_btn_exists: missing.append('#chatSendBtn')

                    if attempt < max_attempts - 1:
                        print(f"  Attempt {attempt + 1}/{max_attempts}: Missing {', '.join(missing)}, waiting 1 second...")
                        await asyncio.sleep(1)
                    else:
                        raise Exception(f"Missing elements: {', '.join(missing)}")

            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"  Attempt {attempt + 1}/{max_attempts}: Error checking UI: {e}, waiting 1 second...")
                    await asyncio.sleep(1)
                else:
                    # Last attempt failed
                    raise Exception(f"Chat UI elements not found after {max_attempts} attempts: {e}")

        return True

    async def initialize(self, headless: bool = False):
        """
        Complete initialization: start browser, login, and launch game.

        Args:
            headless: Whether to run in headless mode. Default is False (headful)
                     because Cloudflare detection is more reliable with a visible browser.
                     Set to True to run headless, but note that Cloudflare may block it.
        """
        try:
            already_logged_in = await self.start(headless=headless)

            if not already_logged_in:
                await self.login()

            await self.login()

            await self.launch_game()

            # Start dismissing dialogs in the background (don't wait for it)
            asyncio.create_task(self.dismiss_dialogs())

            await self.verify_chat_ui()

            # Set up chat interface immediately - dialogs can continue dismissing in background
            await self.setup_chat_interface()

            print("\n" + "=" * 60)
            print("✅ Roll20 client fully initialized and ready!")
            print("=" * 60)

        except Exception as e:
            print("\n" + "=" * 60)
            print("❌ INITIALIZATION FAILED")
            print("=" * 60)
            print(f"Error: {e}")

            # Capture screenshot and DOM on failure (especially useful in headless mode)
            if self.page:
                print("\nAttempting to capture screenshot and DOM for debugging...")

                # Capture both screenshot and DOM with same timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                screenshot_path = await self.capture_screenshot(f"roll20_error_{timestamp}.png")
                dom_path = await self.capture_dom(f"roll20_error_{timestamp}.html")

                if screenshot_path:
                    print(f"Screenshot saved to: {screenshot_path}")
                if dom_path:
                    print(f"DOM saved to: {dom_path}")

                if screenshot_path or dom_path:
                    print("These can help diagnose what went wrong in headless mode.")

            # Re-raise the exception so caller knows initialization failed
            raise

    async def close(self):
        """Close the browser."""
        if self.browser:
            print("\nClosing browser...")
            try:
                # browser.stop() is not async in nodriver, just call it directly
                self.browser.stop()
            except Exception as e:
                print(f"Error closing browser: {e}")
            self.browser = None
            self.page = None
            self._logged_in = False
            self._game_loaded = False
