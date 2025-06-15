# SwayBG+ - Multi-Monitor Background Manager for Sway

SwayBG+ is a powerful utility for managing wallpapers across multiple monitors in the Sway window manager. It provides both command-line and graphical interfaces for stretching images across all monitors or fitting them individually.

## Features

- **Stretch Mode**: Stretch a single image across all monitors seamlessly
- **Fit Mode**: Set the same image on each monitor individually with various scaling modes
- **GUI Interface**: Visual monitor layout editor with drag-and-drop positioning
- **CLI Interface**: Command-line tools for scripting and automation
- **Live Preview**: See your monitor layout and make adjustments before applying
- **Multiple Image Formats**: Support for JPEG, PNG, GIF, BMP, and TIFF images
- **Sway Integration**: Works directly with sway's output configuration

## Installation

### Prerequisites

- Sway window manager
- `swaybg` (usually included with sway)
- Python 3.7+
- Python packages: `Pillow`, `PyGObject` (for GUI)

### Install Dependencies

On Arch Linux:
```bash
sudo pacman -S python-pillow python-gobject gtk3 swaybg
```

On Ubuntu/Debian:
```bash
sudo apt install python3-pil python3-gi python3-gi-cairo gir1.2-gtk-3.0 swaybg
```

On Fedora:
```bash
sudo dnf install python3-pillow python3-gobject gtk3-devel swaybg
```

### Install SwayBG+

1. Clone or download this repository:
```bash
git clone <repository-url> swaybgplus
cd swaybgplus
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Make scripts executable:
```bash
chmod +x swaybgplus_cli.py swaybgplus_gui.py
```

## Usage

### GUI Interface

Launch the graphical interface:
```bash
python3 swaybgplus_gui.py
# or
python3 swaybgplus_cli.py gui
```

The GUI provides:
- Visual monitor layout with drag-and-drop positioning
- Image file browser and loader
- Real-time preview of monitor arrangements
- Apply buttons for different background modes
- Monitor information panel

### Command-Line Interface

#### Basic Commands

List current outputs:
```bash
python3 swaybgplus_cli.py list-outputs
```

Stretch an image across all monitors:
```bash
python3 swaybgplus_cli.py stretch /path/to/image.jpg
```

Fit an image on each monitor:
```bash
python3 swaybgplus_cli.py fit /path/to/image.jpg --mode fill
```

Kill all background processes:
```bash
python3 swaybgplus_cli.py kill-backgrounds
```

#### Background Modes

- `stretch`: Stretch image to fit exact dimensions (may distort)
- `fill`: Scale image to fill screen, cropping if necessary (default)
- `fit`: Scale image to fit within screen, may leave black bars
- `center`: Center image without scaling
- `tile`: Repeat image to fill screen

### Examples

Set a stretched background across three monitors:
```bash
python3 swaybgplus_cli.py stretch ~/Pictures/landscape.jpg
```

Set individual wallpapers with fill mode:
```bash
python3 swaybgplus_cli.py fit ~/Pictures/wallpaper.png --mode fill
```

Check your current monitor setup:
```bash
python3 swaybgplus_cli.py list-outputs
```

## How It Works

### Image Processing

1. **Stretch Mode**: Creates a large canvas spanning all monitors, stretches the source image to fit, then crops individual sections for each monitor
2. **Fit Mode**: Applies the same image to each monitor using swaybg's built-in scaling modes

### Sway Integration

- Uses `swaymsg -t get_outputs` to detect current monitor configuration
- Leverages `swaybg` for actually setting backgrounds
- Supports all sway output features (scaling, rotation, positioning)

### Monitor Detection

The tool automatically detects:
- Monitor names and positions
- Screen resolutions and scaling factors
- Active vs inactive monitors
- Multi-monitor layouts (side-by-side, stacked, mixed)

## Configuration

### Sway Config Integration

You can integrate SwayBG+ into your sway config for automatic startup:

```bash
# ~/.config/sway/config
exec python3 /path/to/swaybgplus_cli.py stretch ~/Pictures/wallpaper.jpg
```

### Custom Monitor Layouts

The GUI allows you to:
- Drag monitors to reposition them
- View current positioning and resolution
- Test different layouts before applying backgrounds

## Troubleshooting

### Common Issues

**"No outputs available"**
- Make sure you're running this inside a sway session
- Check that `swaymsg -t get_outputs` returns active outputs

**"swaybg not found"**
- Install swaybg: `sudo pacman -S swaybg` (Arch) or equivalent
- Make sure swaybg is in your PATH

**GUI won't start**
- Install GTK+ dependencies: `sudo pacman -S python-gobject gtk3`
- Try running from a terminal to see error messages

**Images appear distorted**
- Use "fit" mode instead of "stretch" to maintain aspect ratio
- Try different scaling modes (fill, fit, center)

### Debug Output

Run with verbose output to troubleshoot:
```bash
python3 swaybgplus_cli.py list-outputs  # Check detected monitors
python3 swaybgplus_cli.py kill-backgrounds  # Clear existing backgrounds
```

## Technical Details

### File Structure

- `sway_config_parser.py`: Sway configuration and output detection
- `background_manager.py`: Image processing and swaybg integration  
- `swaybgplus_gui.py`: GTK-based graphical interface
- `swaybgplus_cli.py`: Command-line interface
- `requirements.txt`: Python dependencies

### Dependencies

- **Pillow (PIL)**: Image processing and manipulation
- **PyGObject**: GTK+ bindings for GUI (optional)
- **swaybg**: Sway's background setter (required)

### Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png) 
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## Contributing

Contributions are welcome! Please feel free to:
- Report bugs or request features via issues
- Submit pull requests with improvements
- Share your custom monitor configurations
- Help with documentation and testing

## License

This project is open source. Please check the license file for details.

## Alternatives

Other background managers for sway:
- `swaybg` (basic, included with sway)
- `azote` (GUI wallpaper manager)
- `feh` (works with X11/XWayland)

SwayBG+ focuses specifically on multi-monitor stretched backgrounds, which most other tools don't handle well. 