"""
Roll20 message formatting and posting.

This module handles:
- Formatting messages for Roll20 chat (whispers)
- Posting messages via the headless browser client
"""

from typing import TYPE_CHECKING

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
    return f'/w "{username}" {message}'


async def send_message(client: "Roll20Client", username: str, message: str) -> None:
    """
    Send a whisper message to a user via Roll20 chat.

    Args:
        client: The Roll20Client instance with initialized chat interface
        username: The Roll20 username to whisper to
        message: The message content
    """
    formatted_message = format_whisper(username, message)

    # Type the message into the chat textarea
    await client.chat_textarea.send_keys(formatted_message)

    # Click the send button
    await client.chat_send_button.click()

