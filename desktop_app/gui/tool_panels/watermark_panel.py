"""
Watermark Tool Panel

GUI panel for the GIF watermark tool with text and image watermark options.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.watermark import add_text_watermark_to_gif, add_image_watermark_to_gif


class WatermarkPanel:
    """Panel for GIF watermark operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the watermark panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.current_gif_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the watermark panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Watermark", padding="10")
        
        # Description
        desc_text = "Add text or image watermarks to your GIF. Customize position, opacity, and styling."
        ttk.Label(self.frame, text=desc_text, wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Watermark type selection
        ttk.Label(self.frame, text="Watermark Type:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        self.watermark_type_var = tk.StringVar(value="text")
        type_frame = ttk.Frame(self.frame)
        type_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Radiobutton(
            type_frame,
            text="Text Watermark",
            variable=self.watermark_type_var,
            value="text",
            command=self.update_controls
        ).grid(row=0, column=0, padx=(0, 20), sticky=tk.W)
        
        ttk.Radiobutton(
            type_frame,
            text="Image Watermark",
            variable=self.watermark_type_var,
            value="image",
            command=self.update_controls
        ).grid(row=0, column=1, sticky=tk.W)
        
        # Text watermark settings
        self.text_frame = ttk.LabelFrame(self.frame, text="Text Watermark Settings", padding="10")
        self.text_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Text input
        ttk.Label(self.text_frame, text="Watermark Text:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.watermark_text_var = tk.StringVar(value="© Your Name")
        ttk.Entry(
            self.text_frame,
            textvariable=self.watermark_text_var,
            width=30
        ).grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Font settings
        ttk.Label(self.text_frame, text="Font Family:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.font_family_var = tk.StringVar(value="Arial")
        font_combo = ttk.Combobox(
            self.text_frame,
            textvariable=self.font_family_var,
            values=["Arial", "Times New Roman", "Helvetica", "Courier New", "Verdana", "Georgia"],
            state="readonly",
            width=20
        )
        font_combo.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        ttk.Label(self.text_frame, text="Font Size:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.IntVar(value=24)
        font_size_scale = ttk.Scale(
            self.text_frame,
            from_=8,
            to=72,
            variable=self.font_size_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_font_size_label
        )
        font_size_scale.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.font_size_label = ttk.Label(self.text_frame, text="24")
        self.font_size_label.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Text color
        ttk.Label(self.text_frame, text="Text Color:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.text_color = (255, 255, 255)  # Default white
        self.text_color_button = ttk.Button(
            self.text_frame,
            text="Choose Color",
            command=self.choose_text_color,
            width=12
        )
        self.text_color_button.grid(row=4, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        self.text_color_preview = tk.Frame(self.text_frame, width=30, height=20, bg="#FFFFFF", relief=tk.SUNKEN)
        self.text_color_preview.grid(row=4, column=2, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Background color
        self.bg_enabled_var = tk.BooleanVar(value=False)
        self.bg_check = ttk.Checkbutton(
            self.text_frame,
            text="Background Color",
            variable=self.bg_enabled_var,
            command=self.update_controls
        )
        self.bg_check.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        self.bg_color = (0, 0, 0)  # Default black
        self.bg_color_button = ttk.Button(
            self.text_frame,
            text="Choose BG Color",
            command=self.choose_bg_color,
            width=12,
            state=tk.DISABLED
        )
        self.bg_color_button.grid(row=5, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        self.bg_color_preview = tk.Frame(self.text_frame, width=30, height=20, bg="#000000", relief=tk.SUNKEN)
        self.bg_color_preview.grid(row=5, column=2, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Image watermark settings
        self.image_frame = ttk.LabelFrame(self.frame, text="Image Watermark Settings", padding="10")
        self.image_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Image selection
        ttk.Label(self.image_frame, text="Watermark Image:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.watermark_image_path = tk.StringVar()
        ttk.Entry(
            self.image_frame,
            textvariable=self.watermark_image_path,
            width=30
        ).grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        ttk.Button(
            self.image_frame,
            text="Browse",
            command=self.browse_watermark_image,
            width=12
        ).grid(row=0, column=2, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Image scale
        ttk.Label(self.image_frame, text="Scale:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.image_scale_var = tk.DoubleVar(value=1.0)
        image_scale = ttk.Scale(
            self.image_frame,
            from_=0.1,
            to=2.0,
            variable=self.image_scale_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_image_scale_label
        )
        image_scale.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.image_scale_label = ttk.Label(self.image_frame, text="1.0x")
        self.image_scale_label.grid(row=2, column=0, columnspan=3, pady=5)
        
        # Position settings
        self.position_frame = ttk.LabelFrame(self.frame, text="Position Settings", padding="10")
        self.position_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.position_frame, text="Position:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.position_var = tk.StringVar(value="bottom_right")
        position_combo = ttk.Combobox(
            self.position_frame,
            textvariable=self.position_var,
            values=[
                "top_left", "top_center", "top_right",
                "center_left", "center", "center_right",
                "bottom_left", "bottom_center", "bottom_right",
                "custom"
            ],
            state="readonly",
            width=15
        )
        position_combo.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Custom position
        ttk.Label(self.position_frame, text="Custom Position (x,y):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.custom_x_var = tk.IntVar(value=10)
        self.custom_y_var = tk.IntVar(value=10)
        ttk.Spinbox(
            self.position_frame,
            from_=0,
            to=1000,
            textvariable=self.custom_x_var,
            width=8
        ).grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.W)
        ttk.Spinbox(
            self.position_frame,
            from_=0,
            to=1000,
            textvariable=self.custom_y_var,
            width=8
        ).grid(row=1, column=2, padx=(10, 0), pady=5, sticky=tk.W)
        
        # Padding
        ttk.Label(self.position_frame, text="Padding:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.padding_var = tk.IntVar(value=10)
        padding_scale = ttk.Scale(
            self.position_frame,
            from_=0,
            to=50,
            variable=self.padding_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_padding_label
        )
        padding_scale.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.padding_label = ttk.Label(self.position_frame, text="10 px")
        self.padding_label.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Opacity settings
        self.opacity_frame = ttk.LabelFrame(self.frame, text="Opacity Settings", padding="10")
        self.opacity_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.opacity_frame, text="Opacity:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.opacity_var = tk.DoubleVar(value=0.7)
        opacity_scale = ttk.Scale(
            self.opacity_frame,
            from_=0.1,
            to=1.0,
            variable=self.opacity_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_opacity_label
        )
        opacity_scale.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.opacity_label = ttk.Label(self.opacity_frame, text="70%")
        self.opacity_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Output settings
        self.output_frame = ttk.LabelFrame(self.frame, text="Output Settings", padding="10")
        self.output_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
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
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame,
            text="💧 Add Watermark",
            command=self.process_watermark
        )
        self.progress_bar = ttk.Progressbar(
            self.frame,
            mode='indeterminate'
        )
        self.process_btn.grid(row=7, column=0, columnspan=3, pady=10)
        self.progress_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="No GIF loaded", foreground="gray")
        self.status_label.grid(row=9, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
        
        # Initialize controls visibility
        self.update_controls()
    
    def update_controls(self):
        """Update control visibility based on watermark type."""
        watermark_type = self.watermark_type_var.get()
        
        # Show/hide frames based on type
        if watermark_type == "text":
            self.text_frame.grid()
            self.image_frame.grid_remove()
        else:
            self.text_frame.grid_remove()
            self.image_frame.grid()
        
        # Update background color controls
        bg_enabled = self.bg_enabled_var.get()
        if bg_enabled:
            self.bg_color_button.config(state=tk.NORMAL)
        else:
            self.bg_color_button.config(state=tk.DISABLED)
    
    def update_font_size_label(self, value):
        """Update the font size label when scale changes."""
        self.font_size_label.config(text=str(int(float(value))))
    
    def update_image_scale_label(self, value):
        """Update the image scale label when scale changes."""
        self.image_scale_label.config(text=f"{float(value):.1f}x")
    
    def update_padding_label(self, value):
        """Update the padding label when scale changes."""
        self.padding_label.config(text=f"{int(float(value))} px")
    
    def update_opacity_label(self, value):
        """Update the opacity label when scale changes."""
        opacity_percent = int(float(value) * 100)
        self.opacity_label.config(text=f"{opacity_percent}%")
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def choose_text_color(self):
        """Choose text color."""
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[1]:  # If a color was selected
            # Convert hex to RGB tuple
            hex_color = color[1].lstrip('#')
            rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            self.text_color = rgb_color
            self.text_color_preview.config(bg=color[1])
    
    def choose_bg_color(self):
        """Choose background color."""
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[1]:  # If a color was selected
            # Convert hex to RGB tuple
            hex_color = color[1].lstrip('#')
            rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            self.bg_color = rgb_color
            self.bg_color_preview.config(bg=color[1])
    
    def browse_watermark_image(self):
        """Browse for watermark image."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Watermark Image",
            filetypes=filetypes
        )
        if filename:
            self.watermark_image_path.set(filename)
    
    def get_settings(self) -> dict:
        """Get current watermark settings."""
        if not self.current_gif_path:
            raise ValueError("No GIF file loaded")
        
        watermark_type = self.watermark_type_var.get()
        position = self.position_var.get()
        
        settings = {
            'input_path': self.current_gif_path,
            'position': position,
            'opacity': self.opacity_var.get(),
            'padding': self.padding_var.get(),
            'quality': int(self.quality_var.get()),
        }
        
        if position == "custom":
            settings.update({
                'custom_position': (self.custom_x_var.get(), self.custom_y_var.get())
            })
        
        if watermark_type == "text":
            settings.update({
                'text': self.watermark_text_var.get(),
                'font_family': self.font_family_var.get(),
                'font_size': self.font_size_var.get(),
                'color': self.text_color,
            })
            
            if self.bg_enabled_var.get():
                settings['background_color'] = self.bg_color
        else:  # image
            image_path = self.watermark_image_path.get()
            if not image_path:
                raise ValueError("Please select a watermark image")
            settings.update({
                'watermark_image': image_path,
                'scale': self.image_scale_var.get(),
            })
        
        return settings
    
    def process_watermark(self):
        """Process the watermark operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('watermark', settings)
            else:
                messagebox.showinfo("Watermark", f"Watermark settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Watermark failed: {e}")
    
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
        """Auto-load GIF for watermarking."""
        # Store the path and update status
        self.current_gif_path = gif_path
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"GIF loaded: {Path(gif_path).name}")
