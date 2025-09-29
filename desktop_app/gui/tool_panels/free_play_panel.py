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
        self.selected_layer_index = -1  # Index of currently selected layer
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
        
        # Load GIFs button
        ttk.Button(
            self.controls_frame, 
            text="Load GIFs", 
            command=self.load_gifs
        ).grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.W+tk.E)
        row += 1
        
        # Selected GIFs info
        self.selected_gifs_label = ttk.Label(self.controls_frame, text="No GIFs selected")
        self.selected_gifs_label.grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.W)
        row += 1
        
        # Instructions
        instructions = ttk.Label(
            self.controls_frame, 
            text="Instructions:\n1. Load multiple GIFs\n2. Select a layer from the list\n3. Choose positioning mode\n4. Click on preview to place/move it\n5. Reorder layers as needed\n6. Click 'Create Combined GIF'",
            wraplength=200
        )
        instructions.grid(row=row, column=0, columnspan=2, pady=10, sticky=tk.W)
        row += 1
        
        # Positioning mode
        ttk.Label(self.controls_frame, text="Positioning:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.positioning_var = tk.StringVar(value="center")
        positioning_combo = ttk.Combobox(
            self.controls_frame, 
            textvariable=self.positioning_var,
            values=[
                "top-left", "top-center", "top-right",
                "center-left", "center", "center-right",
                "bottom-left", "bottom-center", "bottom-right",
                "custom"
            ],
            state="readonly",
            width=15
        )
        positioning_combo.grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=5)
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
        
        # First row of controls
        controls_row1 = ttk.Frame(layer_controls)
        controls_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(controls_row1, text="Move Up", command=self.move_layer_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_row1, text="Move Down", command=self.move_layer_down).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_row1, text="Remove", command=self.remove_selected_layer).pack(side=tk.LEFT, padx=(0, 5))
        
        # Second row of controls
        controls_row2 = ttk.Frame(layer_controls)
        controls_row2.pack(fill=tk.X)
        
        ttk.Button(controls_row2, text="Clear All", command=self.clear_all_layers).pack(side=tk.LEFT)
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
            text="Select a layer, choose positioning mode, then click on canvas to place/move it",
            font=('Arial', 10, 'italic')
        )
        self.canvas_instructions.pack(pady=5)
        
        # Selected layer info
        self.selected_layer_label = ttk.Label(
            self.preview_frame, 
            text="No layer selected",
            font=('Arial', 9, 'bold'),
            foreground='blue'
        )
        self.selected_layer_label.pack(pady=2)
        
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
    
    def load_gifs(self):
        """Load multiple GIF files."""
        file_paths = filedialog.askopenfilenames(
            title="Select GIF Files",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        
        if not file_paths:
            return
        
        loaded_count = 0
        for file_path in file_paths:
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
                
                # Add to layers (initially at position 0,0)
                layer = {
                    'file_path': file_path,
                    'position': (0, 0),
                    'frames': frames,
                    'durations': durations,
                    'is_animated': gif.is_animated
                }
                
                self.gif_layers.append(layer)
                loaded_count += 1
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {file_path}: {e}")
        
        if loaded_count > 0:
            # Update UI
            self.update_layers_list()
            self.update_selected_gifs_label()
            self.update_frame_controls()
            self.display_preview_frame()
            self.status_label.config(text=f"Loaded {loaded_count} GIF(s). Select a layer to place it.")
    
    def on_canvas_click(self, event):
        """Handle canvas click to place/move selected layer."""
        if self.selected_layer_index == -1:
            messagebox.showwarning("No Layer Selected", "Please select a layer from the list first.")
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
        
        # Get the selected layer
        layer = self.gif_layers[self.selected_layer_index]
        
        # Calculate position based on positioning mode
        positioning_mode = self.positioning_var.get()
        final_x, final_y = self.calculate_position(
            gif_x, gif_y, layer, positioning_mode
        )
        
        # Update selected layer position
        layer['position'] = (final_x, final_y)
        
        # Update layers list
        self.update_layers_list()
        
        # Update preview
        self.display_preview_frame()
        
        # Update status
        filename = os.path.basename(layer['file_path'])
        self.status_label.config(text=f"Moved: {filename} to ({final_x}, {final_y}) - {positioning_mode}")
    
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
            self.selected_layer_index = selection[0]
            self.update_selected_layer_label()
            self.display_preview_frame()
        else:
            self.selected_layer_index = -1
            self.update_selected_layer_label()
    
    def move_layer_up(self):
        """Move selected layer up in the list."""
        if self.selected_layer_index > 0:
            # Swap with previous layer
            self.gif_layers[self.selected_layer_index], self.gif_layers[self.selected_layer_index - 1] = \
                self.gif_layers[self.selected_layer_index - 1], self.gif_layers[self.selected_layer_index]
            
            # Update selected index
            self.selected_layer_index -= 1
            
            # Update UI
            self.update_layers_list()
            self.layers_listbox.selection_clear(0, tk.END)
            self.layers_listbox.selection_set(self.selected_layer_index)
            self.display_preview_frame()
            self.status_label.config(text="Layer moved up")
    
    def move_layer_down(self):
        """Move selected layer down in the list."""
        if self.selected_layer_index < len(self.gif_layers) - 1:
            # Swap with next layer
            self.gif_layers[self.selected_layer_index], self.gif_layers[self.selected_layer_index + 1] = \
                self.gif_layers[self.selected_layer_index + 1], self.gif_layers[self.selected_layer_index]
            
            # Update selected index
            self.selected_layer_index += 1
            
            # Update UI
            self.update_layers_list()
            self.layers_listbox.selection_clear(0, tk.END)
            self.layers_listbox.selection_set(self.selected_layer_index)
            self.display_preview_frame()
            self.status_label.config(text="Layer moved down")
    
    def remove_selected_layer(self):
        """Remove selected layer."""
        if self.selected_layer_index != -1:
            del self.gif_layers[self.selected_layer_index]
            self.selected_layer_index = -1
            self.update_layers_list()
            self.update_selected_layer_label()
            self.display_preview_frame()
            self.status_label.config(text="Layer removed")
    
    def clear_all_layers(self):
        """Clear all layers."""
        self.gif_layers.clear()
        self.selected_layer_index = -1
        self.update_layers_list()
        self.update_selected_layer_label()
        self.display_preview_frame()
        self.status_label.config(text="All layers cleared")
    
    def update_selected_gifs_label(self):
        """Update the selected GIFs label."""
        count = len(self.gif_layers)
        if count == 0:
            self.selected_gifs_label.config(text="No GIFs selected")
        else:
            self.selected_gifs_label.config(text=f"{count} GIF(s) loaded")
    
    def update_selected_layer_label(self):
        """Update the selected layer label."""
        if self.selected_layer_index == -1:
            self.selected_layer_label.config(text="No layer selected")
        else:
            layer = self.gif_layers[self.selected_layer_index]
            filename = os.path.basename(layer['file_path'])
            x, y = layer['position']
            self.selected_layer_label.config(text=f"Selected: {filename} at ({x}, {y})")
    
    def update_frame_controls(self):
        """Update frame controls based on loaded layers."""
        if not self.gif_layers:
            self.frame_scale.config(to=0)
            self.frame_var.set("0")
            return
        
        # Find the maximum number of frames
        max_frames = max(len(layer['frames']) for layer in self.gif_layers)
        
        # Update frame scale
        self.frame_scale.config(to=max_frames - 1)
        self.frame_var.set("0")
        self.current_frame = 0
    
    def calculate_position(self, click_x, click_y, layer, positioning_mode):
        """Calculate the final position based on positioning mode."""
        # Get the current frame to get dimensions
        if layer['is_animated']:
            frame = layer['frames'][self.current_frame % len(layer['frames'])]
        else:
            frame = layer['frames'][0]
        
        width = frame.width
        height = frame.height
        
        if positioning_mode == "top-left":
            return (click_x, click_y)
        elif positioning_mode == "top-center":
            return (click_x - width // 2, click_y)
        elif positioning_mode == "top-right":
            return (click_x - width, click_y)
        elif positioning_mode == "center-left":
            return (click_x, click_y - height // 2)
        elif positioning_mode == "center":
            return (click_x - width // 2, click_y - height // 2)
        elif positioning_mode == "center-right":
            return (click_x - width, click_y - height // 2)
        elif positioning_mode == "bottom-left":
            return (click_x, click_y - height)
        elif positioning_mode == "bottom-center":
            return (click_x - width // 2, click_y - height)
        elif positioning_mode == "bottom-right":
            return (click_x - width, click_y - height)
        else:  # custom - same as top-left
            return (click_x, click_y)
    
    def update_quality_label(self, value):
        """Update quality label."""
        self.quality_label.config(text=str(int(float(value))))
    
    def display_preview_frame(self):
        """Display the current preview frame with all layers."""
        if not self.gif_layers:
            return
        
        try:
            # Find the maximum dimensions needed
            max_width = 0
            max_height = 0
            
            for layer in self.gif_layers:
                for frame in layer['frames']:
                    x, y = layer['position']
                    max_width = max(max_width, x + frame.width)
                    max_height = max(max_height, y + frame.height)
            
            # Create base frame
            if max_width > 0 and max_height > 0:
                base_frame = Image.new('RGBA', (max_width, max_height), (0, 0, 0, 0))
            else:
                # Fallback to a default size
                base_frame = Image.new('RGBA', (600, 400), (0, 0, 0, 0))
            
            # Add each layer in order
            for layer in self.gif_layers:
                if layer['is_animated']:
                    layer_frame = layer['frames'][self.current_frame % len(layer['frames'])]
                else:
                    layer_frame = layer['frames'][0]
                
                # Paste layer at its position
                x, y = layer['position']
                if layer_frame.mode == 'RGBA':
                    base_frame.paste(layer_frame, (x, y), layer_frame)
                else:
                    base_frame.paste(layer_frame, (x, y))
            
            # Display composite
            self.display_frame_on_canvas(base_frame)
                
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
        if not self.gif_layers:
            return
        
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_btn.config(text="⏸")
            self.start_play_loop()
        else:
            self.play_btn.config(text="▶")
    
    def start_play_loop(self):
        """Start the play loop."""
        if self.is_playing and self.gif_layers:
            self.display_preview_frame()
            
            # Find the maximum number of frames
            max_frames = max(len(layer['frames']) for layer in self.gif_layers) if self.gif_layers else 1
            self.current_frame = (self.current_frame + 1) % max_frames
            
            # Update frame controls
            self.frame_var.set(str(self.current_frame))
            self.frame_scale.set(self.current_frame)
            
            # Schedule next frame
            delay = int(1000 / (self.speed_var.get() * 10))
            self.parent.after(delay, self.start_play_loop)
    
    def on_frame_change(self, event):
        """Handle frame number change."""
        try:
            frame_num = int(self.frame_var.get())
            max_frames = max(len(layer['frames']) for layer in self.gif_layers) if self.gif_layers else 1
            if 0 <= frame_num < max_frames:
                self.current_frame = frame_num
                self.frame_scale.set(frame_num)
                self.display_preview_frame()
        except ValueError:
            pass
    
    def on_frame_scale_change(self, value):
        """Handle frame scale change."""
        try:
            frame_num = int(float(value))
            max_frames = max(len(layer['frames']) for layer in self.gif_layers) if self.gif_layers else 1
            if 0 <= frame_num < max_frames:
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
