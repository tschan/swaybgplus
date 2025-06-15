#!/usr/bin/env python3
"""
SwayBG+ CLI - Command-line interface for managing sway backgrounds
"""

import argparse
import sys
import os
from sway_config_parser import SwayConfigParser
from background_manager import BackgroundManager


def main():
    parser = argparse.ArgumentParser(
        description="SwayBG+ - Multi-monitor background manager for sway",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s stretch /path/to/image.jpg
  %(prog)s fit /path/to/image.jpg --mode fill
  %(prog)s list-outputs
  %(prog)s kill-backgrounds
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stretch command
    stretch_parser = subparsers.add_parser(
        'stretch', 
        help='Stretch image across all monitors'
    )
    stretch_parser.add_argument('image', help='Path to image file')
    
    # Fit command
    fit_parser = subparsers.add_parser(
        'fit', 
        help='Fit image on each monitor individually'
    )
    fit_parser.add_argument('image', help='Path to image file')
    fit_parser.add_argument(
        '--mode', 
        choices=['stretch', 'fill', 'fit', 'center', 'tile'],
        default='fill',
        help='Background mode (default: fill)'
    )
    
    # List outputs command
    list_parser = subparsers.add_parser(
        'list-outputs', 
        help='List current sway outputs'
    )
    
    # Kill backgrounds command
    kill_parser = subparsers.add_parser(
        'kill-backgrounds', 
        help='Kill all running swaybg processes'
    )
    
    # GUI command
    gui_parser = subparsers.add_parser(
        'gui', 
        help='Launch graphical interface'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize components
    config_parser = SwayConfigParser()
    background_manager = BackgroundManager()
    
    try:
        if args.command == 'stretch':
            if not os.path.exists(args.image):
                print(f"Error: Image file '{args.image}' not found", file=sys.stderr)
                return 1
            
            outputs = config_parser.get_current_outputs()
            if not outputs:
                print("Error: No active outputs found", file=sys.stderr)
                return 1
            
            print(f"Stretching '{args.image}' across {len(outputs)} outputs...")
            success = background_manager.set_background_stretched(args.image, outputs)
            
            if success:
                print("Background set successfully!")
                return 0
            else:
                print("Failed to set background", file=sys.stderr)
                return 1
        
        elif args.command == 'fit':
            if not os.path.exists(args.image):
                print(f"Error: Image file '{args.image}' not found", file=sys.stderr)
                return 1
            
            outputs = config_parser.get_current_outputs()
            if not outputs:
                print("Error: No active outputs found", file=sys.stderr)
                return 1
            
            print(f"Setting '{args.image}' on {len(outputs)} outputs (mode: {args.mode})...")
            success = background_manager.set_background_fitted(args.image, outputs, args.mode)
            
            if success:
                print("Background set successfully!")
                return 0
            else:
                print("Failed to set background", file=sys.stderr)
                return 1
        
        elif args.command == 'list-outputs':
            outputs = config_parser.get_current_outputs()
            
            if not outputs:
                print("No active outputs found")
                return 0
            
            print(f"Found {len(outputs)} active outputs:")
            print()
            
            for output in outputs:
                print(f"Name: {output.name}")
                print(f"  Resolution: {output.resolution[0]}x{output.resolution[1]}")
                print(f"  Position: {output.position[0]}, {output.position[1]}")
                print(f"  Scale: {output.scale}")
                print(f"  Transform: {output.transform}")
                print()
            
            # Show total virtual screen size
            total_width, total_height = config_parser.get_total_resolution()
            print(f"Total virtual screen: {total_width}x{total_height}")
            
            return 0
        
        elif args.command == 'kill-backgrounds':
            print("Killing all swaybg processes...")
            background_manager.kill_all_backgrounds()
            print("Done!")
            return 0
        
        elif args.command == 'gui':
            try:
                from swaybgplus_gui import SwayBGPlusGUI
                print("Launching GUI...")
                app = SwayBGPlusGUI()
                app.run()
                return 0
            except ImportError as e:
                print(f"Error: GUI dependencies not available: {e}", file=sys.stderr)
                print("Please install GTK+ dependencies: sudo pacman -S python-gobject gtk3", file=sys.stderr)
                return 1
        
        else:
            parser.print_help()
            return 1
    
    finally:
        background_manager.cleanup()


if __name__ == "__main__":
    sys.exit(main()) 