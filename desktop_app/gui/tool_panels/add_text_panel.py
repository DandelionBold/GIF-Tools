"""
Add Text Tool Panel

GUI panel for the GIF add text tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.add_text import add_text_to_gif


class AddTextPanel:
    """Panel for GIF add text operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the add text panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.setup_ui()
    
    def setup_ui(self):
        """Create the add text panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Add Text to GIF", padding="10")
        
        # Text input
        ttk.Label(self.frame, text="Text:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.text_var = tk.StringVar(value="Hello World!")
        text_entry = ttk.Entry(self.frame, textvariable=self.text_var, width=30)
        text_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Position controls
        ttk.Label(self.frame, text="Position:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # X position
        ttk.Label(self.frame, text="X:").grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.x_var = tk.StringVar(value="10")
        x_entry = ttk.Entry(self.frame, textvariable=self.x_var, width=8)
        x_entry.grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Y position
        ttk.Label(self.frame, text="Y:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(self.frame, text="Y:").grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.y_var = tk.StringVar(value="10")
        y_entry = ttk.Entry(self.frame, textvariable=self.y_var, width=8)
        y_entry.grid(row=2, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Font controls
        ttk.Label(self.frame, text="Font:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.font_family_var = tk.StringVar(value="Arial")
        font_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.font_family_var,
            values=["Arial", "Times New Roman", "Courier New", "Helvetica", "Verdana"],
            state="readonly",
            width=15
        )
        font_combo.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Font size
        ttk.Label(self.frame, text="Size:").grid(row=3, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.font_size_var = tk.StringVar(value="24")
        size_entry = ttk.Entry(self.frame, textvariable=self.font_size_var, width=8)
        size_entry.grid(row=3, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Color controls
        ttk.Label(self.frame, text="Color:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.color_var = tk.StringVar(value="white")
        color_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.color_var,
            values=["white", "black", "red", "green", "blue", "yellow", "cyan", "magenta"],
            state="readonly",
            width=15
        )
        color_combo.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Alignment
        ttk.Label(self.frame, text="Alignment:").grid(row=4, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.alignment_var = tk.StringVar(value="left")
        align_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.alignment_var,
            values=["left", "center", "right"],
            state="readonly",
            width=8
        )
        align_combo.grid(row=4, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Background controls
        self.bg_enabled_var = tk.BooleanVar(value=False)
        bg_check = ttk.Checkbutton(
            self.frame, 
            text="Background", 
            variable=self.bg_enabled_var,
            command=self.toggle_background
        )
        bg_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Background color
        self.bg_color_var = tk.StringVar(value="black")
        self.bg_color_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.bg_color_var,
            values=["black", "white", "red", "green", "blue", "yellow", "cyan", "magenta"],
            state="readonly",
            width=15
        )
        self.bg_color_combo.grid(row=5, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.bg_color_combo.config(state=tk.DISABLED)
        
        # Background opacity
        ttk.Label(self.frame, text="Opacity:").grid(row=5, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.bg_opacity_var = tk.DoubleVar(value=0.5)
        opacity_scale = ttk.Scale(
            self.frame, 
            from_=0.0, 
            to=1.0, 
            variable=self.bg_opacity_var,
            orient=tk.HORIZONTAL,
            length=100
        )
        opacity_scale.grid(row=5, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        self.opacity_scale = opacity_scale
        self.opacity_scale.config(state=tk.DISABLED)
        
        # Stroke controls
        self.stroke_enabled_var = tk.BooleanVar(value=False)
        stroke_check = ttk.Checkbutton(
            self.frame, 
            text="Stroke", 
            variable=self.stroke_enabled_var,
            command=self.toggle_stroke
        )
        stroke_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Stroke width
        ttk.Label(self.frame, text="Width:").grid(row=6, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.stroke_width_var = tk.StringVar(value="2")
        stroke_width_entry = ttk.Entry(self.frame, textvariable=self.stroke_width_var, width=8)
        stroke_width_entry.grid(row=6, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        self.stroke_width_entry = stroke_width_entry
        self.stroke_width_entry.config(state=tk.DISABLED)
        
        # Stroke color
        ttk.Label(self.frame, text="Color:").grid(row=6, column=3, sticky=tk.W, padx=(20, 0), pady=5)
        self.stroke_color_var = tk.StringVar(value="black")
        self.stroke_color_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.stroke_color_var,
            values=["black", "white", "red", "green", "blue", "yellow", "cyan", "magenta"],
            state="readonly",
            width=8
        )
        self.stroke_color_combo.grid(row=6, column=4, sticky=tk.W, padx=(5, 0), pady=5)
        self.stroke_color_combo.config(state=tk.DISABLED)
        
        # Quality control
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
        quality_scale.grid(row=7, column=1, columnspan=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Quality value label
        self.quality_label = ttk.Label(self.frame, text="85")
        self.quality_label.grid(row=7, column=4, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Update quality label when scale changes
        quality_scale.configure(command=self.update_quality_label)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Add Text to GIF", 
            command=self.process_add_text
        )
        self.process_btn.grid(row=8, column=0, columnspan=4, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=9, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
    
    def toggle_background(self):
        """Toggle background controls."""
        if self.bg_enabled_var.get():
            self.bg_color_combo.config(state=tk.NORMAL)
            self.opacity_scale.config(state=tk.NORMAL)
        else:
            self.bg_color_combo.config(state=tk.DISABLED)
            self.opacity_scale.config(state=tk.DISABLED)
    
    def toggle_stroke(self):
        """Toggle stroke controls."""
        if self.stroke_enabled_var.get():
            self.stroke_width_entry.config(state=tk.NORMAL)
            self.stroke_color_combo.config(state=tk.NORMAL)
        else:
            self.stroke_width_entry.config(state=tk.DISABLED)
            self.stroke_color_combo.config(state=tk.DISABLED)
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current add text settings."""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            font_size = int(self.font_size_var.get())
            stroke_width = int(self.stroke_width_var.get()) if self.stroke_enabled_var.get() else 0
        except ValueError:
            raise ValueError("Position and size values must be integers")
        
        settings = {
            'text': self.text_var.get(),
            'position': (x, y),
            'font_family': self.font_family_var.get(),
            'font_size': font_size,
            'color': self.color_var.get(),
            'alignment': self.alignment_var.get(),
            'quality': self.quality_var.get()
        }
        
        # Add background settings if enabled
        if self.bg_enabled_var.get():
            settings.update({
                'background_color': self.bg_color_var.get(),
                'background_opacity': self.bg_opacity_var.get()
            })
        
        # Add stroke settings if enabled
        if self.stroke_enabled_var.get():
            settings.update({
                'stroke_width': stroke_width,
                'stroke_color': self.stroke_color_var.get()
            })
        
        return settings
    
    def process_add_text(self):
        """Process the add text operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('add_text', settings)
            else:
                messagebox.showinfo("Add Text", f"Add text settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Add text failed: {e}")
    
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
    
    def auto_load_gif(self, file_path: Path):
        """Auto-load GIF file for text addition."""
        try:
            self.current_file = file_path
            # Update status or show preview if needed
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Loaded: {file_path.name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GIF: {e}")
