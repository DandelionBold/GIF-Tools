"""
Optimize Tool Panel

GUI panel for the GIF optimize tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.optimize import optimize_gif


class OptimizePanel:
    """Panel for GIF optimize operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the optimize panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.current_gif_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the optimize panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Optimize GIF", padding="10")
        
        # Description
        desc_text = "Optimize your GIF to reduce file size while maintaining visual quality."
        ttk.Label(self.frame, text=desc_text, wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Optimization level
        ttk.Label(self.frame, text="Optimization Level:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        self.optimization_level_var = tk.StringVar(value="balanced")
        level_frame = ttk.Frame(self.frame)
        level_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        level_options = [
            ("Light", "light"),
            ("Balanced", "balanced"),
            ("Aggressive", "aggressive"),
            ("Custom", "custom"),
        ]
        
        for i, (text, value) in enumerate(level_options):
            btn = ttk.Radiobutton(
                level_frame, 
                text=text, 
                variable=self.optimization_level_var, 
                value=value,
                command=self.update_controls
            )
            btn.grid(row=0, column=i, padx=(0, 15), sticky=tk.W)
        
        # Custom settings frame
        self.custom_frame = ttk.LabelFrame(self.frame, text="Custom Settings", padding="5")
        self.custom_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Quality
        ttk.Label(self.custom_frame, text="Quality (1-100):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(
            self.custom_frame, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        quality_scale.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Quality value label
        self.quality_label = ttk.Label(self.custom_frame, text="85")
        self.quality_label.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Update quality label when scale changes
        quality_scale.configure(command=self.update_quality_label)
        
        # Color reduction
        ttk.Label(self.custom_frame, text="Color Reduction:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.color_reduction_var = tk.StringVar(value="adaptive")
        color_combo = ttk.Combobox(
            self.custom_frame, 
            textvariable=self.color_reduction_var,
            values=["none", "adaptive", "fixed"],
            state="readonly",
            width=15
        )
        color_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Max colors
        ttk.Label(self.custom_frame, text="Max Colors:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.max_colors_var = tk.StringVar(value="256")
        ttk.Entry(self.custom_frame, textvariable=self.max_colors_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Dithering
        self.dither_var = tk.BooleanVar(value=True)
        dither_check = ttk.Checkbutton(
            self.custom_frame, 
            text="Enable Dithering", 
            variable=self.dither_var
        )
        dither_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Optimization options
        ttk.Label(self.frame, text="Optimization Options:").grid(row=3, column=0, sticky=tk.W, pady=10)
        
        options_frame = ttk.Frame(self.frame)
        options_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.remove_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Remove duplicate frames", variable=self.remove_duplicates_var).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.optimize_palette_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Optimize color palette", variable=self.optimize_palette_var).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        self.reduce_colors_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Reduce color count", variable=self.reduce_colors_var).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.compress_frames_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Compress frames", variable=self.compress_frames_var).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Advanced options
        self.advanced_var = tk.BooleanVar(value=False)
        advanced_check = ttk.Checkbutton(
            self.frame, 
            text="Show Advanced Options", 
            variable=self.advanced_var,
            command=self.toggle_advanced
        )
        advanced_check.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Advanced frame
        self.advanced_frame = ttk.LabelFrame(self.frame, text="Advanced Options", padding="5")
        self.advanced_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Lossy compression
        ttk.Label(self.advanced_frame, text="Lossy Compression:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lossy_var = tk.IntVar(value=0)
        lossy_scale = ttk.Scale(
            self.advanced_frame, 
            from_=0, 
            to=100, 
            variable=self.lossy_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        lossy_scale.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Lossy value label
        self.lossy_label = ttk.Label(self.advanced_frame, text="0")
        self.lossy_label.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Update lossy label when scale changes
        lossy_scale.configure(command=self.update_lossy_label)
        
        # Interlacing
        self.interlace_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.advanced_frame, text="Enable Interlacing", variable=self.interlace_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Optimize GIF", 
            command=self.process_optimize
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
        
        # Initialize controls visibility
        self.update_controls()
        self.toggle_advanced()
    
    def update_controls(self):
        """Update control visibility based on optimization level."""
        level = self.optimization_level_var.get()
        
        # Show/hide custom settings
        if level == "custom":
            self.custom_frame.grid()
        else:
            self.custom_frame.grid_remove()
            
            # Set preset values
            if level == "light":
                self.quality_var.set(95)
                self.color_reduction_var.set("none")
                self.max_colors_var.set("256")
                self.dither_var.set(False)
            elif level == "balanced":
                self.quality_var.set(85)
                self.color_reduction_var.set("adaptive")
                self.max_colors_var.set("128")
                self.dither_var.set(True)
            elif level == "aggressive":
                self.quality_var.set(70)
                self.color_reduction_var.set("fixed")
                self.max_colors_var.set("64")
                self.dither_var.set(True)
    
    def toggle_advanced(self):
        """Toggle advanced options visibility."""
        if self.advanced_var.get():
            self.advanced_frame.grid()
        else:
            self.advanced_frame.grid_remove()
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def update_lossy_label(self, value):
        """Update the lossy label when scale changes."""
        self.lossy_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current optimize settings."""
        if not self.current_gif_path:
            raise ValueError("No GIF file loaded")
            
        try:
            level = self.optimization_level_var.get()
            quality = self.quality_var.get()
            
            settings = {
                'input_path': self.current_gif_path,
                'level': level,
                'quality': quality,
                'remove_duplicates': self.remove_duplicates_var.get(),
                'optimize_palette': self.optimize_palette_var.get(),
                'reduce_colors': self.reduce_colors_var.get(),
                'compress_frames': self.compress_frames_var.get()
            }
            
            if level == "custom":
                settings.update({
                    'color_reduction': self.color_reduction_var.get(),
                    'max_colors': int(self.max_colors_var.get()),
                    'dither': self.dither_var.get()
                })
            
            if self.advanced_var.get():
                settings.update({
                    'lossy': self.lossy_var.get(),
                    'interlace': self.interlace_var.get()
                })
                
        except ValueError as e:
            raise ValueError(f"Invalid numeric value: {e}")
        
        return settings
    
    def process_optimize(self):
        """Process the optimize operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('optimize', settings)
            else:
                messagebox.showinfo("Optimize", f"Optimize settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Optimize failed: {e}")
    
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
    
    def auto_load_gif(self, gif_path: str):
        """Auto-load GIF for optimization."""
        # Store the path and update status if status_label exists
        self.current_gif_path = gif_path
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"GIF loaded: {Path(gif_path).name}")
