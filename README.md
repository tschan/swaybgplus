# SwayBG+ - Advanced Multi-Monitor Background Manager for Sway

SwayBG+ is a powerful, feature-rich background manager specifically designed for Sway window manager. It provides both GUI and CLI interfaces for managing backgrounds across multiple monitors with advanced positioning, scaling, and persistence features.

## 🌟 Features

### 🎨 **Advanced Background Management**
- **Multiple Background Modes**: Stretched, Fill, Fit, Center, Tile
- **Visual Image Positioning**: Drag and drop image positioning with real-time preview
- **Corner Resize Controls**: Visual resize handles for precise image scaling
- **Multi-Monitor Support**: Seamless background management across multiple displays
- **Real-Time Preview**: See exactly how your background will look before applying

### 🖥️ **Monitor Configuration**
- **Visual Monitor Layout**: Drag and drop monitor positioning
- **Inline Editing**: Double-click to edit resolution, position, and scale
- **Real Resolution Detection**: Automatically detects available resolutions for each monitor
- **Live Configuration**: Apply changes immediately or save to config file
- **🔄 Screen Orientation Support**: Full support for vertical monitors and rotated displays

### 📱 **Screen Orientation Features**
- **Transform Support**: Normal, 90°, 180°, 270° rotations plus flipped variants
- **Visual Indicators**: GUI shows effective resolution and orientation status
- **CLI Control**: Set orientations via command line with `--orientation` flag
- **Smart Background Handling**: Automatically adjusts backgrounds for rotated monitors
- **Portrait Monitor Support**: Perfect for vertical coding displays and reading monitors

### 💾 **Persistence & Startup**
- **Automatic Persistence**: Backgrounds survive reboots and sway restarts
- **Startup Integration**: Automatically adds restoration script to sway config
- **Configuration Backup**: Automatic backup of sway config before changes
- **Smart Detection**: Automatically detects and restores previous backgrounds

### 🎯 **User Interface**
- **Intuitive GUI**: Clean, modern interface with visual controls
- **Powerful CLI**: Full command-line interface for automation and scripting
- **Smart Workflows**: Simplified button layout eliminates confusion
- **Real-Time Feedback**: Live status updates and error handling

## 🚀 Quick Start

### Installation

#### 🔧 Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/swaybgplus.git
cd swaybgplus

# Install dependencies
pip install -r requirements.txt

# Install the package
python setup.py install

# Or install in development mode
pip install -e .
```

#### 📋 Dependencies

**Required:**
- Python 3.6+
- Sway window manager
- swaybg (background setter)
- python-pillow (image processing)

**For GUI (optional):**
- python-gobject
- gtk3

**Arch Linux:**
```bash
sudo pacman -S sway swaybg python python-pillow python-gobject gtk3
```

**Ubuntu/Debian:**
```bash
sudo apt install sway swaybg python3 python3-pil python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

**Fedora:**
```bash
sudo dnf install sway swaybg python3 python3-pillow python3-gobject gtk3-devel
```

### GUI Usage

```bash
# Launch the graphical interface
python3 swaybgplus_gui.py
```

**Workflow:**
1. **Load Image** → Click "📁 Load Image" to select your background
2. **Position & Scale** → Drag image to move, drag corners to resize
3. **Choose Mode** → Select background mode (Stretched, Fill, Fit, Center, Tile)
4. **Save Configuration** → Click "💾 Save" to save monitor configuration
5. **Reset if Needed** → Click "🔄 Reset" to reset image position and scale

### CLI Usage

```bash
# Set stretched background across all monitors
python3 swaybgplus_cli.py image.jpg --mode stretched

# Set fitted background with custom positioning
python3 swaybgplus_cli.py image.jpg --mode fill --offset-x 100 --offset-y 50 --scale 1.2

# Set vertical orientation for a monitor
python3 swaybgplus_cli.py --orientation DP-1:90

# Set background with rotated monitors
python3 swaybgplus_cli.py wallpaper.jpg --mode stretched --orientation DP-1:90

# Multiple monitor orientations
python3 swaybgplus_cli.py --orientation DP-1:90 --orientation HDMI-A-1:270

# Restore saved background configuration
python3 swaybgplus_cli.py --restore

# List current outputs (now shows transforms)
python3 swaybgplus_cli.py --list-outputs

# Clean up old background files
python3 swaybgplus_cli.py --cleanup
```

