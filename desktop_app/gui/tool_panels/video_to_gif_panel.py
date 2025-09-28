"""
Video to GIF Tool Panel

GUI panel for the video to GIF conversion tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.video_to_gif import convert_video_to_gif


class VideoToGifPanel:
    """Panel for video to GIF conversion operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the video to GIF panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.setup_ui()
    
    def setup_ui(self):
        """Create the video to GIF panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Video to GIF Conversion", padding="10")
        
        # Video file selection
        ttk.Label(self.frame, text="Video File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.video_file_var = tk.StringVar()
        video_frame = ttk.Frame(self.frame)
        video_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        video_entry = ttk.Entry(video_frame, textvariable=self.video_file_var, width=40)
        video_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(video_frame, text="Browse", command=self.browse_video_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Duration controls
        ttk.Label(self.frame, text="Duration (seconds):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.StringVar(value="5")
        duration_entry = ttk.Entry(self.frame, textvariable=self.duration_var, width=10)
        duration_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Start time
        ttk.Label(self.frame, text="Start Time (seconds):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.start_time_var = tk.StringVar(value="0")
        start_entry = ttk.Entry(self.frame, textvariable=self.start_time_var, width=10)
        start_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Frame rate
        ttk.Label(self.frame, text="Frame Rate (fps):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.fps_var = tk.StringVar(value="10")
        fps_entry = ttk.Entry(self.frame, textvariable=self.fps_var, width=10)
        fps_entry.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Size controls
        ttk.Label(self.frame, text="Size:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Width
        ttk.Label(self.frame, text="Width:").grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.width_var = tk.StringVar(value="320")
        width_entry = ttk.Entry(self.frame, textvariable=self.width_var, width=8)
        width_entry.grid(row=4, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Height
        ttk.Label(self.frame, text="Height:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Label(self.frame, text="Height:").grid(row=5, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.height_var = tk.StringVar(value="240")
        height_entry = ttk.Entry(self.frame, textvariable=self.height_var, width=8)
        height_entry.grid(row=5, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Maintain aspect ratio
        self.maintain_aspect_var = tk.BooleanVar(value=True)
        aspect_check = ttk.Checkbutton(
            self.frame, 
            text="Maintain aspect ratio", 
            variable=self.maintain_aspect_var
        )
        aspect_check.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=5)
        
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
        
        # Loop settings
        ttk.Label(self.frame, text="Loop Count:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.loop_var = tk.StringVar(value="0")
        loop_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.loop_var,
            values=["0 (infinite)", "1", "2", "3", "5", "10"],
            state="readonly",
            width=15
        )
        loop_combo.grid(row=8, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Optimization
        self.optimize_var = tk.BooleanVar(value=True)
        optimize_check = ttk.Checkbutton(
            self.frame, 
            text="Optimize GIF", 
            variable=self.optimize_var
        )
        optimize_check.grid(row=9, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Convert Video to GIF", 
            command=self.process_conversion
        )
        self.process_btn.grid(row=10, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
    
    def browse_video_file(self):
        """Browse for video file."""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv"),
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.video_file_var.set(file_path)
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current conversion settings."""
        try:
            duration = float(self.duration_var.get())
            start_time = float(self.start_time_var.get())
            fps = int(self.fps_var.get())
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            quality = self.quality_var.get()
            
            # Parse loop count
            loop_text = self.loop_var.get()
            if loop_text.startswith("0"):
                loop_count = 0
            else:
                loop_count = int(loop_text)
                
        except ValueError as e:
            raise ValueError(f"Invalid numeric value: {e}")
        
        return {
            'duration': duration,
            'start_time': start_time,
            'fps': fps,
            'width': width,
            'height': height,
            'maintain_aspect': self.maintain_aspect_var.get(),
            'quality': quality,
            'loop_count': loop_count,
            'optimize': self.optimize_var.get()
        }
    
    def process_conversion(self):
        """Process the video to GIF conversion."""
        try:
            video_file = self.video_file_var.get()
            if not video_file:
                messagebox.showerror("Error", "Please select a video file!")
                return
            
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('video_to_gif', settings, video_file)
            else:
                messagebox.showinfo("Video to GIF", f"Conversion settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")
    
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
