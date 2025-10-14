"""
Test script to demonstrate screenshot capture on failure.

This script intentionally causes an initialization failure to demonstrate
the screenshot capture functionality.

Usage:
    python -m src.roll20.test_screenshot
"""

import asyncio
from .client import Roll20Client


async def main():
    """Test screenshot capture on failure."""
    
    print("=" * 60)
    print("Roll20 Screenshot Capture Test")
    print("=" * 60)
    print("\nThis test will attempt to initialize in headless mode.")
    print("If initialization fails, a screenshot will be captured.\n")
    
    client = Roll20Client()
    
    try:
        # Try to initialize in headless mode
        await client.initialize(headless=True)
        
        print("\n✓ Initialization succeeded!")
        print("No screenshot needed.")
        
        # Keep browser open briefly
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"\n✗ Initialization failed (as expected for testing)")
        print(f"Error: {e}")
        print("\nCheck the screenshots/ directory for the captured screenshot.")
        
    finally:
        await client.close()
        print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(main())

