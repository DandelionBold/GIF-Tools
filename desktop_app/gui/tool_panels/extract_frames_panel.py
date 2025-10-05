"""
Extract Frames Tool Panel

GUI panel for the GIF extract frames tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.extract_frames import extract_gif_frames


class ExtractFramesPanel:
    """Panel for GIF frame extraction operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the extract frames panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.current_gif_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the extract frames panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Extract Frames", padding="10")
        
        # Description
        desc_text = "Extract specific frames from your GIF and save them as static images. Choose which frames to extract and in what format."
        ttk.Label(self.frame, text=desc_text, wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Frame selection method
        ttk.Label(self.frame, text="Frame Selection:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        self.selection_method_var = tk.StringVar(value="all")
        method_frame = ttk.Frame(self.frame)
        method_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        method_options = [
            ("Extract All Frames", "all"),
            ("Extract Specific Frames", "specific"),
            ("Extract Range", "range"),
            ("Extract Every Nth Frame", "interval"),
        ]
        
        for i, (text, value) in enumerate(method_options):
            ttk.Radiobutton(
                method_frame,
                text=text,
                variable=self.selection_method_var,
                value=value,
                command=self.update_controls
            ).grid(row=0, column=i, padx=(0, 20), sticky=tk.W)
        
        # Specific frames controls
        self.specific_frame = ttk.LabelFrame(self.frame, text="Specific Frames", padding="10")
        self.specific_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.specific_frame, text="Frame Numbers:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.specific_frames_var = tk.StringVar(value="1,5,10,15")
        ttk.Entry(
            self.specific_frame,
            textvariable=self.specific_frames_var,
            width=30
        ).grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        ttk.Label(self.specific_frame, text="(e.g., 1,5,10,15 or 1-5,10-15)", foreground="gray").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Range controls
        self.range_frame = ttk.LabelFrame(self.frame, text="Frame Range", padding="10")
        self.range_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.range_frame, text="From Frame:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.range_start_var = tk.IntVar(value=1)
        ttk.Spinbox(
            self.range_frame,
            from_=1,
            to=1000,
            textvariable=self.range_start_var,
            width=10
        ).grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        ttk.Label(self.range_frame, text="To Frame:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.range_end_var = tk.IntVar(value=10)
        ttk.Spinbox(
            self.range_frame,
            from_=1,
            to=1000,
            textvariable=self.range_end_var,
            width=10
        ).grid(row=0, column=3, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Interval controls
        self.interval_frame = ttk.LabelFrame(self.frame, text="Extract Every Nth Frame", padding="10")
        self.interval_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.interval_frame, text="Extract every:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.IntVar(value=2)
        ttk.Spinbox(
            self.interval_frame,
            from_=1,
            to=100,
            textvariable=self.interval_var,
            width=10
        ).grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        ttk.Label(self.interval_frame, text="frames (e.g., 2 = every 2nd frame)", foreground="gray").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Output settings
        self.output_frame = ttk.LabelFrame(self.frame, text="Output Settings", padding="10")
        self.output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Output directory
        ttk.Label(self.output_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar(value="frames_output")
        ttk.Entry(
            self.output_frame,
            textvariable=self.output_dir_var,
            width=30
        ).grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        ttk.Button(
            self.output_frame,
            text="Browse",
            command=self.browse_output_dir,
            width=10
        ).grid(row=0, column=2, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Output format
        ttk.Label(self.output_frame, text="Output Format:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_format_var = tk.StringVar(value="PNG")
        format_combo = ttk.Combobox(
            self.output_frame,
            textvariable=self.output_format_var,
            values=["PNG", "JPEG", "BMP", "TIFF", "WEBP"],
            state="readonly",
            width=15
        )
        format_combo.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Quality (for lossy formats)
        ttk.Label(self.output_frame, text="Quality:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.DoubleVar(value=95)
        quality_scale = ttk.Scale(
            self.output_frame,
            from_=1,
            to=100,
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_quality_label
        )
        quality_scale.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.quality_label = ttk.Label(self.output_frame, text="95")
        self.quality_label.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Filename prefix
        ttk.Label(self.output_frame, text="Filename Prefix:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.prefix_var = tk.StringVar(value="frame")
        ttk.Entry(
            self.output_frame,
            textvariable=self.prefix_var,
            width=20
        ).grid(row=4, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        ttk.Label(self.output_frame, text="(e.g., 'frame' → frame_001.png)", foreground="gray").grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame,
            text="🎬 Extract Frames",
            command=self.process_extract_frames
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
        """Update control visibility based on selected method."""
        method = self.selection_method_var.get()
        
        # Show/hide frames based on method
        if method == "specific":
            self.specific_frame.grid()
            self.range_frame.grid_remove()
            self.interval_frame.grid_remove()
        elif method == "range":
            self.specific_frame.grid_remove()
            self.range_frame.grid()
            self.interval_frame.grid_remove()
        elif method == "interval":
            self.specific_frame.grid_remove()
            self.range_frame.grid_remove()
            self.interval_frame.grid()
        else:  # all
            self.specific_frame.grid_remove()
            self.range_frame.grid_remove()
            self.interval_frame.grid_remove()
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get()
        )
        if directory:
            self.output_dir_var.set(directory)
    
    def get_settings(self) -> dict:
        """Get current extract frames settings."""
        if not self.current_gif_path:
            raise ValueError("No GIF file loaded")
        
        method = self.selection_method_var.get()
        
        settings = {
            'input_path': self.current_gif_path,
            'output_dir': self.output_dir_var.get(),
            'output_format': self.output_format_var.get(),
            'quality': int(self.quality_var.get()),
            'prefix': self.prefix_var.get(),
            'method': method,
        }
        
        if method == "specific":
            # Parse specific frame numbers
            frames_text = self.specific_frames_var.get()
            try:
                frame_indices = self._parse_frame_numbers(frames_text)
                settings['frame_indices'] = frame_indices
            except ValueError as e:
                raise ValueError(f"Invalid frame numbers: {e}")
        elif method == "range":
            start = self.range_start_var.get()
            end = self.range_end_var.get()
            if start > end:
                raise ValueError("Start frame must be less than or equal to end frame")
            settings['frame_range'] = (start, end)
        elif method == "interval":
            interval = self.interval_var.get()
            if interval < 1:
                raise ValueError("Interval must be at least 1")
            settings['interval'] = interval
        
        return settings
    
    def _parse_frame_numbers(self, frames_text: str) -> list:
        """Parse frame numbers from text input."""
        frame_indices = []
        parts = frames_text.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Handle ranges like "1-5"
                start, end = part.split('-', 1)
                start, end = int(start.strip()), int(end.strip())
                frame_indices.extend(range(start, end + 1))
            else:
                # Handle single numbers
                frame_indices.append(int(part))
        
        # Convert to 0-based indices and remove duplicates
        frame_indices = list(set([idx - 1 for idx in frame_indices if idx > 0]))
        frame_indices.sort()
        
        return frame_indices
    
    def process_extract_frames(self):
        """Process the extract frames operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('extract_frames', settings)
            else:
                messagebox.showinfo("Extract Frames", f"Extract frames settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Extract frames failed: {e}")
    
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
        """Auto-load GIF for frame extraction."""
        # Store the path and update status
        self.current_gif_path = gif_path
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"GIF loaded: {Path(gif_path).name}")
