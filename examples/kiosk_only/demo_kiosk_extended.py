"""
Extended kiosk demo showcasing full-screen mode and page switching.

This demo demonstrates:
- Creating a full-screen kiosk using launch_args
- Navigating between multiple whitelisted pages
- Using go_home() to return to default page
- Automatic page switching with timed intervals
"""

from pathlib import Path
import asyncio
import sys

# Add src directory to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from kiosk.engine.playwright import PlaywrightEngine
from kiosk.kiosk.playwright import PlaywrightKiosk


async def main():
    """Run the extended kiosk demo."""
    print("\n=== Running Extended Kiosk Demo (Full-Screen) ===\n")

    # Create the Playwright engine with full-screen launch args
    engine = PlaywrightEngine(
        browser_type="chromium",
        headless=False,
        launch_args=[
            "--kiosk",             # True kiosk mode (perfect for Linux/Raspberry Pi)
            "--disable-infobars",  # Hide info bars
            "--no-first-run",      # Skip first run wizards
        ],
        error_map={},
        resources={},
    )

    # Create the kiosk with multiple allowed URLs
    kiosk = PlaywrightKiosk(
        engine=engine,
        default_page="https://www.wikipedia.org",
        kiosk_name="Extended Demo Kiosk",
        allowed_urls=[
            "https://www.wikipedia.org",
            "https://www.github.com",
        ],
    )

    # Use async context manager to start the kiosk
    async with kiosk:
        print(f"Started at default page: {await engine.get_current_url()}")
        print("Waiting 10 seconds...")
        await asyncio.sleep(10)

        # Navigate to second page
        print("\nNavigating to GitHub...")
        success = await kiosk.navigate("https://www.github.com")
        print(f"Navigation successful: {success}")
        print(f"Current URL: {await engine.get_current_url()}")
        print("Waiting 10 seconds...")
        await asyncio.sleep(10)

        # Go back home
        print("\nGoing back home...")
        success = await kiosk.go_home()
        print(f"Go home successful: {success}")
        print(f"Current URL: {await engine.get_current_url()}")
        print("Waiting 5 seconds before closing...")
        await asyncio.sleep(5)

    print("Extended kiosk demo closed cleanly\n")


if __name__ == "__main__":
    asyncio.run(main())