## 🔧 Background Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Stretched** | Single image stretched across all monitors | Panoramic wallpapers, unified desktop |
| **Fill** | Image scaled to fill each monitor (may crop) | Photos, maintaining aspect ratio |
| **Fit** | Image scaled to fit each monitor (may letterbox) | Logos, preserving full image |
| **Center** | Image centered on each monitor at original size | Icons, small graphics |
| **Tile** | Image repeated across each monitor | Patterns, textures |

## 🎮 Controls


## 🔍 Troubleshooting

### Common Issues

**Resolution dropdown is empty:**
- Ensure monitor is connected and active
- Check `swaymsg -t get_outputs` for available modes

**GUI won't start:**
- Install GTK dependencies: `sudo pacman -S python-gobject gtk3`
- Check Python version: requires Python 3.6+

### Debug Commands

```bash
# Check current outputs
swaymsg -t get_outputs

# List running swaybg processes
ps aux | grep swaybg

# Check saved configuration
cat ~/.config/sway/backgrounds/current_config.json

# Test CLI restore
python3 swaybgplus_cli.py --restore
```

## 🛠️ Dependencies

- **Python 3.6+**
- **Sway window manager**
- **swaybg** (background setter)
- **Python packages**:
  - `Pillow` (image processing)
  - `PyGObject` (GTK GUI)
- **System packages**:
  - `gtk3`
  - `python-gobject`

## 📝 License

This project is licensed under the Ancillary License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Bug Reports

.. coming soon ..
Please report bugs and feature requests through the GitHub issue tracker.

## 🔄 Screen Orientation

### Supported Transforms

| Transform | Description | Use Case |
|-----------|-------------|----------|
| `normal` | No rotation | Standard landscape monitors |
| `90` | 90° clockwise rotation | Portrait mode (vertical) |
| `180` | 180° rotation | Upside down |
| `270` | 270° clockwise rotation | Portrait mode (other direction) |
| `flipped` | Horizontal flip | Mirrored display |
| `flipped-90` | 90° rotation + horizontal flip | Portrait + mirrored |
| `flipped-180` | 180° rotation + horizontal flip | Upside down + mirrored |
| `flipped-270` | 270° rotation + horizontal flip | Portrait + mirrored (other way) |

### GUI Orientation Control

The GUI includes a new **Transform** column in the output configuration table:

1. **Double-click** the Transform column for any monitor
2. **Select** from dropdown: normal, 90, 180, 270, etc.
3. **Apply** changes to activate the new orientation
4. **Visual feedback** shows effective resolution and orientation indicator

### CLI Orientation Control

```bash
# Set a single monitor to portrait mode
swaybgplus_cli.py --orientation DP-1:90

# Set multiple monitor orientations
swaybgplus_cli.py --orientation DP-1:90 --orientation HDMI-A-1:180

# Combine with background setting
swaybgplus_cli.py wallpaper.jpg --mode stretched --orientation DP-1:90

# Orientation-only mode (no background change)
swaybgplus_cli.py --orientation DP-1:270
```

### How It Works

SwayBG+ intelligently handles screen orientations by:

1. **Calculating Effective Resolution**: For 90°/270° rotations, width and height are swapped
2. **Adjusting Background Layouts**: Background images are created using the effective dimensions
3. **Visual Preview**: The GUI shows monitors with their actual rotated dimensions
4. **Sway Integration**: Uses `swaymsg output` commands to apply transformations

### Example: Setting Up a Vertical Monitor

```bash
# Step 1: Set monitor to portrait orientation
swaybgplus_cli.py --orientation DP-2:90

# Step 2: Apply background that works with the new layout  
swaybgplus_cli.py wallpaper.jpg --mode stretched

# Alternative: Do both in one command
swaybgplus_cli.py wallpaper.jpg --mode stretched --orientation DP-2:90
```

---

**SwayBG+** - Making multi-monitor background management simple and powerful! 🎨✨ 
