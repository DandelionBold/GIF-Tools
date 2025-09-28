"""
Resize Tool Panel

GUI panel for the GIF resize tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.resize import resize_gif


class ResizePanel(ttk.Frame):
    """Panel for GIF resize operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the resize panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        super().__init__(parent)
        self.parent = parent
        self.on_process = on_process
        self.setup_ui()
    
    def setup_ui(self):
        """Create the resize panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self, text="Resize GIF", padding="10")
        
        # Width control
        ttk.Label(self.frame, text="Width:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar(value="100")
        width_entry = ttk.Entry(self.frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Height control
        ttk.Label(self.frame, text="Height:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.StringVar(value="100")
        height_entry = ttk.Entry(self.frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Aspect ratio checkbox
        self.maintain_aspect_var = tk.BooleanVar(value=True)
        aspect_check = ttk.Checkbutton(
            self.frame, 
            text="Maintain aspect ratio", 
            variable=self.maintain_aspect_var
        )
        aspect_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Resize method
        ttk.Label(self.frame, text="Method:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.method_var = tk.StringVar(value="lanczos")
        method_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.method_var,
            values=["lanczos", "bilinear", "bicubic", "nearest"],
            state="readonly",
            width=10
        )
        method_combo.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Quality control
        ttk.Label(self.frame, text="Quality:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(
            self.frame, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        quality_scale.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Quality value label
        self.quality_label = ttk.Label(self.frame, text="85")
        self.quality_label.grid(row=4, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Update quality label when scale changes
        quality_scale.configure(command=self.update_quality_label)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Resize GIF", 
            command=self.process_resize
        )
        self.process_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
        
        # Pack the frame
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current resize settings."""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
        except ValueError:
            raise ValueError("Width and height must be integers")
        
        return {
            'width': width,
            'height': height,
            'maintain_aspect': self.maintain_aspect_var.get(),
            'method': self.method_var.get(),
            'quality': self.quality_var.get()
        }
    
    def process_resize(self):
        """Process the resize operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('resize', settings)
            else:
                messagebox.showinfo("Resize", f"Resize settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Resize failed: {e}")
    
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
