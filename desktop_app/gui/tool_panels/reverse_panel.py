"""
Reverse Tool Panel

GUI panel for the GIF reverse tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.reverse import reverse_gif


class ReversePanel:
    """Panel for GIF reverse operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the reverse panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.current_gif_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the reverse panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Reverse GIF", padding="10")
        
        # Description
        desc_text = "This tool will reverse the order of frames in your GIF, making it play backwards."
        ttk.Label(self.frame, text=desc_text, wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Reverse options
        ttk.Label(self.frame, text="Reverse Options:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        # Reverse mode
        self.reverse_mode_var = tk.StringVar(value="simple")
        mode_frame = ttk.Frame(self.frame)
        mode_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        mode_options = [
            ("Simple Reverse", "simple"),
            ("Ping-Pong", "ping_pong"),
            ("Custom Pattern", "custom"),
        ]
        
        for i, (text, value) in enumerate(mode_options):
            btn = ttk.Radiobutton(
                mode_frame, 
                text=text, 
                variable=self.reverse_mode_var, 
                value=value,
                command=self.update_controls
            )
            btn.grid(row=0, column=i, padx=(0, 15), sticky=tk.W)
        
        # Ping-pong controls
        self.ping_pong_frame = ttk.LabelFrame(self.frame, text="Ping-Pong Settings", padding="5")
        self.ping_pong_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.ping_pong_frame, text="Forward Cycles:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.forward_cycles_var = tk.StringVar(value="1")
        ttk.Entry(self.ping_pong_frame, textvariable=self.forward_cycles_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(self.ping_pong_frame, text="Reverse Cycles:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.reverse_cycles_var = tk.StringVar(value="1")
        ttk.Entry(self.ping_pong_frame, textvariable=self.reverse_cycles_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Custom pattern controls
        self.custom_frame = ttk.LabelFrame(self.frame, text="Custom Pattern", padding="5")
        self.custom_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.custom_frame, text="Pattern (e.g., 0,1,2,1,0):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pattern_var = tk.StringVar(value="0,1,2,1,0")
        ttk.Entry(self.custom_frame, textvariable=self.pattern_var, width=30).grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Quality controls
        ttk.Label(self.frame, text="Quality:").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(
            self.frame, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        quality_scale.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=(5, 0), pady=10)
        
        # Quality value label
        self.quality_label = ttk.Label(self.frame, text="85")
        self.quality_label.grid(row=4, column=3, sticky=tk.W, padx=(5, 0), pady=10)
        
        # Update quality label when scale changes
        quality_scale.configure(command=self.update_quality_label)
        
        # Preserve timing
        self.preserve_timing_var = tk.BooleanVar(value=True)
        timing_check = ttk.Checkbutton(
            self.frame, 
            text="Preserve original frame timing", 
            variable=self.preserve_timing_var
        )
        timing_check.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Reverse GIF", 
            command=self.process_reverse
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
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="No GIF loaded", foreground="gray")
        self.status_label.grid(row=8, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
        
        # Initialize controls visibility
        self.update_controls()
    
    def update_controls(self):
        """Update control visibility based on reverse mode."""
        mode = self.reverse_mode_var.get()
        
        # Show/hide ping-pong controls
        if mode == "ping_pong":
            self.ping_pong_frame.grid()
        else:
            self.ping_pong_frame.grid_remove()
        
        # Show/hide custom pattern controls
        if mode == "custom":
            self.custom_frame.grid()
        else:
            self.custom_frame.grid_remove()
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current reverse settings."""
        if not self.current_gif_path:
            raise ValueError("No GIF file loaded")
            
        try:
            mode = self.reverse_mode_var.get()
            quality = self.quality_var.get()
            
            settings = {
                'input_path': self.current_gif_path,
                'mode': mode,
                'quality': quality,
                'preserve_timing': self.preserve_timing_var.get()
            }
            
            if mode == "ping_pong":
                forward_cycles = int(self.forward_cycles_var.get())
                reverse_cycles = int(self.reverse_cycles_var.get())
                settings.update({
                    'forward_cycles': forward_cycles,
                    'reverse_cycles': reverse_cycles
                })
            elif mode == "custom":
                pattern_text = self.pattern_var.get()
                # Parse pattern (e.g., "0,1,2,1,0" -> [0,1,2,1,0])
                try:
                    pattern = [int(x.strip()) for x in pattern_text.split(',')]
                    settings['pattern'] = pattern
                except ValueError:
                    raise ValueError("Invalid pattern format. Use comma-separated numbers (e.g., 0,1,2,1,0)")
                
        except ValueError as e:
            raise ValueError(f"Invalid numeric value: {e}")
        
        return settings
    
    def process_reverse(self):
        """Process the reverse operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('reverse', settings)
            else:
                messagebox.showinfo("Reverse", f"Reverse settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Reverse failed: {e}")
    
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
        """Auto-load GIF for reverse operations."""
        # For now, just store the path - the actual loading will be done during processing
        self.current_gif_path = gif_path
        self.status_label.config(text=f"GIF loaded: {Path(gif_path).name}")
