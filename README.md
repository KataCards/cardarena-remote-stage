# Chromium Kiosk Browser Engine

A production-ready Python browser engine based on Chromium that runs in full kiosk mode. Perfect for digital signage, information displays, embedded systems, and dedicated browser applications.

## Features

- **Full Kiosk Mode**: Runs Chromium without any browser UI (no address bar, tabs, or menus)
- **URL Rotation**: Automatically rotate through multiple URLs for digital signage
- **Programmatic Control**: Full API for navigation, script execution, and page interaction
- **Auto-Recovery**: Automatic restart on crashes with configurable retry limits
- **Embedded System Support**: Optimized for Raspberry Pi and other embedded Linux platforms
- **Environment Configuration**: Easy setup via environment variables or `.env` file
- **Production Ready**: Comprehensive error handling, logging, and resource management

## Requirements

- Python 3.13+
- Linux (X11 or Wayland) or macOS
- `uv` package manager

## Installation

### 1. Install uv (if not already installed)

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### 2. Clone or download this project

```bash
cd cardarena-remote-stage
```

### 3. Install dependencies using uv

```bash
# Sync all dependencies from pyproject.toml
uv sync

# Or install manually
uv pip install playwright pydantic pydantic-settings python-dotenv
```

### 4. Install Playwright browsers

```bash
# Install Chromium browser
uv run playwright install chromium

# Or install all browsers (chromium, firefox, webkit)
uv run playwright install

# For system dependencies (Linux only)
uv run playwright install-deps chromium
```

## Quick Start

### Basic Usage

```bash
# Run with default settings (opens example.com in kiosk mode)
uv run python main.py

# Or activate the virtual environment first
source .venv/bin/activate  # On Linux/macOS
python main.py
```

### Run Different Examples

```bash
# Example 1: Basic kiosk mode
uv run python main.py 1

# Example 2: URL rotation for digital signage
uv run python main.py 2

# Example 3: Context manager with programmatic control
uv run python main.py 3

# Example 4: Advanced programmatic control
uv run python main.py 4

# Example 5: Load configuration from .env file
uv run python main.py 5

# Example 6: Embedded system mode (Raspberry Pi optimized)
uv run python main.py 6
```

## Configuration

### Using Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Basic Settings
START_URL=https://your-website.com
KIOSK_MODE=true
WINDOW_WIDTH=1920
WINDOW_HEIGHT=1080

# URL Rotation
ENABLE_ROTATION=true
ROTATION_URLS=https://site1.com,https://site2.com,https://site3.com
ROTATION_INTERVAL=30

# Performance (for Raspberry Pi)
DISABLE_GPU=true
DISABLE_DEV_SHM=true
```

### Programmatic Configuration

```python
from config import KioskConfig
from kiosk_browser import KioskBrowser

# Create custom configuration
config = KioskConfig(
    start_url="https://your-website.com",
    kiosk_mode=True,
    window_width=1920,
    window_height=1080,
)

# Run browser
browser = KioskBrowser(config)
await browser.run()
```

## Usage Examples

### Example 1: Simple Kiosk Display

```python
import asyncio
from config import KioskConfig
from kiosk_browser import KioskBrowser

async def main():
    config = KioskConfig(
        start_url="https://your-dashboard.com",
        kiosk_mode=True,
    )
    
    browser = KioskBrowser(config)
    await browser.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Digital Signage with URL Rotation

```python
import asyncio
from config import KioskConfig
from kiosk_browser import KioskBrowser

async def main():
    config = KioskConfig(
        enable_rotation=True,
        rotation_urls=[
            "https://dashboard.example.com",
            "https://metrics.example.com",
            "https://news.example.com",
        ],
        rotation_interval=20,  # 20 seconds per page
        kiosk_mode=True,
    )
    
    browser = KioskBrowser(config)
    await browser.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 3: Programmatic Control

```python
import asyncio
from config import KioskConfig
from kiosk_browser import create_kiosk_browser

