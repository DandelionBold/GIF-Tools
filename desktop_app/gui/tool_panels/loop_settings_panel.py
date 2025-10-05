"""
Loop Settings Tool Panel

GUI panel for the GIF loop settings tool with intuitive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.loop_settings import set_gif_loop_count


class LoopSettingsPanel:
    """Panel for GIF loop settings operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the loop settings panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.current_gif_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the loop settings panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Loop Settings", padding="10")
        
        # Description
        desc_text = "Control how your GIF animation loops. Set infinite loops, specific loop counts, or play once."
        ttk.Label(self.frame, text=desc_text, wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Loop behavior selection
        ttk.Label(self.frame, text="Loop Behavior:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        self.loop_behavior_var = tk.StringVar(value="infinite")
        behavior_frame = ttk.Frame(self.frame)
        behavior_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        behavior_options = [
            ("Infinite Loop (0)", "infinite"),
            ("Play Once (1)", "once"),
            ("Play Twice (2)", "twice"),
            ("Custom Count", "custom"),
        ]
        
        for i, (text, value) in enumerate(behavior_options):
            ttk.Radiobutton(
                behavior_frame,
                text=text,
                variable=self.loop_behavior_var,
                value=value,
                command=self.update_controls
            ).grid(row=0, column=i, padx=(0, 20), sticky=tk.W)
        
        # Custom loop count controls
        self.custom_frame = ttk.LabelFrame(self.frame, text="Custom Loop Count", padding="10")
        self.custom_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.custom_frame, text="Loop Count:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.custom_count_var = tk.IntVar(value=3)
        ttk.Spinbox(
            self.custom_frame,
            from_=1,
            to=1000,
            textvariable=self.custom_count_var,
            width=10
        ).grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        ttk.Label(self.custom_frame, text="(1-1000 times)", foreground="gray").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Loop information display
        self.info_frame = ttk.LabelFrame(self.frame, text="Current Loop Settings", padding="10")
        self.info_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.current_loop_label = ttk.Label(self.info_frame, text="No GIF loaded", foreground="gray")
        self.current_loop_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Output settings
        self.output_frame = ttk.LabelFrame(self.frame, text="Output Settings", padding="10")
        self.output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Quality
        ttk.Label(self.output_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.DoubleVar(value=85)
        quality_scale = ttk.Scale(
            self.output_frame,
            from_=1,
            to=100,
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_quality_label
        )
        quality_scale.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.quality_label = ttk.Label(self.output_frame, text="85")
        self.quality_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Quick presets
        self.presets_frame = ttk.LabelFrame(self.frame, text="Quick Presets", padding="10")
        self.presets_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        presets = [
            ("Infinite", "infinite"),
            ("Once", "once"),
            ("Twice", "twice"),
            ("5 Times", "custom_5"),
            ("10 Times", "custom_10"),
        ]
        
        for i, (text, value) in enumerate(presets):
            btn = ttk.Button(
                self.presets_frame,
                text=text,
                command=lambda v=value: self.apply_preset(v),
                width=12
            )
            btn.grid(row=0, column=i, padx=5, pady=5, sticky=tk.W)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame,
            text="🔄 Apply Loop Settings",
            command=self.process_loop_settings
        )
        self.progress_bar = ttk.Progressbar(
            self.frame,
            mode='indeterminate'
        )
        self.process_btn.grid(row=6, column=0, columnspan=3, pady=10)
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="No GIF loaded", foreground="gray")
        self.status_label.grid(row=8, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
        
        # Initialize controls visibility
        self.update_controls()
    
    def update_controls(self):
        """Update control visibility based on selected behavior."""
        behavior = self.loop_behavior_var.get()
        
        # Show/hide custom controls
        if behavior == "custom":
            self.custom_frame.grid()
        else:
            self.custom_frame.grid_remove()
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def apply_preset(self, preset_value):
        """Apply a preset loop setting."""
        if preset_value == "infinite":
            self.loop_behavior_var.set("infinite")
        elif preset_value == "once":
            self.loop_behavior_var.set("once")
        elif preset_value == "twice":
            self.loop_behavior_var.set("twice")
        elif preset_value == "custom_5":
            self.loop_behavior_var.set("custom")
            self.custom_count_var.set(5)
        elif preset_value == "custom_10":
            self.loop_behavior_var.set("custom")
            self.custom_count_var.set(10)
        
        self.update_controls()
    
    def get_settings(self) -> dict:
        """Get current loop settings settings."""
        if not self.current_gif_path:
            raise ValueError("No GIF file loaded")
        
        behavior = self.loop_behavior_var.get()
        
        # Determine loop count based on behavior
        if behavior == "infinite":
            loop_count = 0
        elif behavior == "once":
            loop_count = 1
        elif behavior == "twice":
            loop_count = 2
        elif behavior == "custom":
            loop_count = self.custom_count_var.get()
            if loop_count < 1 or loop_count > 1000:
                raise ValueError("Custom loop count must be between 1 and 1000")
        else:
            raise ValueError("Invalid loop behavior")
        
        settings = {
            'input_path': self.current_gif_path,
            'loop_count': loop_count,
            'quality': int(self.quality_var.get()),
        }
        
        return settings
    
    def process_loop_settings(self):
        """Process the loop settings operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('loop_settings', settings)
            else:
                messagebox.showinfo("Loop Settings", f"Loop settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Loop settings failed: {e}")
    
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
        """Auto-load GIF for loop settings."""
        # Store the path and update status
        self.current_gif_path = gif_path
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"GIF loaded: {Path(gif_path).name}")
        
        # Try to read current loop count from GIF
        try:
            from PIL import Image
            with Image.open(gif_path) as gif:
                # Get loop count from GIF info
                loop_count = gif.info.get('loop', 0)
                if loop_count == 0:
                    loop_text = "Infinite loop"
                elif loop_count == 1:
                    loop_text = "Plays once"
                elif loop_count == 2:
                    loop_text = "Plays twice"
                else:
                    loop_text = f"Plays {loop_count} times"
                
                if hasattr(self, 'current_loop_label'):
                    self.current_loop_label.config(text=f"Current: {loop_text}")
                    
        except Exception:
            # If we can't read the loop count, just show that it's loaded
            if hasattr(self, 'current_loop_label'):
                self.current_loop_label.config(text="GIF loaded (loop info unavailable)")
