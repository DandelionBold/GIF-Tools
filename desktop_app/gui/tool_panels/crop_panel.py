"""
Crop Tool Panel

GUI panel for the GIF crop tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.crop import crop_gif


class CropPanel(ttk.Frame):
    """Panel for GIF crop operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the crop panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        super().__init__(parent)
        self.parent = parent
        self.on_process = on_process
        self.setup_ui()
    
    def setup_ui(self):
        """Create the crop panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self, text="Crop GIF", padding="10")
        
        # Crop coordinates
        ttk.Label(self.frame, text="Crop Area:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # X coordinate
        ttk.Label(self.frame, text="X (left):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.x_var = tk.StringVar(value="0")
        x_entry = ttk.Entry(self.frame, textvariable=self.x_var, width=10)
        x_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Y coordinate
        ttk.Label(self.frame, text="Y (top):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.y_var = tk.StringVar(value="0")
        y_entry = ttk.Entry(self.frame, textvariable=self.y_var, width=10)
        y_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Width
        ttk.Label(self.frame, text="Width:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar(value="100")
        width_entry = ttk.Entry(self.frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Height
        ttk.Label(self.frame, text="Height:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.StringVar(value="100")
        height_entry = ttk.Entry(self.frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Preset crop options
        ttk.Label(self.frame, text="Presets:").grid(row=5, column=0, sticky=tk.W, pady=5)
        
        preset_frame = ttk.Frame(self.frame)
        preset_frame.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        preset_buttons = [
            ("Center Square", self.set_center_square),
            ("Top Half", self.set_top_half),
            ("Bottom Half", self.set_bottom_half),
            ("Left Half", self.set_left_half),
            ("Right Half", self.set_right_half),
        ]
        
        for i, (text, command) in enumerate(preset_buttons):
            row, col = divmod(i, 2)
            btn = ttk.Button(preset_frame, text=text, command=command, width=12)
            btn.grid(row=row, column=col, padx=2, pady=2)
        
        # Crop mode
        ttk.Label(self.frame, text="Crop Mode:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.mode_var = tk.StringVar(value="exact")
        mode_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.mode_var,
            values=["exact", "safe", "center"],
            state="readonly",
            width=15
        )
        mode_combo.grid(row=6, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Quality controls
        ttk.Label(self.frame, text="Quality:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(
            self.frame, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        quality_scale.grid(row=7, column=1, columnspan=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Quality value label
        self.quality_label = ttk.Label(self.frame, text="85")
        self.quality_label.grid(row=7, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Update quality label when scale changes
        quality_scale.configure(command=self.update_quality_label)
        
        # Background color
        ttk.Label(self.frame, text="Background:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.bg_color_var = tk.StringVar(value="transparent")
        bg_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.bg_color_var,
            values=["transparent", "white", "black", "red", "green", "blue"],
            state="readonly",
            width=15
        )
        bg_combo.grid(row=8, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Crop GIF", 
            command=self.process_crop
        )
        self.process_btn.grid(row=9, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
        
        # Pack the frame
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def set_center_square(self):
        """Set crop area to center square."""
        self.x_var.set("50")
        self.y_var.set("50")
        self.width_var.set("100")
        self.height_var.set("100")
    
    def set_top_half(self):
        """Set crop area to top half."""
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set("200")
        self.height_var.set("100")
    
    def set_bottom_half(self):
        """Set crop area to bottom half."""
        self.x_var.set("0")
        self.y_var.set("100")
        self.width_var.set("200")
        self.height_var.set("100")
    
    def set_left_half(self):
        """Set crop area to left half."""
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set("100")
        self.height_var.set("200")
    
    def set_right_half(self):
        """Set crop area to right half."""
        self.x_var.set("100")
        self.y_var.set("0")
        self.width_var.set("100")
        self.height_var.set("200")
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current crop settings."""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            quality = self.quality_var.get()
            
        except ValueError as e:
            raise ValueError(f"Invalid numeric value: {e}")
        
        settings = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'mode': self.mode_var.get(),
            'quality': quality
        }
        
        # Add background color
        bg_color = self.bg_color_var.get()
        if bg_color != "transparent":
            settings['background_color'] = bg_color
        
        return settings
    
    def process_crop(self):
        """Process the crop operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('crop', settings)
            else:
                messagebox.showinfo("Crop", f"Crop settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Crop failed: {e}")
    
    def start_progress(self):
        """Start the progress bar."""
        self.progress_bar.start()
        self.process_btn.config(state=tk.DISABLED)
    
    def stop_progress(self):
        """Stop the progress bar."""
        self.progress_bar.stop()
        self.process_btn.config(state=tk.NORMAL)
    
    def get_widget(self) -> tk.Widget:
        """Get the main widget for this panel."""
        return self.frame
