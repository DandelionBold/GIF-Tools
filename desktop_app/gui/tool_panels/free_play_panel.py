"""
Free Play Panel for layering GIFs with click-to-place functionality.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path


class FreePlayPanel:
    """Panel for layering GIFs with click-to-place functionality."""
    
    def __init__(self, parent, on_process):
        self.parent = parent
        self.on_process = on_process
        
        # GIF layers data
        self.gif_layers = []  # List of {'file_path': str, 'position': (x, y), 'frames': list}
        self.current_gif = None
        self.preview_frames = []
        self.current_frame = 0
        self.is_playing = False
        
        # Canvas dimensions
        self.canvas_width = 600
        self.canvas_height = 400
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main container
        self.main_container = ttk.Frame(self.parent)
        
        # Left panel - Controls
        self.controls_frame = ttk.LabelFrame(self.main_container, text="Controls", padding=10)
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right panel - Preview
        self.preview_frame = ttk.LabelFrame(self.main_container, text="Preview", padding=10)
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_controls()
        self.setup_preview()
    
    def setup_controls(self):
        """Set up control widgets."""
        row = 0
        
        # Load GIF button
        ttk.Button(
            self.controls_frame, 
            text="Load GIF", 
            command=self.load_gif
        ).grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.W+tk.E)
        row += 1
        
        # Current GIF info
        self.current_gif_label = ttk.Label(self.controls_frame, text="No GIF loaded")
        self.current_gif_label.grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.W)
        row += 1
        
        # Instructions
        instructions = ttk.Label(
            self.controls_frame, 
            text="Instructions:\n1. Load a GIF\n2. Click on preview to place it\n3. Load more GIFs to layer\n4. Click 'Create Combined GIF'",
            wraplength=200
        )
        instructions.grid(row=row, column=0, columnspan=2, pady=10, sticky=tk.W)
        row += 1
        
        # Separator
        ttk.Separator(self.controls_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10
        )
        row += 1
        
        # Layer list
        ttk.Label(self.controls_frame, text="Layered GIFs:").grid(row=row, column=0, sticky=tk.W)
        row += 1
        
        # Listbox for layers
        self.layers_listbox = tk.Listbox(self.controls_frame, height=8, width=30)
        self.layers_listbox.grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.W+tk.E)
        self.layers_listbox.bind('<<ListboxSelect>>', self.on_layer_select)
        row += 1
        
        # Layer controls
        layer_controls = ttk.Frame(self.controls_frame)
        layer_controls.grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.W+tk.E)
        
        ttk.Button(layer_controls, text="Remove", command=self.remove_selected_layer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(layer_controls, text="Clear All", command=self.clear_all_layers).pack(side=tk.LEFT)
        row += 1
        
        # Separator
        ttk.Separator(self.controls_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10
        )
        row += 1
        
        # Quality setting
        ttk.Label(self.controls_frame, text="Quality:").grid(row=row, column=0, sticky=tk.W)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(
            self.controls_frame, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        quality_scale.grid(row=row, column=1, sticky=tk.W, padx=(5, 0))
        self.quality_label = ttk.Label(self.controls_frame, text="85")
        self.quality_label.grid(row=row, column=2, sticky=tk.W, padx=(5, 0))
        quality_scale.configure(command=self.update_quality_label)
        row += 1
        
        # Process button
        self.process_btn = ttk.Button(
            self.controls_frame, 
            text="Create Combined GIF", 
            command=self.process_layers
        )
        self.process_btn.grid(row=row, column=0, columnspan=2, pady=20, sticky=tk.W+tk.E)
        row += 1
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.controls_frame, 
            mode='indeterminate'
        )
        self.progress_bar.grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.W+tk.E)
        self.progress_bar.grid_remove()  # Hide initially
        row += 1
        
        # Configure grid weights
        self.controls_frame.grid_columnconfigure(0, weight=1)
    
    def setup_preview(self):
        """Set up preview canvas."""
        # Canvas for preview
        self.preview_canvas = tk.Canvas(
            self.preview_frame, 
            width=self.canvas_width, 
            height=self.canvas_height,
            bg='black'
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.preview_canvas.bind('<Button-1>', self.on_canvas_click)
        
        # Instructions for canvas
        self.canvas_instructions = ttk.Label(
            self.preview_frame, 
            text="Click on the canvas to place the current GIF",
            font=('Arial', 10, 'italic')
        )
        self.canvas_instructions.pack(pady=5)
        
        # Media controls
        controls_frame = ttk.Frame(self.preview_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Play/Pause button
        self.play_btn = ttk.Button(controls_frame, text="▶", command=self.toggle_play)
        self.play_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame navigation
        ttk.Label(controls_frame, text="Frame:").pack(side=tk.LEFT, padx=(0, 5))
        self.frame_var = tk.StringVar(value="0")
        self.frame_entry = ttk.Entry(controls_frame, textvariable=self.frame_var, width=5)
        self.frame_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.frame_entry.bind('<Return>', self.on_frame_change)
        
        # Frame scale
        self.frame_scale = ttk.Scale(
            controls_frame, 
            from_=0, 
            to=0, 
            orient=tk.HORIZONTAL,
            length=200,
            command=self.on_frame_scale_change
        )
        self.frame_scale.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        # Speed control
        ttk.Label(controls_frame, text="Speed:").pack(side=tk.LEFT, padx=(10, 5))
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(
            controls_frame, 
            from_=0.1, 
            to=5.0, 
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            length=100
        )
        self.speed_scale.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(self.preview_frame, text="No GIFs loaded")
        self.status_label.pack(pady=5)
    
    def load_gif(self):
        """Load a GIF file."""
        file_path = filedialog.askopenfilename(
            title="Select GIF File",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Load GIF
            gif = Image.open(file_path)
            
            # Extract frames
            frames = []
            durations = []
            
            if gif.is_animated:
                for frame_idx in range(gif.n_frames):
                    gif.seek(frame_idx)
                    frames.append(gif.copy().convert('RGBA'))
                    durations.append(gif.info.get('duration', 100))
            else:
                frames.append(gif.copy().convert('RGBA'))
                durations.append(100)
            
            # Store current GIF data
            self.current_gif = {
                'file_path': file_path,
                'frames': frames,
                'durations': durations,
                'is_animated': gif.is_animated
            }
            
            # Update UI
            filename = os.path.basename(file_path)
            self.current_gif_label.config(text=f"Loaded: {filename}")
            self.preview_frames = frames
            self.current_frame = 0
            
            # Update frame controls
            self.frame_scale.config(to=len(frames) - 1)
            self.frame_var.set("0")
            
            # Display first frame
            self.display_preview_frame()
            
            # Update status
            self.status_label.config(text=f"Ready to place: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GIF: {e}")
    
    def on_canvas_click(self, event):
        """Handle canvas click to place GIF."""
        if not self.current_gif:
            messagebox.showwarning("No GIF", "Please load a GIF first.")
            return
        
        # Get click position
        x, y = event.x, event.y
        
        # Convert canvas coordinates to GIF coordinates
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Calculate scale
        scale = min(canvas_width / self.canvas_width, canvas_height / self.canvas_height)
        
        # Convert to GIF coordinates
        gif_x = int(x / scale)
        gif_y = int(y / scale)
        
        # Add to layers
        layer = {
            'file_path': self.current_gif['file_path'],
            'position': (gif_x, gif_y),
            'frames': self.current_gif['frames'],
            'durations': self.current_gif['durations'],
            'is_animated': self.current_gif['is_animated']
        }
        
        self.gif_layers.append(layer)
        
        # Update layers list
        self.update_layers_list()
        
        # Update preview
        self.display_preview_frame()
        
        # Update status
        filename = os.path.basename(self.current_gif['file_path'])
        self.status_label.config(text=f"Placed: {filename} at ({gif_x}, {gif_y})")
    
    def update_layers_list(self):
        """Update the layers listbox."""
        self.layers_listbox.delete(0, tk.END)
        
        for i, layer in enumerate(self.gif_layers):
            filename = os.path.basename(layer['file_path'])
            x, y = layer['position']
            self.layers_listbox.insert(tk.END, f"{i+1}. {filename} at ({x}, {y})")
    
    def on_layer_select(self, event):
        """Handle layer selection."""
        selection = self.layers_listbox.curselection()
        if selection:
            # Highlight selected layer in preview
            self.display_preview_frame()
    
    def remove_selected_layer(self):
        """Remove selected layer."""
        selection = self.layers_listbox.curselection()
        if selection:
            index = selection[0]
            del self.gif_layers[index]
            self.update_layers_list()
            self.display_preview_frame()
            self.status_label.config(text="Layer removed")
    
    def clear_all_layers(self):
        """Clear all layers."""
        self.gif_layers.clear()
        self.update_layers_list()
        self.display_preview_frame()
        self.status_label.config(text="All layers cleared")
    
    def update_quality_label(self, value):
        """Update quality label."""
        self.quality_label.config(text=str(int(float(value))))
    
    def display_preview_frame(self):
        """Display the current preview frame with all layers."""
        if not self.preview_frames and not self.gif_layers:
            return
        
        try:
            # Create composite frame
            if self.gif_layers:
                # Use the first layer as base
                base_layer = self.gif_layers[0]
                if base_layer['is_animated']:
                    base_frame = base_layer['frames'][self.current_frame % len(base_layer['frames'])]
                else:
                    base_frame = base_layer['frames'][0]
                
                # Create composite
                composite = base_frame.copy()
                
                # Add other layers
                for layer in self.gif_layers[1:]:
                    if layer['is_animated']:
                        layer_frame = layer['frames'][self.current_frame % len(layer['frames'])]
                    else:
                        layer_frame = layer['frames'][0]
                    
                    # Paste layer at its position
                    x, y = layer['position']
                    if layer_frame.mode == 'RGBA':
                        composite.paste(layer_frame, (x, y), layer_frame)
                    else:
                        composite.paste(layer_frame, (x, y))
                
                # Display composite
                self.display_frame_on_canvas(composite)
            else:
                # Display current GIF frame
                frame = self.preview_frames[self.current_frame]
                self.display_frame_on_canvas(frame)
                
        except Exception as e:
            print(f"Display error: {e}")
    
    def display_frame_on_canvas(self, frame):
        """Display a frame on the canvas."""
        try:
            # Convert PIL image to PhotoImage
            photo = ImageTk.PhotoImage(frame)
            
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
            photo = ImageTk.PhotoImage(resized)
            
            # Clear canvas and display
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                canvas_width // 2, 
                canvas_height // 2, 
                image=photo, 
                anchor=tk.CENTER
            )
            
            # Keep reference to prevent garbage collection
            self.preview_canvas.image = photo
            
        except Exception as e:
            print(f"Canvas display error: {e}")
    
    def toggle_play(self):
        """Toggle play/pause animation."""
        if not self.preview_frames and not self.gif_layers:
            return
        
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_btn.config(text="⏸")
            self.start_play_loop()
        else:
            self.play_btn.config(text="▶")
    
    def start_play_loop(self):
        """Start the play loop."""
        if self.is_playing:
            self.display_preview_frame()
            self.current_frame = (self.current_frame + 1) % max(len(self.preview_frames), 1)
            
            # Update frame controls
            if self.preview_frames:
                self.frame_var.set(str(self.current_frame))
                self.frame_scale.set(self.current_frame)
            
            # Schedule next frame
            delay = int(1000 / (self.speed_var.get() * 10))
            self.parent.after(delay, self.start_play_loop)
    
    def on_frame_change(self, event):
        """Handle frame number change."""
        try:
            frame_num = int(self.frame_var.get())
            if 0 <= frame_num < max(len(self.preview_frames), 1):
                self.current_frame = frame_num
                self.frame_scale.set(frame_num)
                self.display_preview_frame()
        except ValueError:
            pass
    
    def on_frame_scale_change(self, value):
        """Handle frame scale change."""
        try:
            frame_num = int(float(value))
            if 0 <= frame_num < max(len(self.preview_frames), 1):
                self.current_frame = frame_num
                self.frame_var.set(str(frame_num))
                self.display_preview_frame()
        except ValueError:
            pass
    
    def process_layers(self):
        """Process all layers to create combined GIF."""
        if not self.gif_layers:
            messagebox.showwarning("No Layers", "Please add some GIF layers first.")
            return
        
        # Get output path
        output_path = filedialog.asksaveasfilename(
            title="Save Combined GIF",
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        
        if not output_path:
            return
        
        # Start progress
        self.start_progress()
        
        # Get settings
        settings = {
            'gif_layers': self.gif_layers,
            'quality': self.quality_var.get()
        }
        
        # Process
        try:
            self.on_process('free_play', output_path, settings)
            self.status_label.config(text="Combined GIF created successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create combined GIF: {e}")
        finally:
            self.stop_progress()
    
    def start_progress(self):
        """Start progress indication."""
        self.progress_bar.grid()
        self.progress_bar.start()
        self.process_btn.config(state='disabled')
    
    def stop_progress(self):
        """Stop progress indication."""
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.process_btn.config(state='normal')
    
    def get_widget(self):
        """Get the main widget."""
        return self.main_container
