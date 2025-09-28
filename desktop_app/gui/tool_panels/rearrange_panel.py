"""
Rearrange Tool Panel

GUI panel for the GIF rearrange tool with frame preview and drag-and-drop functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Callable, Any, List
import threading
from PIL import Image, ImageTk

from gif_tools.core.rearrange import rearrange_gif_frames


class RearrangePanel:
    """Panel for GIF rearrange operations with frame preview and drag-and-drop."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the rearrange panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.frames: List[Image.Image] = []
        self.frame_order: List[int] = []
        self.frame_thumbnails: List[ImageTk.PhotoImage] = []
        self.selected_frames: List[int] = []
        self.drag_start_index: Optional[int] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the rearrange panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Rearrange GIF Frames", padding="10")
        
        # Instructions
        instructions = "Load a GIF to see its frames. Drag frames to reorder them. Select multiple frames to move them together."
        ttk.Label(self.frame, text=instructions, wraplength=600, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Load GIF button
        load_frame = ttk.Frame(self.frame)
        load_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(load_frame, text="Load GIF", command=self.load_gif).pack(side=tk.LEFT, padx=(0, 10))
        self.file_label = ttk.Label(load_frame, text="No file loaded", foreground="gray")
        self.file_label.pack(side=tk.LEFT)
        
        # Frame preview area
        preview_frame = ttk.LabelFrame(self.frame, text="Frame Preview", padding="5")
        preview_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create canvas with scrollbar for frame preview
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, height=200, bg="white")
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame container
        self.frame_container = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(0, 0, anchor=tk.NW, window=self.frame_container)
        
        # Bind events for drag and drop
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Control buttons
        control_frame = ttk.Frame(self.frame)
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(control_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Clear Selection", command=self.clear_selection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Reset Order", command=self.reset_order).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Duplicate Selected", command=self.duplicate_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        
        # Quality controls
        quality_frame = ttk.Frame(self.frame)
        quality_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(
            quality_frame, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        quality_scale.pack(side=tk.LEFT, padx=(5, 0))
        
        self.quality_label = ttk.Label(quality_frame, text="85")
        self.quality_label.pack(side=tk.LEFT, padx=(5, 0))
        
        quality_scale.configure(command=self.update_quality_label)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame, 
            text="Rearrange GIF", 
            command=self.process_rearrange,
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
        self.frame.grid_rowconfigure(2, weight=1)
    
    def load_gif(self):
        """Load a GIF file and extract its frames."""
        file_path = filedialog.askopenfilename(
            title="Select GIF File",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Load GIF and extract frames
            gif = Image.open(file_path)
            self.frames = []
            self.frame_order = []
            
            # Extract all frames
            frame_index = 0
            while True:
                try:
                    gif.seek(frame_index)
                    frame = gif.copy()
                    self.frames.append(frame)
                    self.frame_order.append(frame_index)
                    frame_index += 1
                except EOFError:
                    break
            
            if not self.frames:
                messagebox.showerror("Error", "Could not extract frames from GIF!")
                return
            
            # Create thumbnails
            self.create_thumbnails()
            
            # Update UI
            self.file_label.config(text=f"Loaded: {Path(file_path).name} ({len(self.frames)} frames)")
            self.process_btn.config(state=tk.NORMAL)
            
            # Update canvas scroll region
            self.update_canvas_scroll()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GIF: {e}")
    
    def create_thumbnails(self):
        """Create thumbnails for all frames."""
        self.frame_thumbnails = []
        
        for frame in self.frames:
            # Resize frame to thumbnail size
            thumbnail = frame.copy()
            thumbnail.thumbnail((80, 80), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(thumbnail)
            self.frame_thumbnails.append(photo)
    
    def update_canvas_scroll(self):
        """Update the canvas scroll region."""
        self.frame_container.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def display_frames(self):
        """Display all frames in the canvas."""
        # Clear existing frames
        for widget in self.frame_container.winfo_children():
            widget.destroy()
        
        # Create frame labels
        for i, (frame_idx, thumbnail) in enumerate(zip(self.frame_order, self.frame_thumbnails)):
            frame_widget = ttk.Frame(self.frame_container, relief=tk.RAISED, borderwidth=1)
            frame_widget.grid(row=0, column=i, padx=2, pady=2)
            
            # Frame number label
            frame_label = ttk.Label(frame_widget, text=f"Frame {frame_idx}")
            frame_label.pack()
            
            # Thumbnail label
            thumb_label = ttk.Label(frame_widget, image=thumbnail)
            thumb_label.pack()
            
            # Store reference to frame widget
            frame_widget.frame_index = frame_idx
            frame_widget.grid_index = i
            
            # Bind click events
            frame_widget.bind("<Button-1>", lambda e, idx=i: self.on_frame_click(e, idx))
            frame_label.bind("<Button-1>", lambda e, idx=i: self.on_frame_click(e, idx))
            thumb_label.bind("<Button-1>", lambda e, idx=i: self.on_frame_click(e, idx))
        
        self.update_canvas_scroll()
    
    def on_frame_click(self, event, frame_index):
        """Handle frame click for selection."""
        if tk.EventType.ButtonPress:
            if event.state & 0x4:  # Ctrl key held
                # Toggle selection
                if frame_index in self.selected_frames:
                    self.selected_frames.remove(frame_index)
                else:
                    self.selected_frames.append(frame_index)
            else:
                # Select only this frame
                self.selected_frames = [frame_index]
            
            self.update_frame_display()
    
    def on_canvas_click(self, event):
        """Handle canvas click."""
        # Find which frame was clicked
        item = self.canvas.find_closest(event.x, event.y)[0]
        if item == self.canvas_window:
            return
        
        # Get the frame widget
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Find frame at this position
        for i, (frame_idx, _) in enumerate(zip(self.frame_order, self.frame_thumbnails)):
            if 0 <= x - i * 90 < 90:  # Approximate frame width
                self.drag_start_index = i
                break
    
    def on_canvas_drag(self, event):
        """Handle canvas drag."""
        if self.drag_start_index is not None:
            # Visual feedback during drag
            pass
    
    def on_canvas_release(self, event):
        """Handle canvas release (drop)."""
        if self.drag_start_index is not None:
            # Find drop position
            x = self.canvas.canvasx(event.x)
            drop_index = int(x // 90)  # Approximate frame width
            
            # Move frame(s)
            if self.selected_frames:
                # Move selected frames
                frames_to_move = [self.frame_order[i] for i in self.selected_frames]
                for frame_idx in frames_to_move:
                    self.frame_order.remove(frame_idx)
                
                # Insert at new position
                insert_pos = min(drop_index, len(self.frame_order))
                for frame_idx in reversed(frames_to_move):
                    self.frame_order.insert(insert_pos, frame_idx)
            else:
                # Move single frame
                frame_to_move = self.frame_order[self.drag_start_index]
                self.frame_order.pop(self.drag_start_index)
                
                insert_pos = min(drop_index, len(self.frame_order))
                self.frame_order.insert(insert_pos, frame_to_move)
            
            # Update display
            self.display_frames()
            self.selected_frames = []
            self.drag_start_index = None
    
    def update_frame_display(self):
        """Update the visual display of frames."""
        # Update frame colors based on selection
        for i, widget in enumerate(self.frame_container.winfo_children()):
            if hasattr(widget, 'frame_index'):
                if widget.frame_index in self.selected_frames:
                    widget.configure(relief=tk.SUNKEN, borderwidth=2)
                else:
                    widget.configure(relief=tk.RAISED, borderwidth=1)
    
    def select_all(self):
        """Select all frames."""
        self.selected_frames = list(range(len(self.frame_order)))
        self.update_frame_display()
    
    def clear_selection(self):
        """Clear frame selection."""
        self.selected_frames = []
        self.update_frame_display()
    
    def reset_order(self):
        """Reset frame order to original."""
        self.frame_order = list(range(len(self.frames)))
        self.display_frames()
    
    def duplicate_selected(self):
        """Duplicate selected frames."""
        if not self.selected_frames:
            messagebox.showwarning("Warning", "Please select frames to duplicate!")
            return
        
        # Add duplicates after selected frames
        new_frames = []
        for frame_idx in self.selected_frames:
            new_frames.append(self.frame_order[frame_idx])
        
        # Insert duplicates
        insert_pos = max(self.selected_frames) + 1
        for frame_idx in reversed(new_frames):
            self.frame_order.insert(insert_pos, frame_idx)
        
        self.display_frames()
    
    def remove_selected(self):
        """Remove selected frames."""
        if not self.selected_frames:
            messagebox.showwarning("Warning", "Please select frames to remove!")
            return
        
        if len(self.frame_order) - len(self.selected_frames) < 1:
            messagebox.showerror("Error", "Cannot remove all frames!")
            return
        
        # Remove selected frames
        frames_to_remove = [self.frame_order[i] for i in self.selected_frames]
        for frame_idx in frames_to_remove:
            self.frame_order.remove(frame_idx)
        
        self.selected_frames = []
        self.display_frames()
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current rearrange settings."""
        return {
            'frame_order': self.frame_order.copy(),
            'quality': self.quality_var.get()
        }
    
    def process_rearrange(self):
        """Process the rearrange operation."""
        try:
            if not self.frames:
                messagebox.showwarning("Warning", "Please load a GIF first!")
                return
            
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('rearrange', settings)
            else:
                messagebox.showinfo("Rearrange", f"Rearrange settings: {settings}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Rearrange failed: {e}")
    
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
