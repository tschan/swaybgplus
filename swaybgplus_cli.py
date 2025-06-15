#!/usr/bin/env python3
"""
SwayBG+ CLI - Command line interface for managing sway backgrounds
"""

import argparse
import sys
import os
from typing import List

from sway_config_parser import SwayConfigParser, OutputConfig
from background_manager import BackgroundManager


def main():
    parser = argparse.ArgumentParser(
        description="SwayBG+ - Multi-monitor background manager for sway",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set stretched background across all monitors
  swaybgplus_cli.py image.jpg --mode stretched
  
  # Set fitted background on each monitor
  swaybgplus_cli.py image.jpg --mode fill
  
  # Restore saved background configuration
  swaybgplus_cli.py --restore
  
  # List current outputs
  swaybgplus_cli.py --list-outputs
        """
    )
    
    parser.add_argument('image', nargs='?', help='Path to background image')
    parser.add_argument('--mode', '-m', 
                       choices=['stretched', 'fill', 'fit', 'center', 'tile'],
                       default='stretched',
                       help='Background mode (default: stretched)')
    parser.add_argument('--restore', '-r', action='store_true',
                       help='Restore saved background configuration')
    parser.add_argument('--list-outputs', '-l', action='store_true',
                       help='List current outputs')
    parser.add_argument('--config', '-c', 
                       help='Path to sway config file')
    parser.add_argument('--offset-x', type=int, default=0,
                       help='Horizontal image offset (default: 0)')
    parser.add_argument('--offset-y', type=int, default=0,
                       help='Vertical image offset (default: 0)')
    parser.add_argument('--scale', type=float, default=1.0,
                       help='Image scale factor (default: 1.0)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up old background files')
    
    args = parser.parse_args()
    
    # Initialize managers
    config_parser = SwayConfigParser()
    background_manager = BackgroundManager()
    
    # Set custom config path if provided
    if args.config:
        config_parser.set_config_path(args.config)
    
    # Handle restore command
    if args.restore:
        print("Restoring saved background configuration...")
        success = background_manager.restore_background()
        if success:
            print("Background restored successfully")
        else:
            print("Failed to restore background")
            sys.exit(1)
        return
    
    # Handle cleanup command
    if args.cleanup:
        print("Cleaning up old background files...")
        background_manager.cleanup()
        print("Cleanup completed")
        return
    
    # Handle list outputs command
    if args.list_outputs:
        outputs = config_parser.get_current_outputs()
        if not outputs:
            print("No outputs found")
            return
        
        print(f"Found {len(outputs)} outputs:")
        for output in outputs:
            status = "enabled" if output.enabled else "disabled"
            print(f"  {output.name}: {output.resolution[0]}x{output.resolution[1]} "
                  f"at ({output.position[0]}, {output.position[1]}) "
                  f"scale {output.scale} [{status}]")
        return
    
    # Require image path for background setting
    if not args.image:
        parser.error("Image path is required unless using --restore, --list-outputs, or --cleanup")
    
    # Check if image exists
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}")
        sys.exit(1)
    
    # Get current outputs
    outputs = config_parser.get_current_outputs()
    if not outputs:
        print("Error: No outputs found")
        sys.exit(1)
    
    print(f"Setting background: {args.image}")
    print(f"Mode: {args.mode}")
    print(f"Outputs: {', '.join(output.name for output in outputs)}")
    
    if args.offset_x != 0 or args.offset_y != 0:
        print(f"Image offset: ({args.offset_x}, {args.offset_y})")
    
    if args.scale != 1.0:
        print(f"Image scale: {args.scale}")
    
    # Apply background
    image_offset = (args.offset_x, args.offset_y)
    
    if args.mode == 'stretched':
        success = background_manager.set_background_stretched(
            args.image, outputs, image_offset, args.scale
        )
    else:
        success = background_manager.set_background_fitted(
            args.image, outputs, args.mode, image_offset, args.scale
        )
    
    if success:
        print("Background applied successfully")
        print(f"Configuration saved to: {background_manager.config_dir}")
    else:
        print("Failed to apply background")
        sys.exit(1)


if __name__ == "__main__":
    main() 