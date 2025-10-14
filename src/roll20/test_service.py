"""
Test script for Roll20 service.

This script tests the Roll20 service by:
1. Opening the service (connects to Roll20)
2. Sending test whisper messages to users
3. Closing the service

Usage:
    python -m src.roll20.test_service              # Run in headful mode (default, browser visible)
    python -m src.roll20.test_service --headless   # Run in headless mode (may be blocked by Cloudflare)
"""

import asyncio
import sys
from .service import Roll20Service


async def main():
    """Test the Roll20 service."""
    
    # Parse command line arguments - default is headful now
    headless = False
    if "--headless" in sys.argv:
        headless = True

    service = Roll20Service()

    try:
        print("=" * 60)
        print("Roll20 Service Test")
        print("=" * 60)

        if headless:
            print("\nRunning in HEADLESS mode")
            print("Note: Cloudflare may block headless browsers.\n")
        else:
            print("\nRunning in HEADFUL mode (browser visible)")
            print("If Cloudflare challenges appear, complete them manually.\n")
        
        # Open the service
        print("Opening service...")
        await service.open(headless=headless)
        
        print(f"\nService state: {service.state.value}")
        
        # Send a test message
        print("\nSending test messages...")
        
        # Example: Send to a test user
        # Replace "TestPlayer" with an actual username in your campaign
        test_users = ["TestPlayer"]
        test_message = "This is a test message from the Roll20 service!"
        
        await service.send(test_users, test_message)
        
        print(f"\nMessage queued. Service state: {service.state.value}")
        
        # Wait a bit for the message to be sent
        print("\nWaiting for messages to be sent...")
        await asyncio.sleep(5)
        
        print(f"Service state: {service.state.value}")
        
        # Send another message to test queuing
        print("\nSending another test message...")
        await service.send(test_users, "Second test message!")
        
        # Wait for it to be sent
        await asyncio.sleep(5)
        
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
        await service.close()
        print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(main())

