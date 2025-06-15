#!/usr/bin/env python3
"""
Setup script for SwayBG+ installation
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are available"""
    print("Checking dependencies...")
    
    # Check for swaybg
    if not shutil.which('swaybg'):
        print("❌ swaybg not found")
        print("Please install swaybg:")
        print("  Arch Linux: sudo pacman -S swaybg")
        print("  Ubuntu/Debian: sudo apt install swaybg")
        print("  Fedora: sudo dnf install swaybg")
        return False
    else:
        print("✅ swaybg found")
    
    # Check for swaymsg
    if not shutil.which('swaymsg'):
        print("❌ swaymsg not found")
        print("Please install sway window manager")
        return False
    else:
        print("✅ swaymsg found")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} found")
    
    # Check for PIL
    try:
        import PIL
        print("✅ Pillow (PIL) found")
    except ImportError:
        print("❌ Pillow (PIL) not found")
        print("Install with: pip install Pillow")
        return False
    
    # Check for GTK (optional)
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        print("✅ GTK+ dependencies found (GUI available)")
        return True
    except (ImportError, ValueError):
        print("⚠️  GTK+ dependencies not found (GUI not available)")
        print("For GUI support, install:")
        print("  Arch Linux: sudo pacman -S python-gobject gtk3")
        print("  Ubuntu/Debian: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0")
        print("  Fedora: sudo dnf install python3-gobject gtk3-devel")
        return "cli-only"


def make_executable():
    """Make Python scripts executable"""
    scripts = [
        'swaybgplus_cli.py',
        'swaybgplus_gui.py',
        'sway_config_parser.py',
        'background_manager.py'
    ]
    
    for script in scripts:
        if os.path.exists(script):
            os.chmod(script, 0o755)
            print(f"✅ Made {script} executable")


def create_desktop_entry():
    """Create a desktop entry for the GUI application"""
    desktop_dir = Path.home() / '.local/share/applications'
    desktop_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = desktop_dir / 'swaybgplus.desktop'
    current_dir = Path.cwd()
    
    desktop_content = f"""[Desktop Entry]
Name=SwayBG+
Comment=Multi-monitor background manager for Sway
Exec=python3 {current_dir}/swaybgplus_gui.py
Icon=preferences-desktop-wallpaper
Terminal=false
Type=Application
Categories=Settings;DesktopSettings;
Keywords=wallpaper;background;sway;monitor;
"""
    
    with open(desktop_file, 'w') as f:
        f.write(desktop_content)
    
    print(f"✅ Created desktop entry: {desktop_file}")


def create_symlinks():
    """Create symbolic links in ~/.local/bin"""
    bin_dir = Path.home() / '.local/bin'
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    current_dir = Path.cwd()
    
    # Create symlinks
    symlinks = [
        ('swaybgplus_cli.py', 'swaybgplus'),
        ('swaybgplus_gui.py', 'swaybgplus-gui'),
    ]
    
    for source, target in symlinks:
        source_path = current_dir / source
        target_path = bin_dir / target
        
        if target_path.exists():
            target_path.unlink()
        
        try:
            target_path.symlink_to(source_path)
            print(f"✅ Created symlink: {target_path} -> {source_path}")
        except OSError as e:
            print(f"❌ Failed to create symlink {target}: {e}")
    
    # Check if ~/.local/bin is in PATH
    local_bin = str(bin_dir)
    if local_bin not in os.environ.get('PATH', ''):
        print(f"⚠️  {local_bin} is not in your PATH")
        print("Add this to your shell profile (.bashrc, .zshrc, etc.):")
        print(f"export PATH=\"$PATH:{local_bin}\"")


def test_installation():
    """Test if the installation works"""
    print("\nTesting installation...")
    
    try:
        # Test CLI
        result = subprocess.run([
            sys.executable, 'swaybgplus_cli.py', 'list-outputs'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI interface works")
        else:
            print("❌ CLI interface failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False
    
    return True


def main():
    """Main setup function"""
    print("SwayBG+ Setup")
    print("=" * 50)
    
    # Check dependencies
    deps_result = check_dependencies()
    if deps_result is False:
        print("\n❌ Missing required dependencies. Please install them first.")
        return 1
    
    print("\n" + "=" * 50)
    print("Setting up SwayBG+...")
    
    # Make scripts executable
    make_executable()
    
    # Create symlinks
    create_symlinks()
    
    # Create desktop entry if GUI is available
    if deps_result is True:
        create_desktop_entry()
    
    # Test installation
    if test_installation():
        print("\n" + "=" * 50)
        print("✅ SwayBG+ setup completed successfully!")
        print("\nUsage:")
        print("  Command line: swaybgplus stretch /path/to/image.jpg")
        print("  Command line: python3 swaybgplus_cli.py --help")
        if deps_result is True:
            print("  GUI: swaybgplus-gui")
            print("  GUI: python3 swaybgplus_gui.py")
        print("\nSee README.md for more information.")
        return 0
    else:
        print("\n❌ Setup completed with errors. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 