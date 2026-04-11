"""
Kiosk Demo Launcher

Interactive launcher for kiosk package demos.

Available demos:
1. Basic Demo (demo_kiosk_base.py)
   - Core kiosk functionality
   - Screenshots and status checks
   - 5-second YouTube display

2. Extended Demo (demo_kiosk_extended.py)
   - Full-screen mode
   - Page switching between Wikipedia and GitHub
   - go_home() navigation
   - 10-second intervals

3. Both Demos
   - Run both demos sequentially
"""

import sys
import subprocess
from pathlib import Path


def print_menu():
    """Print the demo selection menu."""
    print("\n" + "=" * 50)
    print("Kiosk Package Demo Launcher")
    print("=" * 50)
    print("\nAvailable demos:")
    print("  1. Basic Demo")
    print("     - Core kiosk functionality")
    print("     - Screenshots and status checks")
    print("     - 5-second YouTube display")
    print()
    print("  2. Extended Demo")
    print("     - Full-screen mode")
    print("     - Page switching (Wikipedia ↔ GitHub)")
    print("     - go_home() navigation")
    print("     - 10-second intervals")
    print()
    print("  3. Both Demos")
    print("     - Run both demos sequentially")
    print()
    print("  0. Exit")
    print("=" * 50)


def run_demo(demo_file: str):
    """Run a demo script."""
    demo_path = Path(__file__).parent / demo_file
    if not demo_path.exists():
        print(f"\nError: Demo file '{demo_file}' not found!")
        return

    print(f"\nLaunching {demo_file}...\n")
    try:
        subprocess.run([sys.executable, str(demo_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError running demo: {e}")
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")


def main():
    """Main launcher loop."""
    while True:
        print_menu()
        choice = input("\nSelect a demo (0-3): ").strip()

        if choice == "0":
            print("\nExiting launcher. Goodbye!")
            break
        elif choice == "1":
            run_demo("demo_kiosk_base.py")
        elif choice == "2":
            run_demo("demo_kiosk_extended.py")
        elif choice == "3":
            run_demo("demo_kiosk_base.py")
            run_demo("demo_kiosk_extended.py")
        else:
            print("\nInvalid choice. Please select 0, 1, 2, or 3.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nLauncher interrupted. Goodbye!")
        sys.exit(0)