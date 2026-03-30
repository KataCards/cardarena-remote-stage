#!/usr/bin/env python3
"""
Chromium Kiosk Browser Engine - Main Entry Point

A production-ready browser engine for kiosk mode deployments.
Supports URL rotation, auto-restart, and embedded systems.
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.browser_engine import BrowserEngine
from utils.config import LocalConfig, config


def create_parser():
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="Chromium Kiosk Browser Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url https://example.com
  %(prog)s --rotate --urls https://site1.com https://site2.com --interval 20
  %(prog)s --embedded --url https://dashboard.local
  %(prog)s --config .env
        """
    )
    
    parser.add_argument(
        '--url',
        type=str,
        help='URL to load (default: from config)'
    )
    
    parser.add_argument(
        '--rotate',
        action='store_true',
        help='Enable URL rotation mode'
    )
    
    parser.add_argument(
        '--urls',
        nargs='+',
        type=str,
        help='List of URLs for rotation (requires --rotate)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        help='Rotation interval in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        help='Window width in pixels (default: 1920)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        help='Window height in pixels (default: 1080)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode'
    )
    
    parser.add_argument(
        '--no-kiosk',
        action='store_true',
        help='Disable kiosk mode (show browser UI)'
    )
    
    parser.add_argument(
        '--embedded',
        action='store_true',
        help='Embedded system mode (Raspberry Pi optimized)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to .env config file'
    )
    
    parser.add_argument(
        '--example',
        type=int,
        choices=[1, 2, 3, 4, 5],
        help='Run example: 1=basic, 2=rotation, 3=dynamic, 4=embedded, 5=error-handling'
    )
    
    return parser


async def run_basic_example():
    """Example 1: Basic kiosk mode."""
    print("=== Running Example 1: Basic Kiosk Mode ===")
    engine = BrowserEngine()
    try:
        await engine.run("https://www.example.com")
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await engine.shutdown()


async def run_rotation_example():
    """Example 2: URL rotation."""
    print("=== Running Example 2: URL Rotation ===")
    cfg = LocalConfig()
    cfg.enable_rotation = True
    cfg.rotation_urls = [
        "https://www.example.com",
        "https://www.google.com",
        "https://www.github.com"
    ]
    cfg.rotation_interval = 10
    
    engine = BrowserEngine(cfg)
    try:
        await engine.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await engine.shutdown()


async def run_dynamic_example():
    """Example 3: Dynamic control."""
    print("=== Running Example 3: Dynamic Control ===")
    engine = BrowserEngine()
    
    async def control_loop():
        await asyncio.sleep(2)
        urls = [
            "https://www.example.com",
            "https://www.google.com/search?q=chromium+kiosk",
            "https://www.github.com/topics/kiosk"
        ]
        
        for url in urls:
            print(f"Loading {url}")
            await engine.load_url(url)
            await asyncio.sleep(5)
        
        print("Navigating back...")
        await engine.navigate('back')
        await asyncio.sleep(2)
    
    try:
        await asyncio.gather(
            engine.run(),
            control_loop()
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await engine.shutdown()


async def run_embedded_example():
    """Example 4: Raspberry Pi optimized."""
    print("=== Running Example 4: Embedded System Mode ===")
    cfg = LocalConfig()
    cfg.headless = True
    cfg.disable_gpu = True
    cfg.disable_dev_shm = True
    cfg.window_width = 1920
    cfg.window_height = 1080
    cfg.page_load_timeout = 60000
    
    engine = BrowserEngine(cfg)
    try:
        await engine.run("https://www.example.com")
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await engine.shutdown()


async def run_error_handling_example():
    """Example 5: Error handling demonstration."""
    print("=== Running Example 5: Error Handling ===")
    cfg = LocalConfig()
    cfg.auto_restart_on_crash = True
    cfg.max_restart_attempts = 3
    
    engine = BrowserEngine(cfg)
    
    async def simulate_errors():
        await asyncio.sleep(3)
        bad_urls = [
            "https://nonexistent-domain-12345.com",
            "https://httpstat.us/500",
            "https://httpstat.us/404"
        ]
        
        for url in bad_urls:
            print(f"Attempting to load (expected to fail): {url}")
            await engine.load_url(url)
            await asyncio.sleep(8)
        
        print("Loading good URL...")
        await engine.load_url("https://www.httpbin.org/status/200")
        await asyncio.sleep(5)
    
    try:
        await asyncio.gather(
            engine.run(),
            simulate_errors()
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await engine.shutdown()


async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Run example if specified
    if args.example:
        examples = {
            1: run_basic_example,
            2: run_rotation_example,
            3: run_dynamic_example,
            4: run_embedded_example,
            5: run_error_handling_example,
        }
        await examples[args.example]()
        return
    
    # Build configuration from arguments
    cfg = config
    
    if args.embedded:
        cfg.headless = True
        cfg.disable_gpu = True
        cfg.disable_dev_shm = True
        cfg.page_load_timeout = 60000
    
    if args.url:
        cfg.start_url = args.url
    
    if args.rotate:
        cfg.enable_rotation = True
        if args.urls:
            cfg.rotation_urls = args.urls
    
    if args.interval:
        cfg.rotation_interval = args.interval
    
    if args.width:
        cfg.window_width = args.width
    
    if args.height:
        cfg.window_height = args.height
    
    if args.headless:
        cfg.headless = True
    
    if args.no_kiosk:
        cfg.kiosk_mode = False
    
    # Create and run browser
    engine = BrowserEngine(cfg)
    
    try:
        print(f"Starting Chromium Kiosk Browser...")
        print(f"URL: {cfg.start_url}")
        print(f"Kiosk Mode: {cfg.kiosk_mode}")
        print(f"Rotation: {cfg.enable_rotation}")
        if cfg.enable_rotation:
            print(f"URLs: {cfg.rotation_urls}")
            print(f"Interval: {cfg.rotation_interval}s")
        print("\nPress Ctrl+C to exit\n")
        
        await engine.run()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())