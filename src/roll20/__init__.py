"""
Roll20 integration feature: Post-text-to-Roll20.

This package handles:
- Browser automation for Roll20 using nodriver (bypasses Cloudflare)
- Message formatting and posting to Roll20 chat
- Roll20-specific configuration from environment variables

Main components:
- Roll20Client: Browser automation client
- Roll20Config: Configuration management
"""

from .client import Roll20Client
from .config import Roll20Config, config

__all__ = ["Roll20Client", "Roll20Config", "config"]
