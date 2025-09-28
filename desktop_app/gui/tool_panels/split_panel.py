"""
Split Tool Panel with Media Player Interface

GUI panel for the GIF split tool with interactive media player controls and timeline.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Callable, Any
import threading
import time
from PIL import Image, ImageTk

from gif_tools.core.split import split_gif


class SplitPanel(ttk.Frame):
    """Panel for GIF split operations with media player interface."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None, file_path: Optional[str] = None):
        """
        Initialize the split panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
            file_path: Optional GIF file path to auto-load
        """
        super().__init__(parent)
        self.parent = parent
        self.on_process = on_process
        self.file_path = file_path
        
        # GIF data
        self.gif_frames = []
        self.current_frame = 0
        self.total_frames = 0
        self.is_playing = False
        self.play_thread = None
        self.frame_duration = 100  # ms
        
        # Selection markers
        self.start_marker = 0
        self.end_marker = 0
        self.is_dragging = False
        self.drag_type = None  # 'start' or 'end'
        
        self.setup_ui()
        
        # Auto-load GIF if provided
        if file_path:
            self.auto_load_gif(file_path)
    
    def setup_ui(self):
        """Create the split panel UI with media player interface."""
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Top section - GIF preview and controls
        self.create_preview_section()
        
        # Middle section - Timeline
        self.create_timeline_section()
        
        # Bottom section - Split options
        self.create_split_options_section()
    
    def create_preview_section(self):
        """Create the GIF preview and media controls section."""
        # Preview frame
        preview_frame = ttk.LabelFrame(self, text="GIF Preview", padding="10")
        preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)
        
        # Load button
        load_btn = ttk.Button(
            preview_frame, 
            text="Load GIF", 
            command=self.load_gif
        )
        load_btn.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Canvas for GIF display
        self.canvas = tk.Canvas(
            preview_frame, 
            width=400, 
            height=300, 
            bg='black',
            relief=tk.SUNKEN,
            bd=2
        )
        self.canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Media controls
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Play/Pause button
        self.play_btn = ttk.Button(
            controls_frame, 
            text="▶ Play", 
            command=self.toggle_play
        )
        self.play_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Stop button
        self.stop_btn = ttk.Button(
            controls_frame, 
            text="⏹ Stop", 
            command=self.stop_playback
        )
        self.stop_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Frame info
        self.frame_info = ttk.Label(controls_frame, text="Frame: 0 / 0")
        self.frame_info.grid(row=0, column=2, padx=(20, 0))
        
        # Speed control
        ttk.Label(controls_frame, text="Speed:").grid(row=0, column=3, padx=(20, 5))
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(
            controls_frame, 
            from_=0.1, 
            to=3.0, 
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            length=100
        )
        speed_scale.grid(row=0, column=4, padx=(0, 5))
        
        self.speed_label = ttk.Label(controls_frame, text="1.0x")
        self.speed_label.grid(row=0, column=5, padx=(5, 0))
        
        # Update speed label
        speed_scale.configure(command=self.update_speed_label)
    
    def create_timeline_section(self):
        """Create the timeline section with frame navigation."""
        timeline_frame = ttk.LabelFrame(self, text="Timeline & Frame Selection", padding="10")
        timeline_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        timeline_frame.grid_columnconfigure(0, weight=1)
        
        # Timeline canvas
        self.timeline_canvas = tk.Canvas(
            timeline_frame, 
            height=80, 
            bg='white',
            relief=tk.SUNKEN,
            bd=1
        )
        self.timeline_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Bind timeline events
        self.timeline_canvas.bind("<Button-1>", self.on_timeline_click)
        self.timeline_canvas.bind("<B1-Motion>", self.on_timeline_drag)
        self.timeline_canvas.bind("<ButtonRelease-1>", self.on_timeline_release)
        
        # Frame navigation controls
        nav_frame = ttk.Frame(timeline_frame)
        nav_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Previous frame
        ttk.Button(nav_frame, text="⏮", command=self.prev_frame).grid(row=0, column=0, padx=(0, 5))
        
        # Frame input
        ttk.Label(nav_frame, text="Go to frame:").grid(row=0, column=1, padx=(10, 5))
        self.frame_input_var = tk.StringVar()
        self.frame_input = ttk.Entry(nav_frame, textvariable=self.frame_input_var, width=8)
        self.frame_input.grid(row=0, column=2, padx=(0, 5))
        self.frame_input.bind("<Return>", self.go_to_frame)
        
        # Go button
        ttk.Button(nav_frame, text="Go", command=self.go_to_frame).grid(row=0, column=3, padx=(0, 5))
        
        # Next frame
        ttk.Button(nav_frame, text="⏭", command=self.next_frame).grid(row=0, column=4, padx=(5, 0))
        
        # Selection controls
        selection_frame = ttk.Frame(timeline_frame)
        selection_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Start marker
        ttk.Label(selection_frame, text="Start:").grid(row=0, column=0, padx=(0, 5))
        self.start_var = tk.StringVar(value="0")
        self.start_entry = ttk.Entry(selection_frame, textvariable=self.start_var, width=8)
        self.start_entry.grid(row=0, column=1, padx=(0, 10))
        self.start_entry.bind("<Return>", self.update_start_marker)
        
        # End marker
        ttk.Label(selection_frame, text="End:").grid(row=0, column=2, padx=(0, 5))
        self.end_var = tk.StringVar(value="0")
        self.end_entry = ttk.Entry(selection_frame, textvariable=self.end_var, width=8)
        self.end_entry.grid(row=0, column=3, padx=(0, 10))
        self.end_entry.bind("<Return>", self.update_end_marker)
        
        # Clear selection
        ttk.Button(selection_frame, text="Clear Selection", command=self.clear_selection).grid(row=0, column=4, padx=(10, 0))
        
        # Selection info
        self.selection_info = ttk.Label(selection_frame, text="Selected: 0 frames")
        self.selection_info.grid(row=0, column=5, padx=(20, 0))
    
    def create_split_options_section(self):
        """Create the split options section."""
        options_frame = ttk.LabelFrame(self, text="Split Options", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Split mode selection
        ttk.Label(options_frame, text="Split Mode:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.split_mode_var = tk.StringVar(value="extract_selected")
        mode_frame = ttk.Frame(options_frame)
        mode_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Mode options
        mode_options = [
            ("Split into Two GIFs", "split_two"),
            ("Extract Selected Region", "extract_selected"),
            ("Remove Selected Region", "remove_selected")
        ]
        
        for i, (text, value) in enumerate(mode_options):
            btn = ttk.Radiobutton(
                mode_frame, 
                text=text, 
                variable=self.split_mode_var, 
                value=value,
                command=self.update_split_mode
            )
            btn.grid(row=0, column=i, padx=(0, 15), sticky=tk.W)
        
        # All modes now output GIF files only
        info_label = ttk.Label(options_frame, text="Output: GIF files only", font=("Arial", 9, "italic"))
        info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Split button
        self.split_btn = ttk.Button(
            options_frame, 
            text="Split Selected Frames", 
            command=self.process_split,
            state=tk.DISABLED
        )
        self.split_btn.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            options_frame, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Initialize mode
        self.update_split_mode()
    
    def auto_load_gif(self, file_path: str):
        """Auto-load GIF when file path is provided."""
        self.file_path = file_path
        self.load_gif()
    
    def load_gif(self):
        """Load a GIF file for splitting."""
        if not self.file_path:
            file_path = filedialog.askopenfilename(
                title="Select GIF file",
                filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
            )
            if not file_path:
                return
            self.file_path = file_path
        
        try:
            # Load GIF frames
            gif = Image.open(self.file_path)
            self.gif_frames = []
            self.total_frames = 0
            
            # Extract all frames
            while True:
                try:
                    frame = gif.copy()
                    self.gif_frames.append(frame)
                    self.total_frames += 1
                    gif.seek(gif.tell() + 1)
                except EOFError:
                    break
            
            if not self.gif_frames:
                messagebox.showerror("Error", "No frames found in GIF")
                return
            
            # Reset to first frame
            self.current_frame = 0
            self.start_marker = 0
            self.end_marker = min(10, self.total_frames - 1)
            
            # Update UI
            self.update_frame_display()
            self.update_timeline()
            self.update_selection_info()
            self.split_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GIF: {e}")
    
    def update_frame_display(self):
        """Update the frame display on canvas."""
        if not self.gif_frames or self.current_frame >= len(self.gif_frames):
            return
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Get current frame
        frame = self.gif_frames[self.current_frame]
        
        # Calculate display size (fit to canvas)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready, schedule update
            self.after(100, self.update_frame_display)
            return
        
        # Calculate scale to fit
        scale_x = canvas_width / frame.width
        scale_y = canvas_height / frame.height
        scale = min(scale_x, scale_y, 1.0)  # Don't scale up
        
        new_width = int(frame.width * scale)
        new_height = int(frame.height * scale)
        
        # Resize frame
        resized_frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(resized_frame)
        
        # Center on canvas
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        
        # Display image
        self.canvas.create_image(x, y, anchor=tk.NW, image=photo)
        self.canvas.image = photo  # Keep reference
        
        # Update frame info
        self.frame_info.config(text=f"Frame: {self.current_frame + 1} / {self.total_frames}")
        self.frame_input_var.set(str(self.current_frame))
    
    def update_timeline(self):
        """Update the timeline display."""
        if not self.gif_frames:
            return
        
        mode = self.split_mode_var.get()
        if mode == "split_two":
            self.update_timeline_for_split_two()
            return
        
        self.timeline_canvas.delete("all")
        
        canvas_width = self.timeline_canvas.winfo_width()
        canvas_height = self.timeline_canvas.winfo_height()
        
        if canvas_width <= 1:
            self.after(100, self.update_timeline)
            return
        
        # Draw timeline
        timeline_width = canvas_width - 20
        timeline_height = 40
        timeline_x = 10
        timeline_y = (canvas_height - timeline_height) // 2
        
        # Timeline background
        self.timeline_canvas.create_rectangle(
            timeline_x, timeline_y, 
            timeline_x + timeline_width, timeline_y + timeline_height,
            fill='lightgray', outline='black'
        )
        
        # Frame markers
        frame_width = timeline_width / self.total_frames
        for i in range(0, self.total_frames, max(1, self.total_frames // 20)):
            x = timeline_x + i * frame_width
            self.timeline_canvas.create_line(
                x, timeline_y, x, timeline_y + timeline_height,
                fill='black', width=1
            )
        
        # Current frame indicator
        current_x = timeline_x + self.current_frame * frame_width
        self.timeline_canvas.create_line(
            current_x, timeline_y - 5, current_x, timeline_y + timeline_height + 5,
            fill='red', width=3
        )
        
        # Selection markers
        start_x = timeline_x + self.start_marker * frame_width
        end_x = timeline_x + self.end_marker * frame_width
        
        # Selection area
        self.timeline_canvas.create_rectangle(
            start_x, timeline_y, end_x, timeline_y + timeline_height,
            fill='blue', stipple='gray50', outline='blue'
        )
        
        # Start marker
        self.timeline_canvas.create_line(
            start_x, timeline_y - 10, start_x, timeline_y + timeline_height + 10,
            fill='green', width=4
        )
        
        # End marker
        self.timeline_canvas.create_line(
            end_x, timeline_y - 10, end_x, timeline_y + timeline_height + 10,
            fill='red', width=4
        )
    
    def update_timeline_for_split_two(self):
        """Update timeline display for split into two mode."""
        if not self.gif_frames:
            return
        
        self.timeline_canvas.delete("all")
        
        canvas_width = self.timeline_canvas.winfo_width()
        canvas_height = self.timeline_canvas.winfo_height()
        
        if canvas_width <= 1:
            self.after(100, self.update_timeline_for_split_two)
            return
        
        # Draw timeline
        timeline_width = canvas_width - 20
        timeline_height = 40
        timeline_x = 10
        timeline_y = (canvas_height - timeline_height) // 2
        
        # Timeline background
        self.timeline_canvas.create_rectangle(
            timeline_x, timeline_y, 
            timeline_x + timeline_width, timeline_y + timeline_height,
            fill='lightgray', outline='black'
        )
        
        # Frame markers
        frame_width = timeline_width / self.total_frames
        for i in range(0, self.total_frames, max(1, self.total_frames // 20)):
            x = timeline_x + i * frame_width
            self.timeline_canvas.create_line(
                x, timeline_y, x, timeline_y + timeline_height,
                fill='black', width=1
            )
        
        # Current frame indicator
        current_x = timeline_x + self.current_frame * frame_width
        self.timeline_canvas.create_line(
            current_x, timeline_y - 5, current_x, timeline_y + timeline_height + 5,
            fill='red', width=3
        )
        
        # Split point marker (single line)
        split_x = timeline_x + self.current_frame * frame_width
        self.timeline_canvas.create_line(
            split_x, timeline_y - 10, split_x, timeline_y + timeline_height + 10,
            fill='orange', width=6
        )
        
        # Add split point label
        self.timeline_canvas.create_text(
            split_x, timeline_y - 20,
            text="SPLIT", fill='orange', font=('Arial', 8, 'bold')
        )
    
    def on_timeline_click(self, event):
        """Handle timeline click for frame navigation."""
        if not self.gif_frames:
            return
        
        canvas_width = self.timeline_canvas.winfo_width()
        timeline_width = canvas_width - 20
        frame_width = timeline_width / self.total_frames
        
        # Calculate clicked frame
        click_x = event.x - 10
        frame_index = int(click_x / frame_width)
        frame_index = max(0, min(frame_index, self.total_frames - 1))
        
        self.current_frame = frame_index
        
        # Update based on mode
        mode = self.split_mode_var.get()
        if mode == "split_two":
            # For split_two mode, just update the split point
            self.update_frame_display()
            self.update_timeline_for_split_two()
            self.update_selection_info_for_split_two()
        else:
            # For other modes, update normally
            self.update_frame_display()
            self.update_timeline()
    
    def on_timeline_drag(self, event):
        """Handle timeline drag for marker adjustment."""
        if not self.gif_frames:
            return
        
        canvas_width = self.timeline_canvas.winfo_width()
        timeline_width = canvas_width - 20
        frame_width = timeline_width / self.total_frames
        
        # Calculate dragged frame
        drag_x = event.x - 10
        frame_index = int(drag_x / frame_width)
        frame_index = max(0, min(frame_index, self.total_frames - 1))
        
        # Determine which marker to move based on proximity
        start_x = 10 + self.start_marker * frame_width
        end_x = 10 + self.end_marker * frame_width
        
        if abs(event.x - start_x) < abs(event.x - end_x):
            self.start_marker = frame_index
            if self.start_marker > self.end_marker:
                self.end_marker = self.start_marker
        else:
            self.end_marker = frame_index
            if self.end_marker < self.start_marker:
                self.start_marker = self.end_marker
        
        self.update_timeline()
        self.update_selection_info()
        self.start_var.set(str(self.start_marker))
        self.end_var.set(str(self.end_marker))
    
    def on_timeline_release(self, event):
        """Handle timeline release."""
        pass
    
    def toggle_play(self):
        """Toggle play/pause of GIF animation."""
        if not self.gif_frames:
            return
        
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """Start playing the GIF animation."""
        if not self.gif_frames or self.is_playing:
            return
        
        self.is_playing = True
        self.play_btn.config(text="⏸ Pause")
        
        def play_loop():
            while self.is_playing and self.gif_frames:
                self.current_frame = (self.current_frame + 1) % self.total_frames
                self.update_frame_display()
                self.update_timeline()
                
                # Calculate delay based on speed
                delay = int(self.frame_duration / self.speed_var.get())
                time.sleep(delay / 1000.0)
        
        self.play_thread = threading.Thread(target=play_loop, daemon=True)
        self.play_thread.start()
    
    def stop_playback(self):
        """Stop playing the GIF animation."""
        self.is_playing = False
        self.play_btn.config(text="▶ Play")
    
    def prev_frame(self):
        """Go to previous frame."""
        if not self.gif_frames:
            return
        
        self.stop_playback()
        self.current_frame = (self.current_frame - 1) % self.total_frames
        self.update_frame_display()
        self.update_timeline()
    
    def next_frame(self):
        """Go to next frame."""
        if not self.gif_frames:
            return
        
        self.stop_playback()
        self.current_frame = (self.current_frame + 1) % self.total_frames
        self.update_frame_display()
        self.update_timeline()
    
    def go_to_frame(self, event=None):
        """Go to specific frame."""
        if not self.gif_frames:
            return
        
        try:
            frame_num = int(self.frame_input_var.get())
            frame_num = max(0, min(frame_num, self.total_frames - 1))
            self.current_frame = frame_num
            self.update_frame_display()
            self.update_timeline()
        except ValueError:
            pass
    
    def update_start_marker(self, event=None):
        """Update start marker from entry."""
        try:
            start = int(self.start_var.get())
            start = max(0, min(start, self.total_frames - 1))
            self.start_marker = start
            if self.start_marker > self.end_marker:
                self.end_marker = self.start_marker
                self.end_var.set(str(self.end_marker))
            self.update_timeline()
            self.update_selection_info()
        except ValueError:
            pass
    
    def update_end_marker(self, event=None):
        """Update end marker from entry."""
        try:
            end = int(self.end_var.get())
            end = max(0, min(end, self.total_frames - 1))
            self.end_marker = end
            if self.end_marker < self.start_marker:
                self.start_marker = self.end_marker
                self.start_var.set(str(self.start_marker))
            self.update_timeline()
            self.update_selection_info()
        except ValueError:
            pass
    
    def clear_selection(self):
        """Clear frame selection."""
        self.start_marker = 0
        self.end_marker = 0
        self.start_var.set("0")
        self.end_var.set("0")
        self.update_timeline()
        self.update_selection_info()
    
    def update_selection_info(self):
        """Update selection information display."""
        mode = self.split_mode_var.get()
        if mode == "split_two":
            self.update_selection_info_for_split_two()
            return
        
        selected_frames = self.end_marker - self.start_marker + 1
        self.selection_info.config(text=f"Selected: {selected_frames} frames")
    
    def update_selection_info_for_split_two(self):
        """Update selection info for split into two mode."""
        part1_frames = self.current_frame
        part2_frames = self.total_frames - self.current_frame
        self.selection_info.config(text=f"Part 1: {part1_frames} frames | Part 2: {part2_frames} frames")
    
    def update_speed_label(self, value):
        """Update speed label when scale changes."""
        self.speed_label.config(text=f"{float(value):.1f}x")
    
    
    def update_split_mode(self):
        """Update UI based on selected split mode."""
        mode = self.split_mode_var.get()
        
        if mode == "split_two":
            # For splitting into two GIFs, update timeline
            self.split_btn.config(text="Split into Two GIFs")
            self.update_timeline_for_split_two()
        else:
            # For extract/remove modes, update timeline
            if mode == "extract_selected":
                self.split_btn.config(text="Extract Selected Region")
            else:  # remove_selected
                self.split_btn.config(text="Remove Selected Region")
            self.update_timeline()
    
    def get_settings(self) -> dict:
        """Get current split settings."""
        mode = self.split_mode_var.get()
        
        if mode == "split_two":
            return {
                'split_mode': mode,
                'start_frame': self.current_frame,  # Split point
                'end_frame': self.current_frame,    # Same as start for split point
                'output_format': 'gif',  # Always GIF
                'quality': 95,
                'naming_pattern': 'frame_{index:04d}'
            }
        else:
            return {
                'split_mode': mode,
                'start_frame': self.start_marker,
                'end_frame': self.end_marker,
                'output_format': 'gif',  # Always GIF
                'quality': 95,
                'naming_pattern': 'frame_{index:04d}'
            }
    
    def process_split(self):
        """Process the split operation."""
        if not self.gif_frames:
            messagebox.showerror("Error", "Please load a GIF first")
            return
        
        try:
            settings = self.get_settings()
            
            if self.on_process:
                self.on_process('split', settings, self.file_path)
            else:
                messagebox.showinfo("Split", f"Split settings: {settings}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Split failed: {e}")
    
    def start_progress(self):
        """Start the progress bar."""
        self.progress_bar.start()
        self.split_btn.config(state=tk.DISABLED)
    
    def stop_progress(self):
        """Stop the progress bar."""
        self.progress_bar.stop()
        self.split_btn.config(state=tk.NORMAL)
    