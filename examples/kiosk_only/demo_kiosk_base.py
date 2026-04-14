"""
Basic kiosk demo showcasing core functionality.

This demo demonstrates:
- Creating a PlaywrightEngine with visible browser
- Creating a PlaywrightKiosk with URL whitelisting
- Using async context manager for lifecycle management
- Accessing engine methods (get_current_url)
- Taking screenshots
- Checking health status
- Getting kiosk status
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


async def main():
    """Run the basic kiosk demo."""
    from kiosk.engine.playwright import PlaywrightEngine
    from kiosk.kiosk.playwright import PlaywrightKiosk

    print("\n=== Running Basic Kiosk Demo ===\n")

    # Create the Playwright engine
    engine = PlaywrightEngine(
        browser_type="chromium",
        headless=False,
        error_map={},
        resources={},
    )

    # Create the kiosk
    kiosk = PlaywrightKiosk(
        engine=engine,
        default_page="https://youtube.com",
        kiosk_name="Demo Kiosk",
        allowed_urls=["https://youtube.com"],
    )

    # Use async context manager to start the kiosk
    async with kiosk:
        # Print current URL
        current_url = await engine.get_current_url()
        print(f"Current URL: {current_url}")

        # Take a screenshot and save it
        screenshot_bytes = await kiosk.screenshot()
        with open("screenshot.png", "wb") as f:
            f.write(screenshot_bytes)
        print("Screenshot saved to screenshot.png")

        # Print health status
        is_healthy = await kiosk.is_healthy()
        print(f"Is healthy: {is_healthy}")

        # Print kiosk status
        status = await kiosk.get_status()
        print(f"Kiosk status: {status}")

        # Wait 5 seconds so the browser is visible
        print("Waiting 5 seconds...")
        await asyncio.sleep(5)

    print("Kiosk closed cleanly\n")


if __name__ == "__main__":
    asyncio.run(main())