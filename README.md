# Chromium Kiosk Browser Engine

A production-ready Python browser engine based on Chromium that runs in full kiosk mode. Perfect for digital signage, information displays, embedded systems, and dedicated browser applications.

## Features

- **Full Kiosk Mode**: Runs Chromium without any browser UI (no address bar, tabs, or menus)
- **URL Rotation**: Automatically rotate through multiple URLs for digital signage
- **Auto-Recovery**: Automatic restart on crashes with configurable retry limits
- **Embedded System Support**: Optimized for Raspberry Pi and other embedded Linux platforms
- **CLI Interface**: Simple command-line interface with argparse
- **Production Ready**: Comprehensive error handling, logging, and resource management

## Quick Start

### 1. Install Dependencies

```bash
# Install uv package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Install Chromium browser
uv run playwright install chromium
```

### 2. Run the Browser

```bash
# Basic usage (default URL)
uv run python src/main.py

# Load specific URL
uv run python src/main.py --url https://example.com

# URL rotation for digital signage
uv run python src/main.py --rotate --urls https://site1.com https://site2.com --interval 20

# Embedded system mode (Raspberry Pi)
uv run python src/main.py --embedded --url https://dashboard.local

# Run examples
uv run python src/main.py --example 1  # Basic kiosk
uv run python src/main.py --example 2  # URL rotation
uv run python src/main.py --example 3  # Dynamic control
uv run python src/main.py --example 4  # Embedded system
uv run python src/main.py --example 5  # Error handling
```

## Command-Line Options

```
usage: main.py [-h] [--url URL] [--rotate] [--urls URLS [URLS ...]]
               [--interval INTERVAL] [--width WIDTH] [--height HEIGHT]
               [--headless] [--no-kiosk] [--embedded] [--config CONFIG]
               [--example {1,2,3,4,5}]

Options:
  --url URL                 URL to load (default: from config)
  --rotate                  Enable URL rotation mode
  --urls URLS [URLS ...]    List of URLs for rotation
  --interval INTERVAL       Rotation interval in seconds (default: 30)
  --width WIDTH             Window width in pixels (default: 1920)
  --height HEIGHT           Window height in pixels (default: 1080)
  --headless                Run in headless mode
  --no-kiosk                Disable kiosk mode (show browser UI)
  --embedded                Embedded system mode (Raspberry Pi optimized)
  --config CONFIG           Path to .env config file
  --example {1,2,3,4,5}     Run example (1-5)
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

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

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `start_url` | str | `"https://www.google.com"` | Initial URL to load |
| `kiosk_mode` | bool | `True` | Enable full kiosk mode |
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

See `src/config.py` for complete list of options.

## Examples

### Example 1: Basic Kiosk Mode
```bash
uv run python src/main.py --example 1
```
Loads example.com in full kiosk mode.

### Example 2: URL Rotation
```bash
uv run python src/main.py --example 2
```
Rotates through multiple URLs every 10 seconds.

### Example 3: Dynamic Control
```bash
uv run python src/main.py --example 3
```
Demonstrates programmatic navigation and control.

### Example 4: Embedded System Mode
```bash
uv run python src/main.py --example 4
```
Optimized for Raspberry Pi with GPU disabled.

### Example 5: Error Handling
```bash
uv run python src/main.py --example 5
```
Demonstrates auto-recovery and error screens.

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
ExecStart=/home/pi/cardarena-remote-stage/.venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable kiosk-browser
sudo systemctl start kiosk-browser
```

## Troubleshooting

### Browser won't start
```bash
# Install system dependencies (Linux)
uv run playwright install-deps chromium
```

### Display issues on Linux
```bash
export DISPLAY=:0
```

### Memory issues on Raspberry Pi
Use `--embedded` flag or set in config:
```python
disable_gpu=True
disable_dev_shm=True
```

## License

See LICENSE file for details.