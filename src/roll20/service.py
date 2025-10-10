"""
Roll20 Service for managing Roll20 chat interactions.

This module provides a high-level service interface for:
- Managing connection lifecycle (open, close)
- Sending whisper messages to Roll20 users
- Queuing messages for sequential delivery
- State management (Connecting, Ready, Sending, Closed)
"""

import asyncio
from enum import Enum
from typing import Optional

from .client import Roll20Client
from .message import send_message
from .verbose import vprint


class ServiceState(Enum):
    """States for the Roll20 service."""
    CONNECTING = "Connecting"
    READY = "Ready"
    SENDING = "Sending"
    CLOSED = "Closed"


class Roll20Service:
    """
    High-level service for Roll20 chat interactions.
    
    This service manages the Roll20 client lifecycle and provides
    a simple interface for sending whisper messages to users.
    
    Example usage:
        service = Roll20Service()
        await service.open()
        await service.send(["Player1", "Player2"], "Hello!")
        await service.close()
    """
    
    def __init__(self):
        self._client = Roll20Client()
        self._state = ServiceState.CLOSED
        self._message_queue: asyncio.Queue[tuple[list[str], str]] = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
    
    @property
    def state(self) -> ServiceState:
        """Get the current service state."""
        return self._state
    
    async def open(self, headless: bool = True) -> None:
        """
        Open the Roll20 service and connect to the campaign.
        
        This will:
        1. Start the browser
        2. Log in to Roll20
        3. Launch the game
        4. Set up the chat interface
        5. Start the message processing worker
        
        Args:
            headless: Whether to run the browser in headless mode.
                     Set to False for debugging or manual intervention.
        
        Raises:
            Exception: If initialization fails
        """
        if self._state != ServiceState.CLOSED:
            raise RuntimeError(f"Cannot open service in state {self._state.value}")
        
        print("Opening Roll20 service...")
        self._state = ServiceState.CONNECTING
        
        try:
            # Initialize the client (login, launch game, setup chat)
            await self._client.initialize(headless=headless)
            
            # Start the message processing worker
            self._worker_task = asyncio.create_task(self._process_queue())
            
            self._state = ServiceState.READY
            print("✓ Roll20 service is ready!")
            
        except Exception as e:
            self._state = ServiceState.CLOSED
            print(f"✗ Failed to open Roll20 service: {e}")
            raise
    
    async def send(self, to_users: list[str], message: str) -> None:
        """
        Send a whisper message to one or more users.
        
        This method queues the message for delivery and returns immediately.
        Messages are sent sequentially in the order they are queued.
        
        Args:
            to_users: List of Roll20 usernames to send the message to
            message: The message content to send
            
        Raises:
            RuntimeError: If the service is closed
        """
        if self._state == ServiceState.CLOSED:
            raise RuntimeError("Cannot send message: service is closed")
        
        # Queue the message for processing
        await self._message_queue.put((to_users, message))
        print(f"Queued message for {len(to_users)} user(s)")
    
    async def close(self) -> None:
        """
        Close the Roll20 service and clean up resources.
        
        This will:
        1. Stop accepting new messages
        2. Cancel the message processing worker
        3. Close the browser
        """
        if self._state == ServiceState.CLOSED:
            print("Service already closed")
            return
        
        print("Closing Roll20 service...")
        self._state = ServiceState.CLOSED
        
        # Cancel the worker task
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None
        
        # Close the client
        await self._client.close()
        
        print("✓ Roll20 service closed")
    
    async def _process_queue(self) -> None:
        """
        Background worker that processes queued messages.
        
        This runs continuously, pulling messages from the queue
        and sending them to the specified users.
        """
        print("Message processing worker started")
        
        try:
            while True:
                # Wait for a message from the queue
                to_users, message = await self._message_queue.get()

                vprint(f"\n[Service] Processing queued message:")
                vprint(f"  To users: {to_users}")
                vprint(f"  Message: {repr(message)}")

                # Transition to Sending state
                self._state = ServiceState.SENDING

                # Send the message to each user
                for username in to_users:
                    vprint(f"\n[Service] Sending to user '{username}'...")
                    await send_message(self._client, username, message)
                    vprint(f"  ✓ Sent to {username}")
                
                # Mark the task as done
                self._message_queue.task_done()
                
                # Transition back to Ready state
                self._state = ServiceState.READY
                
        except asyncio.CancelledError:
            print("Message processing worker cancelled")
            raise
        except Exception as e:
            print(f"Error in message processing worker: {e}")
            # Continue processing despite errors

