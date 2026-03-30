#!/usr/bin/env python3
"""
Main entry point for the Chromium Kiosk Browser Engine.
Demonstrates various usage patterns and provides CLI interface.
"""

import asyncio
import sys
from pathlib import Path

from config import KioskConfig
from kiosk_browser import KioskBrowser, create_kiosk_browser


async def example_basic_usage():
    """
    Example 1: Basic usage with default configuration.
    Loads a single URL in kiosk mode.
    """
    print("=== Example 1: Basic Kiosk Mode ===\n")
    
    # Create config with custom start URL
    config = KioskConfig(
        start_url="https://www.example.com",
        kiosk_mode=True,
        window_width=1920,
        window_height=1080,
    )
    
    # Create and run browser
    browser = KioskBrowser(config)
    await browser.run()


async def example_url_rotation():
    """
    Example 2: URL rotation for digital signage.
    Rotates through multiple URLs at specified intervals.
    """
    print("=== Example 2: URL Rotation Mode ===\n")
    
    config = KioskConfig(
        enable_rotation=True,
        rotation_urls=[
            "https://www.google.com",
            "https://www.github.com",
            "https://www.wikipedia.org",
        ],
        rotation_interval=10,  # 10 seconds per URL
        kiosk_mode=True,
    )
    
    browser = KioskBrowser(config)
    await browser.run()


async def example_context_manager():
    """
    Example 3: Using context manager for controlled sessions.
    Useful for programmatic control and testing.
    """
    print("=== Example 3: Context Manager Usage ===\n")
    
    config = KioskConfig(
        start_url="https://www.python.org",
        kiosk_mode=False,  # Windowed mode for testing
        window_width=1280,
        window_height=720,
    )
    
    async with create_kiosk_browser(config) as browser:
        # Navigate to different pages
        await browser.navigate_to("https://www.python.org")
        await asyncio.sleep(3)
        
        await browser.navigate_to("https://docs.python.org")
        await asyncio.sleep(3)
        
        # Take a screenshot
        await browser.take_screenshot("screenshot.png")
        print("Screenshot saved to screenshot.png")
        
        # Execute JavaScript
        title = await browser.execute_script("document.title")
        print(f"Page title: {title}")
        
        # Wait a bit before closing
        await asyncio.sleep(2)


async def example_programmatic_control():
    """
    Example 4: Advanced programmatic control.
    Demonstrates navigation, script execution, and state management.
    """
    print("=== Example 4: Programmatic Control ===\n")
    
    config = KioskConfig(
        start_url="https://www.wikipedia.org",
        kiosk_mode=False,
        log_level="DEBUG",
    )
    
    browser = KioskBrowser(config)
    
    try:
        await browser.start()
        
        # Navigate to initial page
        await browser.navigate_to("https://www.wikipedia.org")
        await asyncio.sleep(2)
        
        # Get current URL
        current_url = browser.get_current_url()
        print(f"Current URL: {current_url}")
        
        # Execute custom JavaScript
        result = await browser.execute_script("""
            return {
                title: document.title,
                url: window.location.href,
                userAgent: navigator.userAgent
            }
        """)
        print(f"Page info: {result}")
        
        # Navigate to another page
        await browser.navigate_to("https://en.wikipedia.org/wiki/Python_(programming_language)")
        await asyncio.sleep(3)
        
        # Reload the page
        await browser.reload_page()
        await asyncio.sleep(2)
        
        # Go back
        await browser.go_back()
        await asyncio.sleep(2)
        
        print("Programmatic control demo completed")
        
    finally:
        await browser.stop()


async def example_from_env():
    """
    Example 5: Load configuration from environment variables.
    Create a .env file with your settings.
    """
    print("=== Example 5: Configuration from .env ===\n")
    
    # Config will automatically load from .env file if it exists
    config = KioskConfig()
    
    print(f"Loaded configuration:")
    print(f"  Start URL: {config.start_url}")
    print(f"  Kiosk Mode: {config.kiosk_mode}")
    print(f"  Window Size: {config.window_width}x{config.window_height}")
    print(f"  Rotation Enabled: {config.enable_rotation}")
    
    browser = KioskBrowser(config)
    await browser.run()


async def example_embedded_system():
    """
    Example 6: Configuration optimized for embedded systems (Raspberry Pi).
    Uses performance optimizations for limited resources.
    """
    print("=== Example 6: Embedded System Mode ===\n")
    
    config = KioskConfig(
        start_url="https://www.raspberrypi.org",
        kiosk_mode=True,
        window_width=1920,
        window_height=1080,
        disable_gpu=True,  # Disable GPU for better compatibility
        disable_dev_shm=True,  # Important for limited memory
        page_load_timeout=60000,  # Longer timeout for slower systems
        log_level="INFO",
    )
    
    browser = KioskBrowser(config)
    await browser.run()


def print_usage():
    """Print usage information."""
    print("""
Chromium Kiosk Browser Engine

Usage: python main.py [example_number]

Available Examples:
  1 - Basic kiosk mode with single URL
  2 - URL rotation for digital signage
  3 - Context manager usage with programmatic control
  4 - Advanced programmatic control demo
  5 - Load configuration from .env file
  6 - Embedded system optimized mode (Raspberry Pi)

If no example number is provided, runs Example 1 (basic kiosk mode).

Environment Variables:
  You can configure the browser using a .env file or environment variables.
  See config.py for all available options.

Examples:
  python main.py          # Run basic kiosk mode
  python main.py 2        # Run URL rotation example
  python main.py 5        # Load config from .env
    """)


async def main():
    """Main entry point."""
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            print_usage()
            return
        
        try:
            example_num = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid example number '{sys.argv[1]}'")
            print_usage()
            return
    else:
        example_num = 1
    
    # Run selected example
    examples = {
        1: example_basic_usage,
        2: example_url_rotation,
        3: example_context_manager,
        4: example_programmatic_control,
        5: example_from_env,
        6: example_embedded_system,
    }
    
    if example_num not in examples:
        print(f"Error: Example {example_num} not found")
        print_usage()
        return
    
    try:
        await examples[example_num]()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())