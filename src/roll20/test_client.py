"""
Test script for Roll20 client.

This script tests the Roll20 integration by:
1. Starting the browser
2. Logging in (if needed)
3. Launching the game via setcampaign URL
4. Verifying the chat UI is present

Usage:
    python -m src.roll20.test_client              # Run in headful mode (default, browser visible)
    python -m src.roll20.test_client --headless   # Run in headless mode (may be blocked by Cloudflare)
"""

import asyncio
import sys
from .client import Roll20Client


async def main():
    """Test the Roll20 client initialization."""
    
    # Parse command line arguments - default is headful now
    headless = False
    if "--headless" in sys.argv:
        headless = True

    client = Roll20Client()

    try:
        print("=" * 60)
        print("Roll20 Client Test")
        print("=" * 60)

        if headless:
            print("\nRunning in HEADLESS mode")
            print("Note: Cloudflare may block headless browsers.\n")
        else:
            print("\nRunning in HEADFUL mode (browser visible)")
            print("If Cloudflare challenges appear, complete them manually.\n")
        
        # Initialize the client (this does everything)
        await client.initialize(headless=headless)
        
        # Different wait times for headless vs headful
        if headless:
            wait_time = 30
            print(f"\nThe browser will stay open for {wait_time} seconds so you can inspect it.")
        else:
            wait_time = 300
            print(f"\nThe browser will stay open for {wait_time} seconds (5 minutes) so you can inspect it.")
        
        print("Press Ctrl+C to close early.\n")
        
        # Keep the browser open for inspection
        await asyncio.sleep(wait_time)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()
        print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(main())

