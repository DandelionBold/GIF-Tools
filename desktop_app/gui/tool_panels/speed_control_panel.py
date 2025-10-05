"""
Speed Control Tool Panel

GUI panel for the GIF speed control tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.speed_control import change_gif_speed


class SpeedControlPanel:
    """Panel for GIF speed control operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the speed control panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.current_gif_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the speed control panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Speed Control", padding="10")
        
        # Description
        desc_text = "Adjust the playback speed of your GIF animation. Make it faster or slower by changing the speed multiplier."
        ttk.Label(self.frame, text=desc_text, wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Speed control method
        ttk.Label(self.frame, text="Speed Control Method:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        self.speed_method_var = tk.StringVar(value="multiplier")
        method_frame = ttk.Frame(self.frame)
        method_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        method_options = [
            ("Speed Multiplier", "multiplier"),
            ("Preset Speeds", "preset"),
            ("Custom Duration", "duration"),
        ]
        
        for i, (text, value) in enumerate(method_options):
            ttk.Radiobutton(
                method_frame,
                text=text,
                variable=self.speed_method_var,
                value=value,
                command=self.update_controls
            ).grid(row=0, column=i, padx=(0, 20), sticky=tk.W)
        
        # Speed multiplier controls
        self.multiplier_frame = ttk.LabelFrame(self.frame, text="Speed Multiplier", padding="10")
        self.multiplier_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Speed multiplier slider
        ttk.Label(self.multiplier_frame, text="Speed Multiplier:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(
            self.multiplier_frame,
            from_=0.25,
            to=2.0,
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            length=300,
            command=self.update_speed_label
        )
        speed_scale.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.speed_label = ttk.Label(self.multiplier_frame, text="1.0x (Normal Speed)")
        self.speed_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Speed presets
        ttk.Label(self.multiplier_frame, text="Quick Presets:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        preset_frame = ttk.Frame(self.multiplier_frame)
        preset_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        presets = [
            ("0.25x (Very Slow)", 0.25),
            ("0.5x (Half Speed)", 0.5),
            ("1.0x (Normal)", 1.0),
            ("2.0x (Double Speed)", 2.0),
        ]
        
        for i, (text, value) in enumerate(presets):
            ttk.Button(
                preset_frame,
                text=text,
                width=15,
                command=lambda v=value: self.set_speed_preset(v)
            ).grid(row=0, column=i, padx=(0, 5), pady=2)
        
        # Preset speeds controls
        self.preset_frame = ttk.LabelFrame(self.frame, text="Preset Speeds", padding="10")
        self.preset_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.preset_frame, text="Select Speed Preset:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.preset_var = tk.StringVar(value="slow")
        preset_combo = ttk.Combobox(
            self.preset_frame,
            textvariable=self.preset_var,
            values=[
                "slow", "normal", "fast", "very_fast", "ultra_fast",
                "very_slow", "half_speed", "double_speed", "triple_speed"
            ],
            state="readonly",
            width=15
        )
        preset_combo.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Custom duration controls
        self.duration_frame = ttk.LabelFrame(self.frame, text="Custom Duration", padding="10")
        self.duration_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.duration_frame, text="Frame Duration (ms):").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.duration_var = tk.IntVar(value=100)
        duration_spin = ttk.Spinbox(
            self.duration_frame,
            from_=10,
            to=2000,
            textvariable=self.duration_var,
            width=10
        )
        duration_spin.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        ttk.Label(self.duration_frame, text="(10-2000 milliseconds)").grid(row=0, column=2, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Advanced options
        self.advanced_frame = ttk.LabelFrame(self.frame, text="Advanced Options", padding="10")
        self.advanced_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Quality control
        ttk.Label(self.advanced_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.quality_var = tk.DoubleVar(value=85)
        quality_scale = ttk.Scale(
            self.advanced_frame,
            from_=1,
            to=100,
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_quality_label
        )
        quality_scale.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.quality_label = ttk.Label(self.advanced_frame, text="85")
        self.quality_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame,
            text="🚀 Change Speed",
            command=self.process_speed_control
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
        self.multiplier_frame.grid_columnconfigure(1, weight=1)
        
        # Initialize controls visibility
        self.update_controls()
    
    def update_controls(self):
        """Update control visibility based on selected method."""
        method = self.speed_method_var.get()
        
        # Show/hide frames based on method
        if method == "multiplier":
            self.multiplier_frame.grid()
            self.preset_frame.grid_remove()
            self.duration_frame.grid_remove()
        elif method == "preset":
            self.multiplier_frame.grid_remove()
            self.preset_frame.grid()
            self.duration_frame.grid_remove()
        elif method == "duration":
            self.multiplier_frame.grid_remove()
            self.preset_frame.grid_remove()
            self.duration_frame.grid()
    
    def update_speed_label(self, value):
        """Update the speed label when scale changes."""
        speed = float(value)
        if speed < 0.5:
            label = f"{speed:.2f}x (Very Slow)"
        elif speed < 1.0:
            label = f"{speed:.2f}x (Slow)"
        elif speed == 1.0:
            label = f"{speed:.2f}x (Normal Speed)"
        else:
            label = f"{speed:.2f}x (Fast)"
        
        self.speed_label.config(text=label)
    
    def set_speed_preset(self, multiplier):
        """Set speed from preset button."""
        self.speed_var.set(multiplier)
        self.update_speed_label(multiplier)
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current speed control settings."""
        if not self.current_gif_path:
            raise ValueError("No GIF file loaded")
            
        method = self.speed_method_var.get()
        
        settings = {
            'input_path': self.current_gif_path,
            'method': method,
            'quality': int(self.quality_var.get()),
        }
        
        if method == "multiplier":
            settings['multiplier'] = self.speed_var.get()
        elif method == "preset":
            # Map preset names to multipliers
            preset_multipliers = {
                "very_slow": 0.25,
                "slow": 0.5,
                "normal": 1.0,
                "fast": 2.0,
                "half_speed": 0.5,
                "double_speed": 2.0,
            }
            settings['multiplier'] = preset_multipliers.get(self.preset_var.get(), 1.0)
        elif method == "duration":
            settings['target_duration'] = self.duration_var.get() / 1000.0  # Convert to seconds
        
        return settings
    
    def process_speed_control(self):
        """Process the speed control operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('speed_control', settings)
            else:
                messagebox.showinfo("Speed Control", f"Speed control settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Speed control failed: {e}")
    
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
        """Auto-load GIF for speed control."""
        # Store the path and update status
        self.current_gif_path = gif_path
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"GIF loaded: {Path(gif_path).name}")
