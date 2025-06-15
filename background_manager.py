#!/usr/bin/env python3
"""
Background manager for stretching images across multiple sway outputs
"""

import os
import subprocess
import tempfile
from PIL import Image, ImageOps
from typing import List, Tuple, Optional
from sway_config_parser import OutputConfig, SwayConfigParser


class BackgroundManager:
    """Manages background images for sway outputs"""
    
    def __init__(self):
        self.parser = SwayConfigParser()
        self.temp_files: List[str] = []
    
    def create_stretched_background(self, image_path: str, outputs: List[OutputConfig]) -> str:
        """Create a single stretched background image spanning all outputs"""
        if not outputs:
            raise ValueError("No outputs provided")
        
        # Load the source image
        try:
            source_image = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Could not load image: {e}")
        
        # Calculate total canvas size
        min_x = min(output.position[0] for output in outputs)
        min_y = min(output.position[1] for output in outputs)
        max_x = max(output.position[0] + output.resolution[0] for output in outputs)
        max_y = max(output.position[1] + output.resolution[1] for output in outputs)
        
        canvas_width = max_x - min_x
        canvas_height = max_y - min_y
        
        # Create a new canvas
        canvas = Image.new('RGB', (canvas_width, canvas_height), (0, 0, 0))
        
        # Resize source image to fit the entire canvas (stretched)
        resized_image = source_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        canvas.paste(resized_image, (0, 0))
        
        # Save to temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
        os.close(temp_fd)
        canvas.save(temp_path, 'PNG')
        self.temp_files.append(temp_path)
        
        return temp_path
    
    def create_individual_backgrounds(self, image_path: str, outputs: List[OutputConfig]) -> List[Tuple[str, str]]:
        """Create individual background images for each output"""
        if not outputs:
            raise ValueError("No outputs provided")
        
        # Load the source image
        try:
            source_image = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Could not load image: {e}")
        
        # Calculate total canvas size
        min_x = min(output.position[0] for output in outputs)
        min_y = min(output.position[1] for output in outputs)
        max_x = max(output.position[0] + output.resolution[0] for output in outputs)
        max_y = max(output.position[1] + output.resolution[1] for output in outputs)
        
        canvas_width = max_x - min_x
        canvas_height = max_y - min_y
        
        # Resize source image to fit the entire virtual canvas
        resized_image = source_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        # Create individual images for each output
        output_images = []
        
        for output in outputs:
            # Calculate crop area for this output
            crop_x = output.position[0] - min_x
            crop_y = output.position[1] - min_y
            crop_width = output.resolution[0]
            crop_height = output.resolution[1]
            
            # Crop the image for this output
            cropped_image = resized_image.crop((
                crop_x, crop_y,
                crop_x + crop_width, crop_y + crop_height
            ))
            
            # Save to temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix=f'_{output.name}.png')
            os.close(temp_fd)
            cropped_image.save(temp_path, 'PNG')
            self.temp_files.append(temp_path)
            
            output_images.append((output.name, temp_path))
        
        return output_images
    
    def set_background_stretched(self, image_path: str, outputs: List[OutputConfig] = None) -> bool:
        """Set a stretched background across all outputs"""
        if outputs is None:
            outputs = self.parser.get_current_outputs()
        
        if not outputs:
            print("No outputs available")
            return False
        
        try:
            # Create individual background images
            output_images = self.create_individual_backgrounds(image_path, outputs)
            
            # Set background for each output using swaybg
            for output_name, bg_image_path in output_images:
                self._set_output_background(output_name, bg_image_path)
            
            return True
            
        except Exception as e:
            print(f"Error setting background: {e}")
            return False
    
    def set_background_fitted(self, image_path: str, outputs: List[OutputConfig] = None, 
                            mode: str = "fill") -> bool:
        """Set a fitted background on each output individually"""
        if outputs is None:
            outputs = self.parser.get_current_outputs()
        
        if not outputs:
            print("No outputs available")
            return False
        
        try:
            # Set the same image on all outputs with the specified mode
            for output in outputs:
                self._set_output_background(output.name, image_path, mode)
            
            return True
            
        except Exception as e:
            print(f"Error setting background: {e}")
            return False
    
    def _set_output_background(self, output_name: str, image_path: str, mode: str = "stretch"):
        """Set background for a specific output using swaybg"""
        try:
            # Kill any existing swaybg processes for this output
            subprocess.run(['pkill', '-f', f'swaybg.*{output_name}'], 
                         capture_output=True, check=False)
            
            # Start new swaybg process
            cmd = ['swaybg', '-o', output_name, '-i', image_path, '-m', mode]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        except Exception as e:
            print(f"Error setting background for {output_name}: {e}")
    
    def kill_all_backgrounds(self):
        """Kill all swaybg processes"""
        try:
            subprocess.run(['pkill', 'swaybg'], capture_output=True, check=False)
        except Exception as e:
            print(f"Error killing swaybg processes: {e}")
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except Exception:
                pass
        self.temp_files.clear()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python background_manager.py <image_path> [mode]")
        print("Modes: stretched, fitted")
        sys.exit(1)
    
    image_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "stretched"
    
    manager = BackgroundManager()
    
    if mode == "stretched":
        success = manager.set_background_stretched(image_path)
    else:
        success = manager.set_background_fitted(image_path)
    
    if success:
        print(f"Background set successfully in {mode} mode")
    else:
        print("Failed to set background") 