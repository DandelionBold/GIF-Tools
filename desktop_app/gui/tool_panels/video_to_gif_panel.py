"""
Video to GIF tool panel.

This module provides a GUI panel for converting video files to animated GIFs
with customizable settings for quality, frame rate, duration, and resolution.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Callable, Optional

from gif_tools.core import convert_video_to_gif


class VideoToGifPanel:
    """Video to GIF conversion panel."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """Initialize the video to GIF panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        
        # Video file path
        self.video_path: Optional[Path] = None
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def get_widget(self) -> tk.Widget:
        """Get the main widget."""
        return self.frame
    
    def _create_widgets(self):
        """Create the panel widgets."""
        # Title
        title_label = ttk.Label(self.frame, text="Video to GIF Converter", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Instructions
        instructions = ttk.Label(self.frame, 
                               text="Select a video file and configure settings to convert it to an animated GIF.",
                               font=("Arial", 9), foreground="gray")
        instructions.grid(row=1, column=0, columnspan=3, pady=(0, 15))
        
        # Video file selection
        file_frame = ttk.LabelFrame(self.frame, text="Video File", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, state="readonly", width=50)
        file_entry.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_video).grid(row=0, column=2)
        
        # Video info
        self.info_label = ttk.Label(file_frame, text="No video selected", 
                                  font=("Arial", 9), foreground="gray")
        self.info_label.grid(row=1, column=0, columnspan=3, pady=(5, 0))
        
        # Settings
        settings_frame = ttk.LabelFrame(self.frame, text="Conversion Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # FPS setting
        ttk.Label(settings_frame, text="FPS:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.fps_var = tk.IntVar(value=10)
        fps_spinbox = ttk.Spinbox(settings_frame, from_=1, to=30, textvariable=self.fps_var, width=10)
        fps_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(5, 20), pady=2)
        
        # Duration setting
        ttk.Label(settings_frame, text="Duration (seconds):").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.duration_var = tk.StringVar(value="")
        duration_entry = ttk.Entry(settings_frame, textvariable=self.duration_var, width=10)
        duration_entry.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(settings_frame, text="(Leave empty for full video)", 
                 font=("Arial", 8), foreground="gray").grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=(5, 0))
        
        # Start time setting
        ttk.Label(settings_frame, text="Start time (seconds):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.start_time_var = tk.DoubleVar(value=0.0)
        start_time_spinbox = ttk.Spinbox(settings_frame, from_=0.0, to=3600.0, increment=0.1, 
                                       textvariable=self.start_time_var, width=10)
        start_time_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(5, 20), pady=2)
        
        # Quality setting
        ttk.Label(settings_frame, text="Quality:").grid(row=2, column=2, sticky=tk.W, pady=2)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(settings_frame, from_=1, to=100, variable=self.quality_var, 
                                 orient=tk.HORIZONTAL, length=150)
        quality_scale.grid(row=2, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        
        self.quality_label = ttk.Label(settings_frame, text="85")
        self.quality_label.grid(row=3, column=3, sticky=tk.W, padx=(5, 0))
        
        quality_scale.configure(command=self.update_quality_label)
        
        # Resolution settings
        resolution_frame = ttk.Frame(settings_frame)
        resolution_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(resolution_frame, text="Resolution:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Width
        ttk.Label(resolution_frame, text="Width:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5), pady=2)
        self.width_var = tk.StringVar(value="")
        width_entry = ttk.Entry(resolution_frame, textvariable=self.width_var, width=8)
        width_entry.grid(row=0, column=2, sticky=tk.W, pady=2)
        
        # Height
        ttk.Label(resolution_frame, text="Height:").grid(row=0, column=3, sticky=tk.W, padx=(20, 5), pady=2)
        self.height_var = tk.StringVar(value="")
        height_entry = ttk.Entry(resolution_frame, textvariable=self.height_var, width=8)
        height_entry.grid(row=0, column=4, sticky=tk.W, pady=2)
        
        ttk.Label(resolution_frame, text="(Leave empty to keep original)", 
                 font=("Arial", 8), foreground="gray").grid(row=1, column=0, columnspan=5, sticky=tk.W, pady=(2, 0))
        
        # Advanced settings
        advanced_frame = ttk.LabelFrame(self.frame, text="Advanced Settings", padding="10")
        advanced_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Loop count
        ttk.Label(advanced_frame, text="Loop count:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.loop_var = tk.IntVar(value=0)
        loop_spinbox = ttk.Spinbox(advanced_frame, from_=0, to=100, textvariable=self.loop_var, width=10)
        loop_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(5, 20), pady=2)
        
        ttk.Label(advanced_frame, text="(0 = infinite loop)", 
                 font=("Arial", 8), foreground="gray").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=(5, 0))
        
        # Auto-optimize for large files
        self.auto_optimize_var = tk.BooleanVar(value=True)
        auto_optimize_check = ttk.Checkbutton(advanced_frame, text="Auto-optimize for large files", 
                                            variable=self.auto_optimize_var)
        auto_optimize_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Label(advanced_frame, text="(Automatically reduces resolution/quality for files >100MB)", 
                 font=("Arial", 8), foreground="gray").grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=(5, 0))
        
        # Optimize checkbox
        self.optimize_var = tk.BooleanVar(value=True)
        optimize_check = ttk.Checkbutton(advanced_frame, text="Optimize GIF", 
                                       variable=self.optimize_var)
        optimize_check.grid(row=4, column=0, sticky=tk.W, pady=2)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Convert to GIF", 
            command=self.process_conversion,
            state=tk.DISABLED
        )
        self.process_btn.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(0, weight=1)
        file_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(3, weight=1)
    
    def browse_video(self):
        """Browse for video file."""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.webm"),
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("MOV files", "*.mov"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.video_path = Path(file_path)
            self.file_var.set(str(self.video_path))
            self.info_label.config(text=f"Selected: {self.video_path.name}")
            self.process_btn.config(state=tk.NORMAL)
            
            # Try to get video info
            try:
                from moviepy import VideoFileClip
                with VideoFileClip(str(self.video_path)) as clip:
                    duration = clip.duration
                    fps = clip.fps
                    size = clip.size
                    self.info_label.config(
                        text=f"Selected: {self.video_path.name} | "
                             f"Duration: {duration:.1f}s | FPS: {fps:.1f} | Size: {size[0]}x{size[1]}"
                    )
            except Exception as e:
                self.info_label.config(text=f"Selected: {self.video_path.name} (Could not read video info)")
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def _calculate_auto_optimization(self, video_path: Path) -> dict:
        """Calculate optimal settings for large video files."""
        try:
            from moviepy import VideoFileClip
            with VideoFileClip(str(video_path)) as clip:
                duration = clip.duration
                fps = clip.fps
                size = clip.size
                
                # Calculate file size in MB
                file_size_mb = video_path.stat().st_size / (1024 * 1024)
                
                # If file is larger than 100MB, apply auto-optimization
                if file_size_mb > 100 and self.auto_optimize_var.get():
                    # Calculate optimal settings
                    target_size_ratio = min(0.5, 100 / file_size_mb)  # Target 50% reduction or 100MB
                    
                    # Reduce resolution
                    new_width = max(320, int(size[0] * (target_size_ratio ** 0.5)))
                    new_height = max(240, int(size[1] * (target_size_ratio ** 0.5)))
                    
                    # Reduce FPS for very large files
                    optimal_fps = min(self.fps_var.get(), max(5, int(fps * 0.7)))
                    
                    # Reduce quality
                    optimal_quality = max(60, int(self.quality_var.get() * 0.8))
                    
                    # Reduce duration for extremely large files
                    optimal_duration = None
                    if file_size_mb > 500:  # For files > 500MB
                        optimal_duration = min(30, duration * 0.3)  # Max 30 seconds or 30% of original
                    elif file_size_mb > 200:  # For files > 200MB
                        optimal_duration = min(60, duration * 0.5)  # Max 60 seconds or 50% of original
                    
                    return {
                        'width': new_width,
                        'height': new_height,
                        'fps': optimal_fps,
                        'quality': optimal_quality,
                        'duration': optimal_duration,
                        'auto_applied': True,
                        'original_size_mb': file_size_mb
                    }
                
                return {'auto_applied': False, 'original_size_mb': file_size_mb}
                
        except Exception as e:
            return {'auto_applied': False, 'error': str(e)}
    
    def get_settings(self) -> dict:
        """Get current conversion settings."""
        settings = {
            'fps': self.fps_var.get(),
            'start_time': self.start_time_var.get(),
            'quality': self.quality_var.get(),
            'loop_count': self.loop_var.get(),
            'optimize': self.optimize_var.get(),
            'auto_optimize': self.auto_optimize_var.get()
        }
        
        # Duration
        duration_text = self.duration_var.get().strip()
        if duration_text:
            try:
                settings['duration'] = float(duration_text)
            except ValueError:
                settings['duration'] = None
        else:
            settings['duration'] = None
        
        # Resolution
        width_text = self.width_var.get().strip()
        height_text = self.height_var.get().strip()
        
        if width_text:
            try:
                settings['width'] = int(width_text)
            except ValueError:
                settings['width'] = None
        else:
            settings['width'] = None
            
        if height_text:
            try:
                settings['height'] = int(height_text)
            except ValueError:
                settings['height'] = None
        else:
            settings['height'] = None
        
        return settings
    
    def process_conversion(self):
        """Process the video to GIF conversion."""
        try:
            if not self.video_path:
                messagebox.showwarning("Warning", "Please select a video file first!")
                return
            
            settings = self.get_settings()
            
            # Apply auto-optimization if enabled
            auto_optimization = self._calculate_auto_optimization(self.video_path)
            
            if auto_optimization.get('auto_applied', False):
                # Show optimization dialog
                original_size = auto_optimization['original_size_mb']
                new_width = auto_optimization['width']
                new_height = auto_optimization['height']
                new_fps = auto_optimization['fps']
                new_quality = auto_optimization['quality']
                new_duration = auto_optimization.get('duration')
                
                duration_text = f"Duration: {new_duration:.1f}s" if new_duration else "Duration: Full video"
                
                result = messagebox.askyesno(
                    "Auto-Optimization Applied",
                    f"Your video file is {original_size:.1f}MB (larger than 100MB limit).\n\n"
                    f"Auto-optimization will be applied:\n"
                    f"• Resolution: {new_width}x{new_height}\n"
                    f"• FPS: {new_fps}\n"
                    f"• Quality: {new_quality}\n"
                    f"• {duration_text}\n\n"
                    f"Do you want to continue with these optimized settings?",
                    icon='question'
                )
                
                if not result:
                    return
                
                # Apply auto-optimization settings
                settings.update({
                    'width': new_width,
                    'height': new_height,
                    'fps': new_fps,
                    'quality': new_quality
                })
                
                if new_duration:
                    settings['duration'] = new_duration
            
            if self.on_process:
                self.on_process('video_to_gif', settings, str(self.video_path))
            else:
                messagebox.showinfo("Video to GIF", f"Conversion settings: {settings}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")