"""
Split Tool Panel

GUI panel for the GIF split tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.split import split_gif


class SplitPanel:
    """Panel for GIF split operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the split panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.setup_ui()
    
    def setup_ui(self):
        """Create the split panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Split GIF into Frames", padding="10")
        
        # Split options
        ttk.Label(self.frame, text="Split Options:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Split mode
        self.split_mode_var = tk.StringVar(value="all")
        mode_frame = ttk.Frame(self.frame)
        mode_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        mode_options = [
            ("All Frames", "all"),
            ("Range", "range"),
            ("Every Nth", "every_nth"),
            ("Key Frames", "key_frames"),
        ]
        
        for i, (text, value) in enumerate(mode_options):
            btn = ttk.Radiobutton(
                mode_frame, 
                text=text, 
                variable=self.split_mode_var, 
                value=value,
                command=self.update_controls
            )
            btn.grid(row=0, column=i, padx=(0, 10), sticky=tk.W)
        
        # Range controls
        self.range_frame = ttk.LabelFrame(self.frame, text="Frame Range", padding="5")
        self.range_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.range_frame, text="Start Frame:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.start_frame_var = tk.StringVar(value="0")
        ttk.Entry(self.range_frame, textvariable=self.start_frame_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(self.range_frame, text="End Frame:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.end_frame_var = tk.StringVar(value="10")
        ttk.Entry(self.range_frame, textvariable=self.end_frame_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Every Nth controls
        self.nth_frame = ttk.LabelFrame(self.frame, text="Every Nth Frame", padding="5")
        self.nth_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.nth_frame, text="N (every Nth frame):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.nth_var = tk.StringVar(value="2")
        ttk.Entry(self.nth_frame, textvariable=self.nth_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Key frames controls
        self.key_frame = ttk.LabelFrame(self.frame, text="Key Frames", padding="5")
        self.key_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.key_method_var = tk.StringVar(value="first_last_middle")
        key_combo = ttk.Combobox(
            self.key_frame, 
            textvariable=self.key_method_var,
            values=["first_last_middle", "first_last", "middle_only", "custom"],
            state="readonly",
            width=20
        )
        key_combo.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Output format
        ttk.Label(self.frame, text="Output Format:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.output_format_var,
            values=["png", "jpg", "bmp", "tiff"],
            state="readonly",
            width=15
        )
        format_combo.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Quality controls
        ttk.Label(self.frame, text="Quality:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.IntVar(value=95)
        quality_scale = ttk.Scale(
            self.frame, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        quality_scale.grid(row=5, column=1, columnspan=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Quality value label
        self.quality_label = ttk.Label(self.frame, text="95")
        self.quality_label.grid(row=5, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Update quality label when scale changes
        quality_scale.configure(command=self.update_quality_label)
        
        # Naming pattern
        ttk.Label(self.frame, text="Naming Pattern:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.naming_var = tk.StringVar(value="frame_{:04d}")
        ttk.Entry(self.frame, textvariable=self.naming_var, width=20).grid(row=6, column=1, columnspan=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Split GIF", 
            command=self.process_split
        )
        self.process_btn.grid(row=7, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
        
        # Initialize controls visibility
        self.update_controls()
    
    def update_controls(self):
        """Update control visibility based on split mode."""
        mode = self.split_mode_var.get()
        
        # Show/hide range controls
        if mode == "range":
            self.range_frame.grid()
        else:
            self.range_frame.grid_remove()
        
        # Show/hide nth controls
        if mode == "every_nth":
            self.nth_frame.grid()
        else:
            self.nth_frame.grid_remove()
        
        # Show/hide key frames controls
        if mode == "key_frames":
            self.key_frame.grid()
        else:
            self.key_frame.grid_remove()
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current split settings."""
        try:
            mode = self.split_mode_var.get()
            quality = self.quality_var.get()
            output_format = self.output_format_var.get()
            naming_pattern = self.naming_var.get()
            
            settings = {
                'mode': mode,
                'quality': quality,
                'output_format': output_format,
                'naming_pattern': naming_pattern
            }
            
            if mode == "range":
                start_frame = int(self.start_frame_var.get())
                end_frame = int(self.end_frame_var.get())
                settings.update({
                    'start_frame': start_frame,
                    'end_frame': end_frame
                })
            elif mode == "every_nth":
                nth = int(self.nth_var.get())
                settings['nth'] = nth
            elif mode == "key_frames":
                method = self.key_method_var.get()
                settings['key_method'] = method
                
        except ValueError as e:
            raise ValueError(f"Invalid numeric value: {e}")
        
        return settings
    
    def process_split(self):
        """Process the split operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('split', settings)
            else:
                messagebox.showinfo("Split", f"Split settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Split failed: {e}")
    
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
