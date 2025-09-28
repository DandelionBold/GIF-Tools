"""
Crop Tool Panel

GUI panel for the GIF crop tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.crop import crop_gif


class CropPanel(ttk.Frame):
    """Panel for GIF crop operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the crop panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        super().__init__(parent)
        self.parent = parent
        self.on_process = on_process
        self.setup_ui()
    
    def setup_ui(self):
        """Create the crop panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self, text="Crop GIF", padding="10")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Visual crop tab
        self.visual_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.visual_frame, text="Visual Crop")
        
        # Manual crop tab
        self.manual_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.manual_frame, text="Manual Crop")
        
        # Setup visual crop interface
        self.setup_visual_crop()
        
        # Setup manual crop interface
        self.setup_manual_crop()
        
        # Common controls
        self.setup_common_controls()
    
    def setup_visual_crop(self):
        """Setup visual crop interface."""
        # Image preview frame
        preview_frame = ttk.LabelFrame(self.visual_frame, text="GIF Preview", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas for image display
        self.canvas = tk.Canvas(preview_frame, bg="white", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events for crop selection
        self.canvas.bind("<Button-1>", self.start_crop_selection)
        self.canvas.bind("<B1-Motion>", self.update_crop_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop_selection)
        
        # Load GIF button
        load_btn = ttk.Button(preview_frame, text="Load GIF", command=self.load_gif_for_crop)
        load_btn.pack(pady=5)
        
        # Crop area info
        info_frame = ttk.Frame(self.visual_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="Crop Area:").pack(side=tk.LEFT)
        self.crop_info_label = ttk.Label(info_frame, text="X: 0, Y: 0, W: 0, H: 0")
        self.crop_info_label.pack(side=tk.LEFT, padx=10)
        
        # Aspect ratio checkbox
        self.aspect_ratio_var = tk.BooleanVar(value=True)
        aspect_check = ttk.Checkbutton(info_frame, text="Lock Aspect Ratio", variable=self.aspect_ratio_var)
        aspect_check.pack(side=tk.RIGHT)
        
        # Initialize crop variables
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        self.crop_rect = None
        self.current_gif = None
        self.image_scale = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0
    
    def setup_manual_crop(self):
        """Setup manual crop interface."""
        # Crop coordinates
        ttk.Label(self.manual_frame, text="Crop Area:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # X coordinate
        ttk.Label(self.manual_frame, text="X (left):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.x_var = tk.StringVar(value="0")
        x_entry = ttk.Entry(self.manual_frame, textvariable=self.x_var, width=10)
        x_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Y coordinate
        ttk.Label(self.manual_frame, text="Y (top):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.y_var = tk.StringVar(value="0")
        y_entry = ttk.Entry(self.manual_frame, textvariable=self.y_var, width=10)
        y_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Width
        ttk.Label(self.manual_frame, text="Width:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar(value="100")
        width_entry = ttk.Entry(self.manual_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Height
        ttk.Label(self.manual_frame, text="Height:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.StringVar(value="100")
        height_entry = ttk.Entry(self.manual_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Preset crop options
        ttk.Label(self.manual_frame, text="Presets:").grid(row=5, column=0, sticky=tk.W, pady=5)
        
        preset_frame = ttk.Frame(self.manual_frame)
        preset_frame.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        preset_buttons = [
            ("Center Square", self.set_center_square),
            ("Top Half", self.set_top_half),
            ("Bottom Half", self.set_bottom_half),
            ("Left Half", self.set_left_half),
            ("Right Half", self.set_right_half),
        ]
        
        for i, (text, command) in enumerate(preset_buttons):
            row, col = divmod(i, 2)
            btn = ttk.Button(preset_frame, text=text, command=command, width=12)
            btn.grid(row=row, column=col, padx=2, pady=2)
        
        # Crop mode
        ttk.Label(self.manual_frame, text="Crop Mode:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.mode_var = tk.StringVar(value="exact")
        mode_combo = ttk.Combobox(
            self.manual_frame, 
            textvariable=self.mode_var,
            values=["exact", "safe", "center"],
            state="readonly",
            width=15
        )
        mode_combo.grid(row=6, column=1, sticky=tk.W, padx=(5, 0), pady=5)
    
    def setup_common_controls(self):
        """Setup common controls for both tabs."""
        # Quality controls
        ttk.Label(self.frame, text="Quality:").grid(row=1, column=0, sticky=tk.W, pady=5)
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
        
        # Background color
        ttk.Label(self.frame, text="Background:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.bg_color_var = tk.StringVar(value="transparent")
        bg_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.bg_color_var,
            values=["transparent", "white", "black", "red", "green", "blue"],
            state="readonly",
            width=15
        )
        bg_combo.grid(row=8, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Crop GIF", 
            command=self.process_crop
        )
        self.process_btn.grid(row=9, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
        
        # Pack the frame
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def load_gif_for_crop(self):
        """Load GIF for visual cropping."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select GIF file",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        if file_path:
            try:
                from PIL import Image
                self.current_gif = Image.open(file_path)
                self.display_gif_preview()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load GIF: {e}")
    
    def display_gif_preview(self):
        """Display GIF preview on canvas."""
        if not self.current_gif:
            return
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Calculate scale to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready, schedule for later
            self.canvas.after(100, self.display_gif_preview)
            return
        
        img_width = self.current_gif.width
        img_height = self.current_gif.height
        
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        self.image_scale = min(scale_x, scale_y, 1.0)  # Don't scale up
        
        # Calculate centered position
        scaled_width = int(img_width * self.image_scale)
        scaled_height = int(img_height * self.image_scale)
        
        self.image_offset_x = (canvas_width - scaled_width) // 2
        self.image_offset_y = (canvas_height - scaled_height) // 2
        
        # Resize image for display
        display_img = self.current_gif.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        from PIL import ImageTk
        self.display_photo = ImageTk.PhotoImage(display_img)
        
        # Display image
        self.canvas.create_image(
            self.image_offset_x + scaled_width // 2,
            self.image_offset_y + scaled_height // 2,
            image=self.display_photo
        )
    
    def start_crop_selection(self, event):
        """Start crop area selection."""
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        self.crop_end_x = event.x
        self.crop_end_y = event.y
        
        # Clear previous crop rectangle
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
    
    def update_crop_selection(self, event):
        """Update crop area selection."""
        if self.crop_start_x is None:
            return
        
        self.crop_end_x = event.x
        self.crop_end_y = event.y
        
        # Clear previous rectangle
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        
        # Draw new rectangle
        self.crop_rect = self.canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y,
            self.crop_end_x, self.crop_end_y,
            outline="red", width=2, fill="", stipple="gray50"
        )
        
        # Update crop info
        self.update_crop_info()
    
    def end_crop_selection(self, event):
        """End crop area selection."""
        if self.crop_start_x is None:
            return
        
        self.crop_end_x = event.x
        self.crop_end_y = event.y
        
        # Update crop info
        self.update_crop_info()
    
    def update_crop_info(self):
        """Update crop area information."""
        if self.crop_start_x is None or self.crop_end_x is None:
            return
        
        # Calculate crop area in canvas coordinates
        x1 = min(self.crop_start_x, self.crop_end_x)
        y1 = min(self.crop_start_y, self.crop_end_y)
        x2 = max(self.crop_start_x, self.crop_end_x)
        y2 = max(self.crop_start_y, self.crop_end_y)
        
        # Convert to image coordinates
        if self.current_gif:
            img_x1 = int((x1 - self.image_offset_x) / self.image_scale)
            img_y1 = int((y1 - self.image_offset_y) / self.image_scale)
            img_x2 = int((x2 - self.image_offset_x) / self.image_scale)
            img_y2 = int((y2 - self.image_offset_y) / self.image_scale)
            
            # Ensure coordinates are within image bounds
            img_x1 = max(0, min(img_x1, self.current_gif.width))
            img_y1 = max(0, min(img_y1, self.current_gif.height))
            img_x2 = max(0, min(img_x2, self.current_gif.width))
            img_y2 = max(0, min(img_y2, self.current_gif.height))
            
            # Calculate width and height
            width = img_x2 - img_x1
            height = img_y2 - img_y1
            
            # Update info label
            self.crop_info_label.config(text=f"X: {img_x1}, Y: {img_y1}, W: {width}, H: {height}")
            
            # Update manual crop fields
            self.x_var.set(str(img_x1))
            self.y_var.set(str(img_y1))
            self.width_var.set(str(width))
            self.height_var.set(str(height))
    
    def set_center_square(self):
        """Set crop area to center square."""
        self.x_var.set("50")
        self.y_var.set("50")
        self.width_var.set("100")
        self.height_var.set("100")
    
    def set_top_half(self):
        """Set crop area to top half."""
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set("200")
        self.height_var.set("100")
    
    def set_bottom_half(self):
        """Set crop area to bottom half."""
        self.x_var.set("0")
        self.y_var.set("100")
        self.width_var.set("200")
        self.height_var.set("100")
    
    def set_left_half(self):
        """Set crop area to left half."""
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set("100")
        self.height_var.set("200")
    
    def set_right_half(self):
        """Set crop area to right half."""
        self.x_var.set("100")
        self.y_var.set("0")
        self.width_var.set("100")
        self.height_var.set("200")
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current crop settings."""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            quality = self.quality_var.get()
            
        except ValueError as e:
            raise ValueError(f"Invalid numeric value: {e}")
        
        settings = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'mode': self.mode_var.get(),
            'quality': quality
        }
        
        # Add background color
        bg_color = self.bg_color_var.get()
        if bg_color != "transparent":
            settings['background_color'] = bg_color
        
        return settings
    
    def process_crop(self):
        """Process the crop operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('crop', settings)
            else:
                messagebox.showinfo("Crop", f"Crop settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Crop failed: {e}")
    
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
