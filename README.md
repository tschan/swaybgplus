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

```bash
# Clone the repository
git clone https://github.com/yourusername/swaybgplus.git
cd swaybgplus

# Install dependencies
pip install -r requirements.txt

# Make executable
python setup.py
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

# Restore saved background configuration
python3 swaybgplus_cli.py --restore

# List current outputs
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

---

**SwayBG+** - Making multi-monitor background management simple and powerful! 🎨✨ 