async def main():
    config = KioskConfig(
        start_url="https://example.com",
        kiosk_mode=False,  # Windowed mode for testing
    )
    
    async with create_kiosk_browser(config) as browser:
        # Navigate to pages
        await browser.navigate_to("https://example.com")
        await asyncio.sleep(2)
        
        # Execute JavaScript
        title = await browser.execute_script("document.title")
        print(f"Page title: {title}")
        
        # Take screenshot
        await browser.take_screenshot("screenshot.png")
        
        # Reload page
        await browser.reload_page()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 4: Raspberry Pi / Embedded System

```python
import asyncio
from config import KioskConfig
from kiosk_browser import KioskBrowser

async def main():
    config = KioskConfig(
        start_url="https://your-kiosk-app.com",
        kiosk_mode=True,
        window_width=1920,
        window_height=1080,
        # Performance optimizations for embedded systems
        disable_gpu=True,
        disable_dev_shm=True,
        page_load_timeout=60000,
        auto_restart_on_crash=True,
        max_restart_attempts=5,
    )
    
    browser = KioskBrowser(config)
    await browser.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `browser_type` | str | `"chromium"` | Browser type: chromium, chrome, msedge |
| `headless` | bool | `False` | Run in headless mode |
| `kiosk_mode` | bool | `True` | Enable full kiosk mode |
| `start_url` | str | `"https://www.google.com"` | Initial URL to load |
| `window_width` | int | `1920` | Browser window width |
| `window_height` | int | `1080` | Browser window height |
| `enable_rotation` | bool | `False` | Enable URL rotation |
| `rotation_urls` | list | `[]` | List of URLs to rotate |
| `rotation_interval` | int | `30` | Seconds between rotations |
| `disable_gpu` | bool | `False` | Disable GPU acceleration |
| `disable_dev_shm` | bool | `False` | Disable /dev/shm usage |
| `page_load_timeout` | int | `30000` | Page load timeout (ms) |
| `auto_restart_on_crash` | bool | `True` | Auto-restart on crash |
| `max_restart_attempts` | int | `3` | Max restart attempts |
| `log_level` | str | `"INFO"` | Logging level |

See `config.py` for complete list of options.

## API Reference

### KioskBrowser Class

#### Methods

- `async start()` - Initialize and start the browser
- `async stop()` - Stop the browser and cleanup resources
- `async run()` - Run the browser with auto-restart on crash
- `async navigate_to(url: str)` - Navigate to a URL
- `async reload_page()` - Reload the current page
- `async go_back()` - Navigate back in history
- `async go_forward()` - Navigate forward in history
- `async execute_script(script: str)` - Execute JavaScript
- `async take_screenshot(path: str)` - Take a screenshot
- `get_current_url()` - Get the current page URL

### Context Manager

```python
async with create_kiosk_browser(config) as browser:
    # Browser automatically starts and stops
    await browser.navigate_to("https://example.com")
```

## Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/kiosk-browser.service`:

```ini
[Unit]
Description=Chromium Kiosk Browser
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/cardarena-remote-stage
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/pi/.Xauthority"
ExecStart=/home/pi/cardarena-remote-stage/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable kiosk-browser
sudo systemctl start kiosk-browser
sudo systemctl status kiosk-browser
```

### Auto-start on Boot (Raspberry Pi)

Add to `~/.config/autostart/kiosk.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=Kiosk Browser
Exec=/home/pi/cardarena-remote-stage/.venv/bin/python /home/pi/cardarena-remote-stage/main.py
X-GNOME-Autostart-enabled=true
```

## Troubleshooting

### Browser won't start

```bash
# Install system dependencies
uv run playwright install-deps chromium

# Check Playwright installation
uv run playwright --version
```

### Display issues on Linux

```bash
# Set DISPLAY environment variable
export DISPLAY=:0

# For Wayland
export WAYLAND_DISPLAY=wayland-0
```

### Memory issues on Raspberry Pi

Enable these options in your config:

```python
config = KioskConfig(
    disable_gpu=True,
    disable_dev_shm=True,
)
```

### Permission errors

```bash
# Ensure proper permissions
chmod +x main.py

# For systemd service
sudo chown -R $USER:$USER /home/$USER/cardarena-remote-stage
```

## Development

### Install development dependencies

```bash
uv sync --extra dev
```

### Run tests

```bash
uv run pytest
```

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the project repository.