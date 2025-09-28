"""
Rotate Tool Panel

GUI panel for the GIF rotate tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.rotate import rotate_gif


class RotatePanel(ttk.Frame):
    """Panel for GIF rotate operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the rotate panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        super().__init__(parent)
        self.parent = parent
        self.on_process = on_process
        self.setup_ui()
    
    def setup_ui(self):
        """Create the rotate panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self, text="Rotate GIF", padding="10")
        
        # Rotation angle
        ttk.Label(self.frame, text="Rotation Angle:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Angle selection frame
        angle_frame = ttk.Frame(self.frame)
        angle_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.angle_var = tk.StringVar(value="90")
        angle_buttons = [
            ("90°", "90"),
            ("180°", "180"),
            ("270°", "270"),
        ]
        
        for i, (text, value) in enumerate(angle_buttons):
            btn = ttk.Radiobutton(
                angle_frame, 
                text=text, 
                variable=self.angle_var, 
                value=value
            )
            btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Custom angle entry
        ttk.Label(self.frame, text="Custom Angle:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.custom_angle_var = tk.StringVar(value="90")
        custom_entry = ttk.Entry(self.frame, textvariable=self.custom_angle_var, width=10)
        custom_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Flip options
        ttk.Label(self.frame, text="Flip Options:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        flip_frame = ttk.Frame(self.frame)
        flip_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.flip_horizontal_var = tk.BooleanVar(value=False)
        self.flip_vertical_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(flip_frame, text="Horizontal", variable=self.flip_horizontal_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(flip_frame, text="Vertical", variable=self.flip_vertical_var).pack(side=tk.LEFT)
        
        # Quality controls
        ttk.Label(self.frame, text="Quality:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(
            self.frame, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        quality_scale.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Quality value label
        self.quality_label = ttk.Label(self.frame, text="85")
        self.quality_label.grid(row=3, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Update quality label when scale changes
        quality_scale.configure(command=self.update_quality_label)
        
        # Background color
        ttk.Label(self.frame, text="Background:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.bg_color_var = tk.StringVar(value="transparent")
        bg_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.bg_color_var,
            values=["transparent", "white", "black", "red", "green", "blue"],
            state="readonly",
            width=15
        )
        bg_combo.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Expand to fit
        self.expand_var = tk.BooleanVar(value=True)
        expand_check = ttk.Checkbutton(
            self.frame, 
            text="Expand to fit rotated content", 
            variable=self.expand_var
        )
        expand_check.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Rotate GIF", 
            command=self.process_rotate
        )
        self.process_btn.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
        
        # Pack the frame
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current rotate settings."""
        try:
            # Get rotation angle
            if self.angle_var.get() in ["90", "180", "270"]:
                angle = int(self.angle_var.get())
            else:
                angle = int(self.custom_angle_var.get())
            
            quality = self.quality_var.get()
            
        except ValueError as e:
            raise ValueError(f"Invalid angle value: {e}")
        
        settings = {
            'angle': angle,
            'quality': quality,
            'expand': self.expand_var.get()
        }
        
        # Add flip settings
        if self.flip_horizontal_var.get() or self.flip_vertical_var.get():
            settings['flip'] = []
            if self.flip_horizontal_var.get():
                settings['flip'].append('horizontal')
            if self.flip_vertical_var.get():
                settings['flip'].append('vertical')
        
        # Add background color
        bg_color = self.bg_color_var.get()
        if bg_color != "transparent":
            settings['background_color'] = bg_color
        
        return settings
    
    def process_rotate(self):
        """Process the rotate operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('rotate', settings)
            else:
                messagebox.showinfo("Rotate", f"Rotate settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Rotate failed: {e}")
    
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
