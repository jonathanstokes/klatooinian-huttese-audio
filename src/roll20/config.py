"""
Roll20-specific configuration.

This module handles:
- Roll20 credentials and campaign configuration from environment variables
- Browser automation settings
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Roll20Config:
    """Configuration for Roll20 integration."""
    
    def __init__(self):
        self.username = os.getenv("ROLL20_USERNAME")
        self.password = os.getenv("ROLL20_PASSWORD")
        self.campaign_id = os.getenv("ROLL20_CAMPAIGN_ID")
        
        # Validate required configuration
        if not self.username:
            raise ValueError("ROLL20_USERNAME environment variable is required")
        if not self.password:
            raise ValueError("ROLL20_PASSWORD environment variable is required")
        if not self.campaign_id:
            raise ValueError("ROLL20_CAMPAIGN_ID environment variable is required")
    
    @property
    def campaign_url(self) -> str:
        """Get the campaign details URL."""
        return f"https://app.roll20.net/campaigns/details/{self.campaign_id}"
    
    @property
    def login_url(self) -> str:
        """Get the Roll20 login URL."""
        return "https://app.roll20.net/sessions/new"


# Global config instance
config = Roll20Config()

