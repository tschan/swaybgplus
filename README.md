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
chmod +x swaybgplus_gui.py swaybgplus_cli.py
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

## 🎛️ Interface Overview

### Main Window Layout

```
[File] [View]                                                    [✕]
────────────────────────────────────────────────────────────────────
💡 Drag image to move • Drag corners to resize • Ctrl+R to reset

┌─────────────────────────────────┬─────────────────────────────────┐
│ Monitor Layout & Preview        │ Output Configuration            │
│                                 │ ┌─────────────────────────────┐ │
│  ┌─────┐    ┌─────┐            │ │ Output │ Resolution │ Pos... │ │
│  │ DP-1│    │DP-2 │            │ │ DP-1   │ 2560x1440  │ 0,0    │ │
│  │     │    │     │            │ │ DP-2   │ 2560x1440  │ 2560,0 │ │
│  └─────┘    └─────┘            │ └─────────────────────────────┘ │
│                                 │                    [🔄 Refresh] │
│  [Background Preview Here]      │                                 │
│                                 │ Image Preview                   │
│                                 │ Image: filename.jpg             │
│                                 │ Size: 1920×1080                 │
│                                 │ ┌─────────────────────────────┐ │
│                                 │ │    [Image Thumbnail]        │ │
│                                 │ └─────────────────────────────┘ │
│                                 │        [Mode ▼] [📁 Load Image] │
└─────────────────────────────────┴─────────────────────────────────┘

Status: Ready...                                    [🔄 Reset] [💾 Save]
```

### Menu Structure

**File Menu:**
- Select Sway Config... *(choose config file)*
- Quit

**View Menu:**
- Show Config Path *(display current config file)*
- Show Backgrounds Directory *(show where backgrounds are stored)*

## 🔧 Background Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Stretched** | Single image stretched across all monitors | Panoramic wallpapers, unified desktop |
| **Fill** | Image scaled to fill each monitor (may crop) | Photos, maintaining aspect ratio |
| **Fit** | Image scaled to fit each monitor (may letterbox) | Logos, preserving full image |
| **Center** | Image centered on each monitor at original size | Icons, small graphics |
| **Tile** | Image repeated across each monitor | Patterns, textures |

## 🎮 Controls

### Visual Controls
- **Drag Image**: Click and drag to move image position
- **Resize Corners**: Drag white corner handles to scale image
- **Monitor Selection**: Click monitors to select and configure
- **Monitor Movement**: Drag selected monitors to reposition

### Keyboard Shortcuts
- **Ctrl+R**: Reset image position and scale to defaults

### Mouse Controls
- **Left Click**: Select monitor or start dragging
- **Drag**: Move image or monitor
- **Corner Drag**: Resize image proportionally

## 📁 File Structure

```
~/.config/sway/backgrounds/
├── current_config.json          # Current background configuration
├── restore_background.sh        # Startup restoration script
├── image_DP-1.png              # Processed background for monitor 1
├── image_DP-2.png              # Processed background for monitor 2
└── image_original.jpg          # Original image copy
```

## ⚙️ Configuration

### Automatic Startup
SwayBG+ automatically adds this line to your sway config:
```bash
exec ~/.config/sway/backgrounds/restore_background.sh
```

### Manual Configuration
You can also manually configure backgrounds:
```bash
# Apply specific background mode
swaybg -o DP-1 -i ~/.config/sway/backgrounds/image_DP-1.png -m stretch
```

## 🔍 Troubleshooting

### Common Issues

**Background doesn't persist after reboot:**
- Check if startup script was added to sway config
- Verify script permissions: `chmod +x ~/.config/sway/backgrounds/restore_background.sh`

**Resolution dropdown is empty:**
- Ensure monitor is connected and active
- Check `swaymsg -t get_outputs` for available modes

**Image positioning feels inverted:**
- This has been fixed in recent versions
- Try resetting position with Ctrl+R

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Bug Reports

Please report bugs and feature requests through the GitHub issue tracker.

---

**SwayBG+** - Making multi-monitor background management simple and powerful! 🎨✨ 