"""
Roll20 message formatting and posting.

This module handles:
- Formatting messages for Roll20 chat (whispers)
- Posting messages via the headless browser client
"""

import asyncio
import json
from typing import TYPE_CHECKING

from .verbose import vprint

if TYPE_CHECKING:
    from .client import Roll20Client


def format_whisper(username: str, message: str) -> str:
    """
    Format a whisper message for Roll20 chat.

    Args:
        username: The Roll20 username to whisper to
        message: The message content

    Returns:
        Formatted whisper command: /w "username" message
    """
    # Replace double-quotes with single-quotes in the message to avoid confusing Roll20's parser
    sanitized_message = message.replace('"', "'")
    return f'/w "{username}" {sanitized_message}'


async def send_message(client: "Roll20Client", username: str, message: str) -> None:
    """
    Send a whisper message to a user via Roll20 chat.

    Args:
        client: The Roll20Client instance with initialized chat interface
        username: The Roll20 username to whisper to
        message: The message content
    """
    formatted_message = format_whisper(username, message)

    vprint(f"\n[Message] Formatting and sending:")
    vprint(f"  Username: {repr(username)}")
    vprint(f"  Message: {repr(message)}")
    vprint(f"  Formatted whisper: {repr(formatted_message)}")

    # Use JavaScript to set the textarea value and click send
    # This is more reliable than using nodriver's DOM methods
    vprint(f"  Setting textarea value and clicking send...")

    # Escape backslashes and single quotes for JavaScript string literal
    # We use single quotes in JS so we only need to escape single quotes and backslashes
    js_safe_message = formatted_message.replace('\\', '\\\\').replace("'", "\\'")

    script = f"""
        // Get the textarea
        var textarea = document.querySelector("#textchat-input textarea");
        if (!textarea) {{
            throw new Error("Could not find chat textarea");
        }}

        // Clear and set the value
        textarea.value = "";
        textarea.value = '{js_safe_message}';

        // Click the send button
        var sendBtn = document.getElementById("chatSendBtn");
        if (!sendBtn) {{
            throw new Error("Could not find send button");
        }}
        sendBtn.click();
    """

    await client.page.evaluate(script)

    vprint(f"  ✓ Message sent!")

