"""
Add Text Tool Panel

GUI panel for the GIF add text tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font, colorchooser
from pathlib import Path
from typing import Optional, Callable, Any
import threading
import math

from gif_tools.core.add_text import add_text_to_gif


class AddTextPanel:
    """Panel for GIF add text operations with live preview."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the add text panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.current_file = None
        self.preview_gif = None
        self.preview_frames = []
        self.current_frame = 0
        self.is_playing = False
        self.play_thread = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the add text panel UI with live preview."""
        # Main container
        self.main_container = ttk.Frame(self.parent)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        self.controls_frame = ttk.LabelFrame(self.main_container, text="Text Settings", padding="10")
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right panel - Preview
        self.preview_frame = ttk.LabelFrame(self.main_container, text="Live Preview", padding="10")
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_controls()
        self.setup_preview()
    
    def setup_controls(self):
        """Setup the controls panel."""
        row = 0
        
        # Text input
        ttk.Label(self.controls_frame, text="Text:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.text_var = tk.StringVar(value="Hello World!")
        self.text_var.trace('w', self.update_preview)
        text_entry = ttk.Entry(self.controls_frame, textvariable=self.text_var, width=25)
        text_entry.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Click to position
        ttk.Label(self.controls_frame, text="Position:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.click_pos_var = tk.StringVar(value="Click on preview to position")
        self.click_pos_label = ttk.Label(self.controls_frame, textvariable=self.click_pos_var, 
                                       foreground="blue", cursor="hand2")
        self.click_pos_label.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5)
        self.click_pos_label.bind("<Button-1>", self.on_click_position)
        row += 1
        
        # Font controls
        ttk.Label(self.controls_frame, text="Font:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.font_family_var = tk.StringVar(value="Arial")
        self.font_family_var.trace('w', self.update_preview)
        font_combo = ttk.Combobox(
            self.controls_frame, 
            textvariable=self.font_family_var,
            values=["Arial", "Times New Roman", "Courier New", "Helvetica", "Verdana", 
                   "Tahoma", "Calibri", "Segoe UI", "Arabic Typesetting", "Arial Unicode MS"],
            state="readonly",
            width=20
        )
        font_combo.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        row += 1
        
        # Font size
        ttk.Label(self.controls_frame, text="Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.IntVar(value=24)
        self.font_size_var.trace('w', self.update_preview)
        size_scale = ttk.Scale(
            self.controls_frame, 
            from_=8, 
            to=72, 
            variable=self.font_size_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        size_scale.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.size_label = ttk.Label(self.controls_frame, text="24")
        self.size_label.grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        size_scale.configure(command=self.update_size_label)
        row += 1
        
        # Text color with picker
        ttk.Label(self.controls_frame, text="Text Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.text_color = (255, 255, 255)  # White
        self.text_color_button = ttk.Button(
            self.controls_frame, 
            text="Choose Color", 
            command=self.choose_text_color
        )
        self.text_color_button.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.text_color_preview = tk.Frame(self.controls_frame, width=30, height=20, bg="white")
        self.text_color_preview.grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        row += 1
        
        # Text opacity
        ttk.Label(self.controls_frame, text="Text Opacity:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.text_opacity_var = tk.DoubleVar(value=1.0)
        self.text_opacity_var.trace('w', self.update_preview)
        text_opacity_scale = ttk.Scale(
            self.controls_frame, 
            from_=0.0, 
            to=1.0, 
            variable=self.text_opacity_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        text_opacity_scale.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.text_opacity_label = ttk.Label(self.controls_frame, text="100%")
        self.text_opacity_label.grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        text_opacity_scale.configure(command=self.update_text_opacity_label)
        row += 1
        
        # Alignment
        ttk.Label(self.controls_frame, text="Alignment:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.alignment_var = tk.StringVar(value="left")
        self.alignment_var.trace('w', self.update_preview)
        align_combo = ttk.Combobox(
            self.controls_frame, 
            textvariable=self.alignment_var,
            values=["left", "center", "right"],
            state="readonly",
            width=15
        )
        align_combo.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        row += 1
        
        # Background controls
        self.bg_enabled_var = tk.BooleanVar(value=False)
        self.bg_enabled_var.trace('w', self.update_preview)
        bg_check = ttk.Checkbutton(
            self.controls_frame, 
            text="Background", 
            variable=self.bg_enabled_var,
            command=self.toggle_background
        )
        bg_check.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Background color
        self.bg_color = (0, 0, 0)  # Black
        self.bg_color_button = ttk.Button(
            self.controls_frame, 
            text="BG Color", 
            command=self.choose_bg_color,
            state=tk.DISABLED
        )
        self.bg_color_button.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.bg_color_preview = tk.Frame(self.controls_frame, width=30, height=20, bg="black")
        self.bg_color_preview.grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        row += 1
        
        # Background opacity
        ttk.Label(self.controls_frame, text="BG Opacity:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.bg_opacity_var = tk.DoubleVar(value=0.5)
        self.bg_opacity_var.trace('w', self.update_preview)
        self.bg_opacity_scale = ttk.Scale(
            self.controls_frame, 
            from_=0.0, 
            to=1.0, 
            variable=self.bg_opacity_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        self.bg_opacity_scale.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.bg_opacity_scale.config(state=tk.DISABLED)
        self.bg_opacity_label = ttk.Label(self.controls_frame, text="50%")
        self.bg_opacity_label.grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        self.bg_opacity_scale.configure(command=self.update_bg_opacity_label)
        row += 1
        
        # Stroke controls
        self.stroke_enabled_var = tk.BooleanVar(value=False)
        self.stroke_enabled_var.trace('w', self.update_preview)
        stroke_check = ttk.Checkbutton(
            self.controls_frame, 
            text="Stroke", 
            variable=self.stroke_enabled_var,
            command=self.toggle_stroke
        )
        stroke_check.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Stroke width
        ttk.Label(self.controls_frame, text="Stroke Width:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.stroke_width_var = tk.IntVar(value=2)
        self.stroke_width_var.trace('w', self.update_preview)
        self.stroke_width_scale = ttk.Scale(
            self.controls_frame, 
            from_=0, 
            to=10, 
            variable=self.stroke_width_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        self.stroke_width_scale.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.stroke_width_scale.config(state=tk.DISABLED)
        self.stroke_width_label = ttk.Label(self.controls_frame, text="2")
        self.stroke_width_label.grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        self.stroke_width_scale.configure(command=self.update_stroke_width_label)
        row += 1
        
        # Stroke color
        ttk.Label(self.controls_frame, text="Stroke Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.stroke_color = (0, 0, 0)  # Black
        self.stroke_color_button = ttk.Button(
            self.controls_frame, 
            text="Stroke Color", 
            command=self.choose_stroke_color,
            state=tk.DISABLED
        )
        self.stroke_color_button.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.stroke_color_preview = tk.Frame(self.controls_frame, width=30, height=20, bg="black")
        self.stroke_color_preview.grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        row += 1
        
        # Stroke opacity
        ttk.Label(self.controls_frame, text="Stroke Opacity:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.stroke_opacity_var = tk.DoubleVar(value=1.0)
        self.stroke_opacity_var.trace('w', self.update_preview)
        self.stroke_opacity_scale = ttk.Scale(
            self.controls_frame, 
            from_=0.0, 
            to=1.0, 
            variable=self.stroke_opacity_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        self.stroke_opacity_scale.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.stroke_opacity_scale.config(state=tk.DISABLED)
        self.stroke_opacity_label = ttk.Label(self.controls_frame, text="100%")
        self.stroke_opacity_label.grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        self.stroke_opacity_scale.configure(command=self.update_stroke_opacity_label)
        row += 1
        
        # Quality control
        ttk.Label(self.controls_frame, text="Quality:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(
            self.controls_frame, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        quality_scale.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.quality_label = ttk.Label(self.controls_frame, text="85")
        self.quality_label.grid(row=row, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        quality_scale.configure(command=self.update_quality_label)
        row += 1
        
        # Process button
        self.process_btn = ttk.Button(
            self.controls_frame, 
            text="Add Text to GIF", 
            command=self.process_add_text
        )
        self.process_btn.grid(row=row, column=0, columnspan=3, pady=10)
        row += 1
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.controls_frame, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.controls_frame.grid_columnconfigure(1, weight=1)
    
    def setup_preview(self):
        """Setup the preview panel with media player controls."""
        # Preview canvas
        self.preview_canvas = tk.Canvas(self.preview_frame, width=400, height=300, bg="black")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.preview_canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Media player controls
        controls_frame = ttk.Frame(self.preview_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Play/Pause button
        self.play_btn = ttk.Button(controls_frame, text="▶", command=self.toggle_play)
        self.play_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Frame navigation
        ttk.Label(controls_frame, text="Frame:").pack(side=tk.LEFT, padx=(10, 5))
        self.frame_var = tk.StringVar(value="0")
        self.frame_entry = ttk.Entry(controls_frame, textvariable=self.frame_var, width=8)
        self.frame_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.frame_entry.bind("<Return>", self.on_frame_change)
        
        # Frame slider
        self.frame_scale = ttk.Scale(controls_frame, from_=0, to=0, orient=tk.HORIZONTAL, 
                                   command=self.on_frame_scale_change)
        self.frame_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Speed control
        ttk.Label(controls_frame, text="Speed:").pack(side=tk.LEFT, padx=(10, 5))
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(controls_frame, from_=0.1, to=3.0, variable=self.speed_var, 
                              orient=tk.HORIZONTAL, length=100)
        speed_scale.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(self.preview_frame, text="No GIF loaded")
        self.status_label.pack(pady=5)
    
    def on_canvas_click(self, event):
        """Handle canvas click for text positioning."""
        if not self.preview_gif:
            return
        
        # Calculate position relative to GIF
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Get GIF dimensions
        gif_width = self.preview_gif.width
        gif_height = self.preview_gif.height
        
        # Calculate scale
        scale_x = gif_width / canvas_width
        scale_y = gif_height / canvas_height
        
        # Convert click position to GIF coordinates
        x = int(event.x * scale_x)
        y = int(event.y * scale_y)
        
        # Update position
        self.text_position = (x, y)
        self.click_pos_var.set(f"Position: ({x}, {y})")
        self.update_preview()
    
    def on_click_position(self, event):
        """Handle click on position label."""
        self.click_pos_var.set("Click on preview to position")
    
    def choose_text_color(self):
        """Open color picker for text color."""
        color = colorchooser.askcolor(title="Choose Text Color", color=self.text_color)[1]
        if color:
            self.text_color = tuple(int(c) for c in color[1:].split(','))
            self.text_color_preview.config(bg=color)
            self.update_preview()
    
    def choose_bg_color(self):
        """Open color picker for background color."""
        color = colorchooser.askcolor(title="Choose Background Color", color=self.bg_color)[1]
        if color:
            self.bg_color = tuple(int(c) for c in color[1:].split(','))
            self.bg_color_preview.config(bg=color)
            self.update_preview()
    
    def choose_stroke_color(self):
        """Open color picker for stroke color."""
        color = colorchooser.askcolor(title="Choose Stroke Color", color=self.stroke_color)[1]
        if color:
            self.stroke_color = tuple(int(c) for c in color[1:].split(','))
            self.stroke_color_preview.config(bg=color)
            self.update_preview()
    
    def toggle_background(self):
        """Toggle background controls."""
        if self.bg_enabled_var.get():
            self.bg_color_button.config(state=tk.NORMAL)
            self.bg_opacity_scale.config(state=tk.NORMAL)
        else:
            self.bg_color_button.config(state=tk.DISABLED)
            self.bg_opacity_scale.config(state=tk.DISABLED)
        self.update_preview()
    
    def toggle_stroke(self):
        """Toggle stroke controls."""
        if self.stroke_enabled_var.get():
            self.stroke_width_scale.config(state=tk.NORMAL)
            self.stroke_color_button.config(state=tk.NORMAL)
            self.stroke_opacity_scale.config(state=tk.NORMAL)
        else:
            self.stroke_width_scale.config(state=tk.DISABLED)
            self.stroke_color_button.config(state=tk.DISABLED)
            self.stroke_opacity_scale.config(state=tk.DISABLED)
        self.update_preview()
    
    def update_size_label(self, value):
        """Update the size label when scale changes."""
        self.size_label.config(text=str(int(float(value))))
    
    def update_text_opacity_label(self, value):
        """Update the text opacity label when scale changes."""
        opacity = int(float(value) * 100)
        self.text_opacity_label.config(text=f"{opacity}%")
    
    def update_bg_opacity_label(self, value):
        """Update the background opacity label when scale changes."""
        opacity = int(float(value) * 100)
        self.bg_opacity_label.config(text=f"{opacity}%")
    
    def update_stroke_width_label(self, value):
        """Update the stroke width label when scale changes."""
        self.stroke_width_label.config(text=str(int(float(value))))
    
    def update_stroke_opacity_label(self, value):
        """Update the stroke opacity label when scale changes."""
        opacity = int(float(value) * 100)
        self.stroke_opacity_label.config(text=f"{opacity}%")
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def update_preview(self, *args):
        """Update the live preview."""
        if not self.preview_gif or not hasattr(self, 'text_position'):
            return
        
        try:
            # Create preview frame with text
            preview_frame = self.create_text_preview()
            if preview_frame:
                self.display_preview_frame(preview_frame)
        except Exception as e:
            print(f"Preview update error: {e}")
    
    def create_text_preview(self):
        """Create a preview frame with text overlay."""
        if not self.preview_gif or not hasattr(self, 'text_position'):
            return None
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Get current frame
            if self.preview_gif.is_animated:
                frame = self.preview_frames[self.current_frame]
            else:
                frame = self.preview_gif
            
            # Create a copy for preview
            preview = frame.copy().convert('RGBA')
            draw = ImageDraw.Draw(preview)
            
            # Get text settings
            text = self.text_var.get()
            if not text:
                return preview
            
            position = self.text_position
            font_family = self.font_family_var.get()
            font_size = self.font_size_var.get()
            alignment = self.alignment_var.get()
            
            # Create font
            try:
                font_obj = ImageFont.truetype(font_family, font_size)
            except:
                font_obj = ImageFont.load_default()
            
            # Get text color with opacity
            text_color = self.text_color + (int(self.text_opacity_var.get() * 255),)
            
            # Draw background if enabled
            if self.bg_enabled_var.get():
                bg_color = self.bg_color + (int(self.bg_opacity_var.get() * 255),)
                # Calculate text bounds
                bbox = draw.textbbox(position, text, font=font_obj)
                draw.rectangle(bbox, fill=bg_color)
            
            # Draw stroke if enabled
            if self.stroke_enabled_var.get():
                stroke_width = self.stroke_width_var.get()
                stroke_color = self.stroke_color + (int(self.stroke_opacity_var.get() * 255),)
                
                # Draw stroke
                for adj in range(-stroke_width, stroke_width + 1):
                    for adj2 in range(-stroke_width, stroke_width + 1):
                        if adj != 0 or adj2 != 0:
                            draw.text((position[0] + adj, position[1] + adj2), text, 
                                    font=font_obj, fill=stroke_color)
            
            # Draw text
            draw.text(position, text, font=font_obj, fill=text_color)
            
            return preview
            
        except Exception as e:
            print(f"Preview creation error: {e}")
            return None
    
    def display_preview_frame(self, frame):
        """Display a frame in the preview canvas."""
        try:
            # Convert PIL image to PhotoImage
            from PIL import ImageTk
            
            # Resize to fit canvas
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Calculate scale to fit
            scale = min(canvas_width / frame.width, canvas_height / frame.height)
            new_width = int(frame.width * scale)
            new_height = int(frame.height * scale)
            
            # Resize frame
            resized = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(resized)
            
            # Clear canvas and display
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
            self.preview_canvas.image = photo  # Keep reference
            
        except Exception as e:
            print(f"Display error: {e}")
    
    def toggle_play(self):
        """Toggle play/pause of preview."""
        if not self.preview_gif or not self.preview_gif.is_animated:
            return
        
        if self.is_playing:
            self.is_playing = False
            self.play_btn.config(text="▶")
        else:
            self.is_playing = True
            self.play_btn.config(text="⏸")
            self.start_play_loop()
    
    def start_play_loop(self):
        """Start the play loop in a separate thread."""
        if self.play_thread and self.play_thread.is_alive():
            return
        
        self.play_thread = threading.Thread(target=self.play_loop, daemon=True)
        self.play_thread.start()
    
    def play_loop(self):
        """Play loop for animated preview."""
        while self.is_playing and self.preview_gif and self.preview_gif.is_animated:
            try:
                # Update preview
                preview_frame = self.create_text_preview()
                if preview_frame:
                    self.parent.after(0, lambda: self.display_preview_frame(preview_frame))
                
                # Move to next frame
                self.current_frame = (self.current_frame + 1) % len(self.preview_frames)
                self.parent.after(0, lambda: self.frame_var.set(str(self.current_frame)))
                self.parent.after(0, lambda: self.frame_scale.set(self.current_frame))
                
                # Wait based on speed
                import time
                time.sleep(0.1 / self.speed_var.get())
                
            except Exception as e:
                print(f"Play loop error: {e}")
                break
    
    def on_frame_change(self, event):
        """Handle frame number change."""
        try:
            frame_num = int(self.frame_var.get())
            if 0 <= frame_num < len(self.preview_frames):
                self.current_frame = frame_num
                self.frame_scale.set(frame_num)
                self.update_preview()
        except ValueError:
            pass
    
    def on_frame_scale_change(self, value):
        """Handle frame scale change."""
        try:
            frame_num = int(float(value))
            if 0 <= frame_num < len(self.preview_frames):
                self.current_frame = frame_num
                self.frame_var.set(str(frame_num))
                self.update_preview()
        except ValueError:
            pass
    
    def get_settings(self) -> dict:
        """Get current add text settings."""
        settings = {
            'text': self.text_var.get(),
            'position': getattr(self, 'text_position', (10, 10)),
            'font_family': self.font_family_var.get(),
            'font_size': self.font_size_var.get(),
            'color': self.text_color,
            'text_opacity': self.text_opacity_var.get(),
            'alignment': self.alignment_var.get(),
            'quality': self.quality_var.get()
        }
        
        # Add background settings if enabled
        if self.bg_enabled_var.get():
            settings.update({
                'background_color': self.bg_color,
                'background_opacity': self.bg_opacity_var.get()
            })
        
        # Add stroke settings if enabled
        if self.stroke_enabled_var.get():
            settings.update({
                'stroke_width': self.stroke_width_var.get(),
                'stroke_color': self.stroke_color,
                'stroke_opacity': self.stroke_opacity_var.get()
            })
        
        return settings
    
    def process_add_text(self):
        """Process the add text operation."""
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('add_text', settings)
            else:
                messagebox.showinfo("Add Text", f"Add text settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Add text failed: {e}")
    
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
        return self.main_container
    
    def auto_load_gif(self, file_path: Path):
        """Auto-load GIF file for text addition."""
        try:
            self.current_file = file_path
            # Schedule the loading after the UI is fully initialized
            self.parent.after(100, lambda: self.load_gif_preview(file_path))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GIF: {e}")
    
    def load_gif_preview(self, file_path: Path):
        """Load GIF for preview."""
        try:
            from PIL import Image
            
            # Load GIF
            self.preview_gif = Image.open(file_path)
            
            # Load frames if animated
            if self.preview_gif.is_animated:
                self.preview_frames = []
                for i in range(self.preview_gif.n_frames):
                    self.preview_gif.seek(i)
                    self.preview_frames.append(self.preview_gif.copy())
                
                # Setup frame controls
                self.frame_scale.config(to=len(self.preview_frames) - 1)
                self.frame_var.set("0")
                self.current_frame = 0
                self.status_label.config(text=f"Loaded: {file_path.name} ({len(self.preview_frames)} frames)")
            else:
                self.preview_frames = [self.preview_gif]
                self.frame_scale.config(to=0)
                self.frame_var.set("0")
                self.current_frame = 0
                self.status_label.config(text=f"Loaded: {file_path.name} (Static)")
            
            # Set initial position
            self.text_position = (10, 10)
            self.click_pos_var.set("Position: (10, 10)")
            
            # Display first frame without text first
            self.display_preview_frame(self.preview_frames[0])
            
            # Then update with text
            self.update_preview()
            
        except Exception as e:
            print(f"Load GIF error: {e}")
            self.status_label.config(text=f"Error loading: {file_path.name}")
