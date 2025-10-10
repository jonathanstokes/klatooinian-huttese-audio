"""
Roll20 integration feature: Post-text-to-Roll20.

This package handles:
- Browser automation for Roll20 using nodriver (bypasses Cloudflare)
- Message formatting and posting to Roll20 chat
- Roll20-specific configuration from environment variables
- High-level service for managing Roll20 interactions

Main components:
- Roll20Service: High-level service for sending messages (recommended)
- Roll20Client: Low-level browser automation client
- Roll20Config: Configuration management
"""

from .client import Roll20Client
from .config import Roll20Config, config
from .service import Roll20Service, ServiceState

__all__ = ["Roll20Service", "ServiceState", "Roll20Client", "Roll20Config", "config"]
