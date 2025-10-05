"""
Format Conversion Tool Panel

GUI panel for the GIF format conversion tool with format selection and quality controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.format_conversion import convert_gif_format


class FormatConversionPanel:
    """Panel for GIF format conversion operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the format conversion panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.current_gif_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the format conversion panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Format Conversion", padding="10")
        
        # Description
        desc_text = "Convert your GIF to different animated formats. Choose the target format and adjust quality settings."
        ttk.Label(self.frame, text=desc_text, wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Current format info
        self.current_info_frame = ttk.LabelFrame(self.frame, text="Current Format", padding="10")
        self.current_info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.current_format_label = ttk.Label(self.current_info_frame, text="No GIF loaded", foreground="gray")
        self.current_format_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Target format selection
        ttk.Label(self.frame, text="Target Format:").grid(row=2, column=0, sticky=tk.W, pady=10)
        
        self.target_format_var = tk.StringVar(value="WebP")
        format_frame = ttk.Frame(self.frame)
        format_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Format buttons
        formats = [
            ("GIF", "GIF", "Standard GIF format"),
            ("WebP", "WebP", "Modern format, smaller file size"),
            ("APNG", "APNG", "Animated PNG, better quality"),
        ]
        
        for i, (text, value, description) in enumerate(formats):
            btn = ttk.Radiobutton(
                format_frame,
                text=f"{text} - {description}",
                variable=self.target_format_var,
                value=value,
                command=self.update_controls
            )
            btn.grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # Format-specific settings
        self.settings_frame = ttk.LabelFrame(self.frame, text="Format Settings", padding="10")
        self.settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Quality setting
        ttk.Label(self.settings_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.DoubleVar(value=85)
        quality_scale = ttk.Scale(
            self.settings_frame,
            from_=1,
            to=100,
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_quality_label
        )
        quality_scale.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.quality_label = ttk.Label(self.settings_frame, text="85")
        self.quality_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Lossless option
        self.lossless_var = tk.BooleanVar(value=False)
        self.lossless_check = ttk.Checkbutton(
            self.settings_frame,
            text="Lossless compression (larger file, better quality)",
            variable=self.lossless_var,
            command=self.update_controls
        )
        self.lossless_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # WebP specific settings
        self.webp_frame = ttk.LabelFrame(self.frame, text="WebP Settings", padding="10")
        self.webp_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # WebP method
        ttk.Label(self.webp_frame, text="Compression Method:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.webp_method_var = tk.StringVar(value="auto")
        webp_method_combo = ttk.Combobox(
            self.webp_frame,
            textvariable=self.webp_method_var,
            values=["auto", "fast", "best"],
            state="readonly",
            width=15
        )
        webp_method_combo.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        # WebP effort
        ttk.Label(self.webp_frame, text="Compression Effort:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.webp_effort_var = tk.IntVar(value=4)
        webp_effort_scale = ttk.Scale(
            self.webp_frame,
            from_=1,
            to=6,
            variable=self.webp_effort_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_webp_effort_label
        )
        webp_effort_scale.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.webp_effort_label = ttk.Label(self.webp_frame, text="4 (Balanced)")
        self.webp_effort_label.grid(row=2, column=0, columnspan=3, pady=5)
        
        # Format comparison info
        self.comparison_frame = ttk.LabelFrame(self.frame, text="Format Comparison", padding="10")
        self.comparison_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        comparison_text = """Format Comparison:
• GIF: Universal support, larger files, limited colors
• WebP: Modern format, 25-35% smaller than GIF, good browser support
• APNG: PNG-based, better quality than GIF, limited browser support"""
        
        ttk.Label(self.comparison_frame, text=comparison_text, justify=tk.LEFT, foreground="gray").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame,
            text="🔄 Convert Format",
            command=self.process_format_conversion
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
        """Update control visibility based on selected format."""
        format_type = self.target_format_var.get()
        lossless = self.lossless_var.get()
        
        # Show/hide WebP specific controls
        if format_type == "WebP":
            self.webp_frame.grid()
        else:
            self.webp_frame.grid_remove()
        
        # Update quality control visibility
        if lossless and format_type in ["WebP", "APNG"]:
            # Hide quality for lossless formats
            self.settings_frame.grid_remove()
        else:
            self.settings_frame.grid()
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def update_webp_effort_label(self, value):
        """Update the WebP effort label when scale changes."""
        effort = int(float(value))
        effort_descriptions = {
            1: "1 (Fastest)",
            2: "2 (Very Fast)", 
            3: "3 (Fast)",
            4: "4 (Balanced)",
            5: "5 (Slow)",
            6: "6 (Slowest)"
        }
        self.webp_effort_label.config(text=f"{effort} ({effort_descriptions[effort]})")
    
    def get_settings(self) -> dict:
        """Get current format conversion settings."""
        if not self.current_gif_path:
            raise ValueError("No GIF file loaded")
        
        format_type = self.target_format_var.get()
        lossless = self.lossless_var.get()
        
        settings = {
            'input_path': self.current_gif_path,
            'target_format': format_type,
            'quality': int(self.quality_var.get()) if not lossless else 100,
            'lossless': lossless,
        }
        
        # Add format-specific settings
        if format_type == "WebP":
            settings.update({
                'method': self.webp_method_var.get(),
                'effort': int(self.webp_effort_var.get()),
            })
        
        return settings
    
    def process_format_conversion(self):
        """Process the format conversion operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('format_conversion', settings)
            else:
                messagebox.showinfo("Format Conversion", f"Format conversion settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Format conversion failed: {e}")
    
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
        """Auto-load GIF for format conversion."""
        # Store the path and update status
        self.current_gif_path = gif_path
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"GIF loaded: {Path(gif_path).name}")
        
        # Try to read current format info from GIF
        try:
            from PIL import Image
            with Image.open(gif_path) as gif:
                format_info = gif.format
                size_info = f"{gif.size[0]}x{gif.size[1]}"
                frame_count = getattr(gif, 'n_frames', 1)
                
                format_text = f"Current: {format_info} format, {size_info}, {frame_count} frames"
                
                if hasattr(self, 'current_format_label'):
                    self.current_format_label.config(text=format_text)
                    
        except Exception:
            # If we can't read the format info, just show that it's loaded
            if hasattr(self, 'current_format_label'):
                self.current_format_label.config(text="GIF loaded (format info unavailable)")
