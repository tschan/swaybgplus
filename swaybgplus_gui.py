#!/usr/bin/env python3
"""
SwayBG+ GUI - A graphical interface for managing sway backgrounds across multiple monitors
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')

from gi.repository import Gtk, GdkPixbuf, Gdk, GLib, Gio, GObject
import os
import sys
import threading
from typing import List, Optional
from PIL import Image
import cairo

from sway_config_parser import SwayConfigParser, OutputConfig
from background_manager import BackgroundManager


class MonitorWidget(Gtk.DrawingArea):
    """Widget to display and arrange monitors"""
    
    __gsignals__ = {
        'output-selected': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        'output-changed': (GObject.SIGNAL_RUN_FIRST, None, (object,))
    }
    
    def __init__(self, outputs: List[OutputConfig]):
        super().__init__()
        self.outputs = outputs
        self.scale_factor = 0.1  # Scale down monitors for display
        self.selected_output = None
        self.dragging = False
        self.drag_start = (0, 0)
        self.preview_image = None  # Preview image to show on monitors
        
        self.set_size_request(800, 600)
        self.set_can_focus(True)
        
        # Connect drawing and mouse events
        self.connect('draw', self.on_draw)
        self.connect('button-press-event', self.on_button_press)
        self.connect('button-release-event', self.on_button_release)
        self.connect('motion-notify-event', self.on_motion)
        
        # Enable mouse events
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | 
                       Gdk.EventMask.BUTTON_RELEASE_MASK |
                       Gdk.EventMask.POINTER_MOTION_MASK)
        
        self.update_scale()
    
    def set_preview_image(self, image_path: str):
        """Set preview image to display on monitors"""
        try:
            self.preview_image = Image.open(image_path)
            self.queue_draw()
        except Exception as e:
            print(f"Error loading preview image: {e}")
            self.preview_image = None
    
    def clear_preview(self):
        """Clear preview image"""
        self.preview_image = None
        self.queue_draw()
    
    def update_scale(self):
        """Update scale factor based on monitor layout"""
        if not self.outputs:
            return
        
        # Find total bounds
        min_x = min(output.position[0] for output in self.outputs)
        min_y = min(output.position[1] for output in self.outputs)
        max_x = max(output.position[0] + output.resolution[0] for output in self.outputs)
        max_y = max(output.position[1] + output.resolution[1] for output in self.outputs)
        
        total_width = max_x - min_x
        total_height = max_y - min_y
        
        # Calculate scale to fit in widget
        widget_width = 750
        widget_height = 550
        
        scale_x = widget_width / total_width if total_width > 0 else 0.1
        scale_y = widget_height / total_height if total_height > 0 else 0.1
        
        self.scale_factor = min(scale_x, scale_y, 0.3)  # Cap at 0.3 for readability
    
    def on_draw(self, widget, cr):
        """Draw the monitors"""
        if not self.outputs:
            return False
        
        # Clear background
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.paint()
        
        # Find offset to center the layout
        min_x = min(output.position[0] for output in self.outputs)
        min_y = min(output.position[1] for output in self.outputs)
        
        widget_width = widget.get_allocated_width()
        widget_height = widget.get_allocated_height()
        
        offset_x = (widget_width - (max(output.position[0] + output.resolution[0] for output in self.outputs) - min_x) * self.scale_factor) / 2
        offset_y = (widget_height - (max(output.position[1] + output.resolution[1] for output in self.outputs) - min_y) * self.scale_factor) / 2
        
        # Prepare preview image if available
        preview_surface = None
        if self.preview_image:
            # Create a stretched version of the preview across all monitors
            total_width = max(output.position[0] + output.resolution[0] for output in self.outputs) - min_x
            total_height = max(output.position[1] + output.resolution[1] for output in self.outputs) - min_y
            
            # Resize preview image to virtual screen size
            preview_resized = self.preview_image.resize((total_width, total_height), Image.Resampling.LANCZOS)
            
            # Convert to Cairo surface
            preview_data = preview_resized.tobytes('raw', 'RGB')
            preview_surface = cairo.ImageSurface.create_for_data(
                preview_data, cairo.FORMAT_RGB24, total_width, total_height
            )
        
        # Draw each monitor
        for output in self.outputs:
            x = (output.position[0] - min_x) * self.scale_factor + offset_x
            y = (output.position[1] - min_y) * self.scale_factor + offset_y
            width = output.resolution[0] * self.scale_factor
            height = output.resolution[1] * self.scale_factor
            
            # Draw monitor background color first
            if output == self.selected_output:
                cr.set_source_rgb(0.3, 0.6, 1.0)  # Blue for selected
            else:
                cr.set_source_rgb(0.6, 0.6, 0.6)  # Gray for normal
            
            # Draw monitor rectangle background
            cr.rectangle(x, y, width, height)
            cr.fill()
            
            # Draw preview image if available (overlay on top of background)
            if preview_surface:
                cr.save()
                cr.rectangle(x, y, width, height)
                cr.clip()
                
                # Scale and position the preview
                preview_x = (output.position[0] - min_x) * self.scale_factor
                preview_y = (output.position[1] - min_y) * self.scale_factor
                
                cr.scale(self.scale_factor, self.scale_factor)
                cr.set_source_surface(preview_surface, preview_x / self.scale_factor - (output.position[0] - min_x), 
                                    preview_y / self.scale_factor - (output.position[1] - min_y))
                cr.paint_with_alpha(0.8)  # Make preview semi-transparent so we can see selection
                cr.restore()
            
            # Always draw border (on top of everything)
            if output == self.selected_output:
                cr.set_source_rgb(1.0, 1.0, 0.0)  # Yellow border for selected
                cr.set_line_width(3)
            else:
                cr.set_source_rgb(0.8, 0.8, 0.8)  # Light gray border for normal
                cr.set_line_width(2)
            
            cr.rectangle(x, y, width, height)
            cr.stroke()
            
            # Always draw monitor name and resolution (on top of everything)
            cr.set_source_rgb(1, 1, 1)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(12)
            
            text = f"{output.name}\n{output.resolution[0]}x{output.resolution[1]}"
            text_lines = text.split('\n')
            
            # Calculate text positioning
            text_extents = cr.text_extents(text_lines[0])
            text_width = max(cr.text_extents(line).width for line in text_lines)
            text_height = len(text_lines) * 15
            
            text_x = x + (width - text_width) / 2
            text_y = y + (height - text_height) / 2 + 12  # +12 for baseline offset
            
            # Draw text background for better readability (semi-transparent black)
            cr.set_source_rgba(0, 0, 0, 0.8)
            cr.rectangle(text_x - 8, text_y - 15, text_width + 16, text_height + 8)
            cr.fill()
            
            # Draw text (white on dark background)
            cr.set_source_rgb(1, 1, 1)
            for i, line in enumerate(text_lines):
                line_extents = cr.text_extents(line)
                line_x = x + (width - line_extents.width) / 2
                cr.move_to(line_x, text_y + i * 15)
                cr.show_text(line)
        
        return True
    
    def on_button_press(self, widget, event):
        """Handle mouse button press"""
        if event.button == 1:  # Left click
            clicked_output = self.get_output_at_position(event.x, event.y)
            if clicked_output:
                self.selected_output = clicked_output
                self.dragging = True
                self.drag_start = (event.x, event.y)
                self.queue_draw()
                # Emit signal for output selection
                self.emit('output-selected', clicked_output)
                return True
        return False
    
    def on_button_release(self, widget, event):
        """Handle mouse button release"""
        if event.button == 1:
            self.dragging = False
        return False
    
    def on_motion(self, widget, event):
        """Handle mouse motion"""
        if self.dragging and self.selected_output:
            dx = (event.x - self.drag_start[0]) / self.scale_factor
            dy = (event.y - self.drag_start[1]) / self.scale_factor
            
            # Update output position
            new_x = int(self.selected_output.position[0] + dx)
            new_y = int(self.selected_output.position[1] + dy)
            
            # Snap to grid (optional)
            new_x = (new_x // 10) * 10
            new_y = (new_y // 10) * 10
            
            self.selected_output.position = (new_x, new_y)
            
            self.drag_start = (event.x, event.y)
            self.queue_draw()
            
            # Emit signal for position change
            self.emit('output-changed', self.selected_output)
            
            return True
        return False
    
    def get_output_at_position(self, x, y) -> Optional[OutputConfig]:
        """Get output at the given screen position"""
        if not self.outputs:
            return None
        
        min_x = min(output.position[0] for output in self.outputs)
        min_y = min(output.position[1] for output in self.outputs)
        
        widget_width = self.get_allocated_width()
        widget_height = self.get_allocated_height()
        
        offset_x = (widget_width - (max(output.position[0] + output.resolution[0] for output in self.outputs) - min_x) * self.scale_factor) / 2
        offset_y = (widget_height - (max(output.position[1] + output.resolution[1] for output in self.outputs) - min_y) * self.scale_factor) / 2
        
        for output in self.outputs:
            output_x = (output.position[0] - min_x) * self.scale_factor + offset_x
            output_y = (output.position[1] - min_y) * self.scale_factor + offset_y
            output_width = output.resolution[0] * self.scale_factor
            output_height = output.resolution[1] * self.scale_factor
            
            if (output_x <= x <= output_x + output_width and 
                output_y <= y <= output_y + output_height):
                return output
        
        return None


class SwayBGPlusGUI:
    """Main GUI application"""
    
    def __init__(self):
        self.parser = SwayConfigParser()
        self.background_manager = BackgroundManager()
        self.outputs: List[OutputConfig] = []
        self.current_image_path: Optional[str] = None
        self.current_mode: str = "stretched"  # Current background mode
        self.selected_output: Optional[OutputConfig] = None
        
        self.build_ui()
        self.refresh_outputs()
    
    def build_ui(self):
        """Build the user interface"""
        # Main window
        self.window = Gtk.Window()
        self.window.set_title("SwayBG+ - Multi-Monitor Background Manager")
        self.window.set_default_size(1400, 900)
        self.window.connect('destroy', self.on_quit)
        self.window.connect('delete-event', self.on_quit)  # Handle X button
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.window.add(main_box)
        
        # Menu bar
        main_box.pack_start(self.menubar, False, False, 0)
        
        # Content area
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        content_box.set_margin_left(12)
        content_box.set_margin_right(12)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)
        main_box.pack_start(content_box, True, True, 0)
        
        # Header bar with buttons
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        content_box.pack_start(header_box, False, False, 0)
        
        # Refresh button
        refresh_btn = Gtk.Button.new_with_label("🔄 Refresh Outputs")
        refresh_btn.connect('clicked', self.on_refresh_outputs)
        header_box.pack_start(refresh_btn, False, False, 0)
        
        # Load image button
        load_image_btn = Gtk.Button.new_with_label("📁 Load Image")
        load_image_btn.connect('clicked', self.on_load_image)
        header_box.pack_start(load_image_btn, False, False, 0)
        
        # Mode selection
        mode_label = Gtk.Label()
        mode_label.set_text("Mode:")
        header_box.pack_start(mode_label, False, False, 0)
        
        self.mode_combo = Gtk.ComboBoxText()
        self.mode_combo.append_text("Stretched")
        self.mode_combo.append_text("Fill")
        self.mode_combo.append_text("Fit")
        self.mode_combo.append_text("Center")
        self.mode_combo.append_text("Tile")
        self.mode_combo.set_active(0)  # Default to stretched
        self.mode_combo.connect('changed', self.on_mode_changed)
        header_box.pack_start(self.mode_combo, False, False, 0)
        
        # Save button (main action button)
        self.save_btn = Gtk.Button.new_with_label("💾 Save Background")
        self.save_btn.connect('clicked', self.on_save_background)
        self.save_btn.set_sensitive(False)  # Disabled until image is loaded
        self.save_btn.get_style_context().add_class("suggested-action")
        header_box.pack_start(self.save_btn, False, False, 0)
        
        # Current image label
        self.image_label = Gtk.Label()
        self.image_label.set_text("No image selected")
        self.image_label.set_halign(Gtk.Align.END)
        header_box.pack_end(self.image_label, True, True, 0)
        
        # Main content area - horizontal paned
        main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        content_box.pack_start(main_paned, True, True, 0)
        
        # Left panel - monitor layout
        left_frame = Gtk.Frame()
        left_frame.set_label("Monitor Layout & Preview")
        left_frame.set_size_request(500, -1)
        main_paned.pack1(left_frame, True, False)
        
        self.monitor_widget = MonitorWidget([])
        self.monitor_widget.connect('output-selected', self.on_output_selected)
        self.monitor_widget.connect('output-changed', self.on_output_changed)
        left_frame.add(self.monitor_widget)
        
        # Right panel - vertical paned for output info and image preview
        right_paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        right_paned.set_size_request(500, -1)
        main_paned.pack2(right_paned, False, False)
        
        # Top right - output configuration with inline editing
        output_frame = Gtk.Frame()
        output_frame.set_label("Output Configuration")
        right_paned.pack1(output_frame, True, False)
        
        # Create output list with inline editing
        self.create_output_list(output_frame)
        
        # Bottom right - image preview
        preview_frame = Gtk.Frame()
        preview_frame.set_label("Image Preview")
        right_paned.pack2(preview_frame, True, False)
        
        preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        preview_box.set_margin_left(12)
        preview_box.set_margin_right(12)
        preview_box.set_margin_top(12)
        preview_box.set_margin_bottom(12)
        preview_frame.add(preview_box)
        
        # Image preview widget
        self.preview_image = Gtk.Image()
        self.preview_image.set_size_request(300, 200)
        
        preview_scrolled = Gtk.ScrolledWindow()
        preview_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        preview_scrolled.add(self.preview_image)
        preview_box.pack_start(preview_scrolled, True, True, 0)
        
        # Image info label
        self.image_info_label = Gtk.Label()
        self.image_info_label.set_text("No image loaded")
        self.image_info_label.set_halign(Gtk.Align.START)
        preview_box.pack_start(self.image_info_label, False, False, 0)
        
        # Status bar
        self.status_bar = Gtk.Statusbar()
        content_box.pack_end(self.status_bar, False, False, 0)
        
        self.window.show_all()
    
    def create_menu_bar(self):
        """Create the menu bar"""
        self.menubar = Gtk.MenuBar()
        
        # File menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem.new_with_label("File")
        file_item.set_submenu(file_menu)
        self.menubar.append(file_item)
        
        # Select config file
        config_item = Gtk.MenuItem.new_with_label("Select Sway Config...")
        config_item.connect('activate', self.on_select_config)
        file_menu.append(config_item)
        
        file_menu.append(Gtk.SeparatorMenuItem())
        
        # Save config
        save_config_item = Gtk.MenuItem.new_with_label("Save Monitor Config")
        save_config_item.connect('activate', self.on_save_config)
        file_menu.append(save_config_item)
        
        # Apply config
        apply_config_item = Gtk.MenuItem.new_with_label("Apply Monitor Config")
        apply_config_item.connect('activate', self.on_apply_config)
        file_menu.append(apply_config_item)
        
        file_menu.append(Gtk.SeparatorMenuItem())
        
        # Quit
        quit_item = Gtk.MenuItem.new_with_label("Quit")
        quit_item.connect('activate', self.on_quit)
        file_menu.append(quit_item)
        
        # View menu
        view_menu = Gtk.Menu()
        view_item = Gtk.MenuItem.new_with_label("View")
        view_item.set_submenu(view_menu)
        self.menubar.append(view_item)
        
        # Show config path
        show_config_item = Gtk.MenuItem.new_with_label("Show Config Path")
        show_config_item.connect('activate', self.on_show_config_path)
        view_menu.append(show_config_item)
    
    def create_output_list(self, parent_frame):
        """Create the output list with inline editing capabilities"""
        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        list_box.set_margin_left(12)
        list_box.set_margin_right(12)
        list_box.set_margin_top(12)
        list_box.set_margin_bottom(12)
        
        # Instructions label
        instructions = Gtk.Label()
        instructions.set_markup("<i>Double-click position, resolution, or scale values to edit</i>")
        instructions.set_halign(Gtk.Align.START)
        list_box.pack_start(instructions, False, False, 0)
        
        # Output list with editable cells
        # Store: name, resolution, position, scale, enabled, output_object
        self.output_store = Gtk.ListStore(str, str, str, str, bool, object)
        self.output_tree = Gtk.TreeView(model=self.output_store)
        self.output_tree.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        
        # Name column (read-only)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Output", renderer, text=0)
        column.set_min_width(100)
        column.set_resizable(True)
        self.output_tree.append_column(column)
        
        # Resolution column (editable with dropdown)
        self.resolution_renderer = Gtk.CellRendererCombo()
        self.resolution_renderer.set_property("editable", True)
        self.resolution_renderer.set_property("model", Gtk.ListStore(str))
        self.resolution_renderer.set_property("text-column", 0)
        self.resolution_renderer.set_property("has-entry", False)
        self.resolution_renderer.connect("edited", self.on_resolution_edited)
        
        column = Gtk.TreeViewColumn("Resolution", self.resolution_renderer, text=1)
        column.set_min_width(120)
        column.set_resizable(True)
        self.output_tree.append_column(column)
        
        # Position column (editable)
        position_renderer = Gtk.CellRendererText()
        position_renderer.set_property("editable", True)
        position_renderer.connect("edited", self.on_position_edited)
        
        column = Gtk.TreeViewColumn("Position (X,Y)", position_renderer, text=2)
        column.set_min_width(120)
        column.set_resizable(True)
        self.output_tree.append_column(column)
        
        # Scale column (editable)
        scale_renderer = Gtk.CellRendererText()
        scale_renderer.set_property("editable", True)
        scale_renderer.connect("edited", self.on_scale_edited)
        
        column = Gtk.TreeViewColumn("Scale", scale_renderer, text=3)
        column.set_min_width(80)
        column.set_resizable(True)
        self.output_tree.append_column(column)
        
        # Enabled column (checkbox)
        enabled_renderer = Gtk.CellRendererToggle()
        enabled_renderer.connect("toggled", self.on_enabled_toggled)
        
        column = Gtk.TreeViewColumn("Enabled", enabled_renderer, active=4)
        column.set_min_width(80)
        self.output_tree.append_column(column)
        
        # Connect selection changed
        selection = self.output_tree.get_selection()
        selection.connect("changed", self.on_tree_selection_changed)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_size_request(-1, 300)
        scrolled.add(self.output_tree)
        list_box.pack_start(scrolled, True, True, 0)
        
        # Control buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        # Apply config button
        apply_btn = Gtk.Button.new_with_label("⚡ Apply Config")
        apply_btn.connect('clicked', self.on_apply_config)
        apply_btn.set_tooltip_text("Apply current configuration to sway immediately")
        button_box.pack_start(apply_btn, False, False, 0)
        
        # Save config button
        save_config_btn = Gtk.Button.new_with_label("💾 Save to Config")
        save_config_btn.connect('clicked', self.on_save_config)
        save_config_btn.set_tooltip_text("Save configuration to sway config file")
        button_box.pack_start(save_config_btn, False, False, 0)
        
        list_box.pack_start(button_box, False, False, 0)
        
        parent_frame.add(list_box)
    
    def refresh_outputs(self):
        """Refresh the list of outputs"""
        self.outputs = self.parser.get_current_outputs()
        
        # Update monitor widget
        self.monitor_widget.outputs = self.outputs
        self.monitor_widget.update_scale()
        self.monitor_widget.queue_draw()
        
        # Update output list
        self.output_store.clear()
        for output in self.outputs:
            self.output_store.append([
                output.name,
                f"{output.resolution[0]}x{output.resolution[1]}",
                f"{output.position[0]}, {output.position[1]}",
                f"{output.scale:.1f}",
                output.enabled,
                output
            ])
        
        # Update output combo
        self.output_combo.remove_all()
        for output in self.outputs:
            self.output_combo.append_text(output.name)
        
        if self.outputs:
            self.output_combo.set_active(0)
        
        self.update_status(f"Found {len(self.outputs)} outputs")
        
        # Update config path in status
        config_path = self.parser.get_config_path()
        if config_path:
            self.update_status(f"Found {len(self.outputs)} outputs | Config: {config_path}")
        else:
            self.update_status(f"Found {len(self.outputs)} outputs | No config file found")
    
    def update_status(self, message: str):
        """Update status bar"""
        context_id = self.status_bar.get_context_id("main")
        self.status_bar.push(context_id, message)
    
    def on_output_selected(self, widget, output):
        """Handle output selection from monitor widget"""
        self.selected_output = output
        
        # Find and select in tree view
        for i, row in enumerate(self.output_store):
            if row[5] == output:  # Compare output objects
                selection = self.output_tree.get_selection()
                selection.select_iter(self.output_store.get_iter(i))
                break
    
    def on_output_changed(self, widget, output):
        """Handle output change from monitor widget"""
        self.selected_output = output
        self.refresh_output_list()
    
    def refresh_output_list(self):
        """Refresh the output list display"""
        self.output_store.clear()
        for output in self.outputs:
            self.output_store.append([
                output.name,
                f"{output.resolution[0]}x{output.resolution[1]}",
                f"{output.position[0]}, {output.position[1]}",
                f"{output.scale:.1f}",
                output.enabled,
                output
            ])
    
    def on_tree_selection_changed(self, selection):
        """Handle tree selection change"""
        model, tree_iter = selection.get_selected()
        if tree_iter:
            output = model[tree_iter][5]  # Get output object from column 5
            self.selected_output = output
            self.monitor_widget.selected_output = output
            self.monitor_widget.queue_draw()
    
    def on_resolution_edited(self, renderer, path, new_text):
        """Handle resolution cell editing"""
        tree_iter = self.output_store.get_iter(path)
        output = self.output_store[tree_iter][5]  # Get output object
        
        if 'x' in new_text:
            try:
                width, height = map(int, new_text.split('x'))
                output.resolution = (width, height)
                self.output_store[tree_iter][1] = new_text
                self.monitor_widget.update_scale()
                self.monitor_widget.queue_draw()
                self.update_status(f"Updated {output.name} resolution to {new_text}")
            except ValueError:
                self.show_error(f"Invalid resolution format: {new_text}. Use format like '1920x1080'")
    
    def on_position_edited(self, renderer, path, new_text):
        """Handle position cell editing"""
        tree_iter = self.output_store.get_iter(path)
        output = self.output_store[tree_iter][5]  # Get output object
        
        # Parse position - accept formats like "0,0" or "0, 0" or "0 0"
        try:
            # Replace common separators with comma and split
            clean_text = new_text.replace(' ', ',').replace(',', ' ').strip()
            parts = clean_text.split()
            if len(parts) == 2:
                x, y = map(int, parts)
                output.position = (x, y)
                self.output_store[tree_iter][2] = f"{x}, {y}"
                self.monitor_widget.queue_draw()
                self.update_status(f"Updated {output.name} position to ({x}, {y})")
            else:
                raise ValueError("Need exactly 2 values")
        except ValueError:
            self.show_error(f"Invalid position format: {new_text}. Use format like '0, 0' or '1920 0'")
    
    def on_scale_edited(self, renderer, path, new_text):
        """Handle scale cell editing"""
        tree_iter = self.output_store.get_iter(path)
        output = self.output_store[tree_iter][5]  # Get output object
        
        try:
            scale = float(new_text)
            if 0.1 <= scale <= 5.0:
                output.scale = scale
                self.output_store[tree_iter][3] = f"{scale:.1f}"
                self.update_status(f"Updated {output.name} scale to {scale:.1f}")
            else:
                raise ValueError("Scale must be between 0.1 and 5.0")
        except ValueError as e:
            self.show_error(f"Invalid scale value: {new_text}. {str(e)}")
    
    def on_enabled_toggled(self, renderer, path):
        """Handle enabled checkbox toggle"""
        tree_iter = self.output_store.get_iter(path)
        output = self.output_store[tree_iter][5]  # Get output object
        
        # Toggle enabled state
        output.enabled = not output.enabled
        self.output_store[tree_iter][4] = output.enabled
        
        status = "enabled" if output.enabled else "disabled"
        self.update_status(f"{output.name} {status}")
    
    def on_select_config(self, widget):
        """Handle select config file"""
        dialog = Gtk.FileChooserDialog(
            title="Select Sway Config File",
            parent=self.window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        # Set default path
        current_config = self.parser.get_config_path()
        if current_config:
            dialog.set_filename(current_config)
        else:
            dialog.set_current_folder(os.path.expanduser("~/.config/sway"))
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            config_path = dialog.get_filename()
            self.parser.set_config_path(config_path)
            self.update_status(f"Config file set to: {config_path}")
        
        dialog.destroy()
    
    def on_save_config(self, widget):
        """Handle save monitor config"""
        if not self.parser.get_config_path():
            self.show_error("No config file selected. Please select a config file first.")
            return
        
        try:
            success = self.parser.save_config_file(backup=True)
            if success:
                self.show_info("Monitor Configuration Saved", 
                             "Monitor configuration has been saved to the sway config file.\n"
                             "A backup was created with .backup extension.")
            else:
                self.show_error("Failed to save config file")
        except Exception as e:
            self.show_error(f"Error saving config: {e}")
    
    def on_apply_config(self, widget):
        """Handle apply monitor config"""
        for output in self.outputs:
            success = self.parser.apply_output_config(output)
            if not success:
                self.show_error(f"Failed to apply config for {output.name}")
                return
        
        self.show_info("Configuration Applied", 
                      "Monitor configuration has been applied to sway.\n"
                      "Changes will take effect immediately.")
    
    def on_show_config_path(self, widget):
        """Show current config path"""
        config_path = self.parser.get_config_path()
        if config_path:
            self.show_info("Sway Config Path", f"Current config file:\n{config_path}")
        else:
            self.show_info("Sway Config Path", "No config file found or selected.")
    
    def on_refresh_outputs(self, button):
        """Handle refresh outputs button"""
        self.refresh_outputs()
    
    def on_mode_changed(self, combo):
        """Handle mode selection change"""
        active_text = combo.get_active_text()
        if active_text:
            self.current_mode = active_text.lower()
            self.update_status(f"Mode changed to: {active_text}")
    
    def on_load_image(self, button):
        """Handle load image button"""
        dialog = Gtk.FileChooserDialog(
            title="Choose an image",
            parent=self.window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        # Add image filter
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Images")
        filter_images.add_mime_type("image/jpeg")
        filter_images.add_mime_type("image/png")
        filter_images.add_mime_type("image/gif")
        filter_images.add_mime_type("image/bmp")
        filter_images.add_mime_type("image/tiff")
        dialog.add_filter(filter_images)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.current_image_path = dialog.get_filename()
            self.load_image_preview()
            self.save_btn.set_sensitive(True)
            self.image_label.set_text(f"Image: {os.path.basename(self.current_image_path)}")
            self.update_status(f"Loaded image: {self.current_image_path}")
        
        dialog.destroy()
    
    def load_image_preview(self):
        """Load and display image preview"""
        if not self.current_image_path:
            return
        
        try:
            # Load image info
            with Image.open(self.current_image_path) as img:
                width, height = img.size
                format_name = img.format or "Unknown"
                file_size = os.path.getsize(self.current_image_path)
                file_size_mb = file_size / (1024 * 1024)
                
                self.image_info_label.set_text(
                    f"Size: {width}×{height}\n"
                    f"Format: {format_name}\n"
                    f"File size: {file_size_mb:.1f} MB"
                )
            
            # Load preview for the image widget
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                self.current_image_path, 300, 200, True
            )
            self.preview_image.set_from_pixbuf(pixbuf)
            
            # Set preview on monitor widget
            self.monitor_widget.set_preview_image(self.current_image_path)
            
        except Exception as e:
            self.show_error(f"Error loading image preview: {e}")
            self.image_info_label.set_text("Error loading image")
    
    def on_save_background(self, button):
        """Handle save background button"""
        if not self.current_image_path:
            self.show_error("Please load an image first")
            return
        
        if not self.outputs:
            self.show_error("No outputs available")
            return
        
        # Run in background thread to avoid freezing UI
        def apply_background():
            if self.current_mode == "stretched":
                success = self.background_manager.set_background_stretched(
                    self.current_image_path, self.outputs
                )
            else:
                success = self.background_manager.set_background_fitted(
                    self.current_image_path, self.outputs, self.current_mode
                )
            
            GLib.idle_add(self.on_background_applied, success, self.current_mode)
        
        self.update_status(f"Applying background ({self.current_mode} mode)...")
        self.save_btn.set_sensitive(False)
        threading.Thread(target=apply_background, daemon=True).start()
    
    def on_background_applied(self, success: bool, mode: str):
        """Called when background application is complete"""
        self.save_btn.set_sensitive(True)
        
        if success:
            self.update_status(f"Background applied successfully ({mode} mode)")
            # Show success notification
            self.show_info("Background Applied Successfully!", 
                          f"Background set in {mode} mode across all monitors.")
        else:
            self.update_status(f"Failed to apply background ({mode} mode)")
            self.show_error(f"Failed to apply background in {mode} mode")
        
        return False  # Don't repeat this idle callback
    
    def show_error(self, message: str):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
    
    def show_info(self, title: str, message: str):
        """Show info dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def on_quit(self, widget, event=None):
        """Handle quit event"""
        self.background_manager.cleanup()
        Gtk.main_quit()
        return False  # Allow window to close
    
    def run(self):
        """Run the application"""
        Gtk.main()


def main():
    """Main entry point"""
    app = SwayBGPlusGUI()
    app.run()


if __name__ == "__main__":
    main() 