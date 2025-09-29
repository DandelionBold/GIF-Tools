#!/usr/bin/env python3
"""
GIF-Tools Desktop Application

A comprehensive desktop GUI application for GIF manipulation with 17 powerful tools.
Built with Tkinter for cross-platform compatibility.

Author: Kamal Nady
License: MIT
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import threading
import queue
import time

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gif_tools.core import (
    # Basic tools
    convert_video_to_gif, resize_gif, rotate_gif, crop_gif, split_gif, merge_gifs,
    # Advanced tools
    add_text_to_gif, rearrange_gif_frames, reverse_gif, optimize_gif, 
    change_gif_speed, apply_gif_filter,
    # Additional tools
    extract_gif_frames, set_gif_loop_count, convert_gif_format, 
    process_gif_batch,
    # Split modes
    split_gif_into_two, extract_gif_region, remove_gif_region
)
from desktop_app.gui.tool_panels import (
    RearrangePanel,
    VideoToGifPanel,
    AddTextPanel
)
from gif_tools.utils import validate_animated_file, get_supported_extensions


class GifToolsApp:
    """Main application class for GIF-Tools desktop GUI."""
    
    def __init__(self):
        """Initialize the GIF-Tools application."""
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.setup_menus()
        self.setup_status_bar()
        
        # File handling
        self.current_file: Optional[Path] = None
        self.output_dir: Optional[Path] = None
        
        # Processing queue for background operations
        self.processing_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.is_processing = False
        
        # Start background processing thread
        self.start_background_processing()
    
    def setup_window(self):
        """Configure the main window."""
        self.root.title("GIF-Tools - Professional GIF Manipulation Suite")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Set window icon (if available)
        try:
            icon_path = project_root / "desktop_app" / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass  # Icon not critical
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def setup_variables(self):
        """Initialize Tkinter variables."""
        # File variables
        self.input_file_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        
        # Progress variables
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        
        # Tool-specific variables
        self.tool_vars = {}
    
    def setup_ui(self):
        """Create the main user interface."""
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        self.create_main_content()
        
        # Create tool panels
        self.create_tool_panels()
    
    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # File operations
        ttk.Button(toolbar, text="Open GIF", command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save As", command=self.save_as).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Output directory
        ttk.Label(toolbar, text="Output:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(toolbar, textvariable=self.output_dir_var, width=30).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Browse", command=self.browse_output_dir).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Stop button
        self.stop_btn = ttk.Button(toolbar, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    def create_main_content(self):
        """Create the main content area with notebook for tools."""
        # Create notebook for tool panels
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create tool categories
        self.create_basic_tools_tab()
        self.create_advanced_tools_tab()
        self.create_additional_tools_tab()
    
    def create_basic_tools_tab(self):
        """Create the basic tools tab."""
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="Basic Tools")
        
        # Create tool buttons
        tools = [
            ("Video to GIF", self.open_video_to_gif_dialog),
            ("Resize", self.open_resize_dialog),
            ("Rotate", self.open_rotate_dialog),
            ("Crop", self.open_crop_dialog),
            ("Split", self.open_split_dialog),
            ("Merge", self.open_merge_dialog),
        ]
        
        for i, (name, command) in enumerate(tools):
            row, col = divmod(i, 2)
            btn = ttk.Button(basic_frame, text=name, command=command, width=20)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        for i in range(2):
            basic_frame.grid_columnconfigure(i, weight=1)
    
    def create_advanced_tools_tab(self):
        """Create the advanced tools tab."""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Advanced Tools")
        
        # Create tool buttons
        tools = [
            ("Add Text", self.open_add_text_dialog),
            ("Rearrange Frames", self.open_rearrange_dialog),
            ("Reverse", self.open_reverse_dialog),
            ("Optimize", self.open_optimize_dialog),
            ("Speed Control", self.open_speed_dialog),
            ("Filter Effects", self.open_filter_dialog),
        ]
        
        for i, (name, command) in enumerate(tools):
            row, col = divmod(i, 2)
            btn = ttk.Button(advanced_frame, text=name, command=command)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        for i in range(2):
            advanced_frame.grid_columnconfigure(i, weight=1)
    
    def create_additional_tools_tab(self):
        """Create the additional tools tab."""
        additional_frame = ttk.Frame(self.notebook)
        self.notebook.add(additional_frame, text="Additional Tools")
        
        # Create tool buttons
        tools = [
            ("Extract Frames", self.open_extract_frames_dialog),
            ("Loop Settings", self.open_loop_settings_dialog),
            ("Format Conversion", self.open_format_conversion_dialog),
            ("Watermark", self.open_watermark_dialog),
        ]
        
        for i, (name, command) in enumerate(tools):
            row, col = divmod(i, 2)
            btn = ttk.Button(additional_frame, text=name, command=command)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        for i in range(2):
            additional_frame.grid_columnconfigure(i, weight=1)
    
    
    def create_tool_panels(self):
        """Create individual tool panels (placeholder for now)."""
        # This will be expanded with specific tool panels
        pass
    
    def setup_menus(self):
        """Create the application menus."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open GIF", command=self.open_file)
        file_menu.add_command(label="Save As", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Basic tools submenu
        basic_menu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="Basic Tools", menu=basic_menu)
        basic_menu.add_command(label="Video to GIF", command=self.open_video_to_gif_dialog)
        basic_menu.add_command(label="Resize", command=self.open_resize_dialog)
        basic_menu.add_command(label="Rotate", command=self.open_rotate_dialog)
        basic_menu.add_command(label="Crop", command=self.open_crop_dialog)
        basic_menu.add_command(label="Split", command=self.open_split_dialog)
        basic_menu.add_command(label="Merge", command=self.open_merge_dialog)
        
        # Advanced tools submenu
        advanced_menu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="Advanced Tools", menu=advanced_menu)
        advanced_menu.add_command(label="Add Text", command=self.open_add_text_dialog)
        advanced_menu.add_command(label="Rearrange Frames", command=self.open_rearrange_dialog)
        advanced_menu.add_command(label="Reverse", command=self.open_reverse_dialog)
        advanced_menu.add_command(label="Optimize", command=self.open_optimize_dialog)
        advanced_menu.add_command(label="Speed Control", command=self.open_speed_dialog)
        advanced_menu.add_command(label="Filter Effects", command=self.open_filter_dialog)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
    
    def setup_status_bar(self):
        """Create the status bar."""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    def start_background_processing(self):
        """Start the background processing thread."""
        def process_worker():
            while True:
                task = None
                try:
                    task = self.processing_queue.get(timeout=1)
                    if task is None:
                        break
                    
                    self.is_processing = True
                    self.root.after(0, lambda: self.status_var.set("Processing..."))
                    
                    # Execute the task
                    result = task['function'](*task['args'], **task['kwargs'])
                    
                    # Put result in result queue
                    self.result_queue.put({
                        'success': True,
                        'result': result,
                        'task_id': task.get('task_id')
                    })
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.result_queue.put({
                        'success': False,
                        'error': str(e),
                        'task_id': task.get('task_id') if task else None
                    })
                finally:
                    self.is_processing = False
                    if task is not None:
                        self.processing_queue.task_done()
        
        self.processing_thread = threading.Thread(target=process_worker, daemon=True)
        self.processing_thread.start()
        
        # Start result processing
        self.check_results()
    
    def check_results(self):
        """Check for processing results."""
        try:
            while True:
                result = self.result_queue.get_nowait()
                if result['success']:
                    self.handle_success(result)
                else:
                    self.handle_error(result)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_results)
    
    def handle_success(self, result):
        """Handle successful processing result."""
        self.status_var.set("Processing completed successfully!")
        self.progress_var.set(100)
        self.set_buttons_state(True)  # Re-enable buttons
        messagebox.showinfo("Success", "File processed successfully!")
    
    def handle_error(self, result):
        """Handle processing error."""
        self.status_var.set("Processing failed!")
        self.progress_var.set(0)
        self.set_buttons_state(True)  # Re-enable buttons
        messagebox.showerror("Error", f"Processing failed: {result['error']}")
    
    def set_buttons_state(self, enabled: bool):
        """Enable or disable buttons during processing."""
        state = "normal" if enabled else "disabled"
        
        # Disable/enable process and stop buttons
        if hasattr(self, 'process_btn'):
            # Process button was removed, no action needed
            pass
        if hasattr(self, 'stop_btn'):
            # Stop button is enabled when processing, disabled when not
            self.stop_btn.config(state="normal" if not enabled else "disabled")
        
        # Disable/enable all buttons in the notebook tabs
        try:
            # Get all frames in the notebook
            for tab_id in self.notebook.tabs():
                frame = self.notebook.nametowidget(tab_id)
                # Find all buttons in this frame and its children
                self._disable_buttons_in_widget(frame, state)
        except Exception:
            # If there's an error accessing notebook, continue
            pass
    
    def _disable_buttons_in_widget(self, widget, state):
        """Recursively disable/enable buttons in a widget and its children."""
        try:
            if isinstance(widget, ttk.Button):
                widget.config(state=state)
            elif hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    self._disable_buttons_in_widget(child, state)
        except Exception:
            # If there's an error with a widget, continue
            pass
    
    def stop_processing(self):
        """Stop current processing operation."""
        if self.is_processing:
            self.is_processing = False
            self.status_var.set("Stopping processing...")
            # Clear the processing queue
            while not self.processing_queue.empty():
                try:
                    self.processing_queue.get_nowait()
                except queue.Empty:
                    break
            self.set_buttons_state(True)
            self.status_var.set("Processing stopped.")
            self.progress_var.set(0)
    
    def process_tool(self, tool_name: str, settings: dict, input_file: Optional[str] = None):
        """Process a tool operation."""
        # Special handling for merge tool - it doesn't need a main file loaded
        if tool_name == 'merge':
            # For merge tool, check if files are provided in settings
            if not settings.get('file_list'):
                messagebox.showwarning("Warning", "Please add files to merge!")
                return
        else:
            # For other tools, check if a file is loaded
            if not self.current_file and not input_file:
                messagebox.showwarning("Warning", "No file loaded!")
                return
            
            input_path = input_file or self.current_file
            if not input_path:
                messagebox.showwarning("Warning", "No input file specified!")
                return
        
        # Get output path
        if not self.output_dir_var.get():
            messagebox.showwarning("Warning", "Please select an output directory!")
            return
        
        output_dir = Path(self.output_dir_var.get())
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename based on tool type
        if tool_name == 'merge':
            # For merge tool, create a generic output filename
            output_filename = f"merged_{tool_name}.gif"
            output_path = output_dir / output_filename
        else:
            # For other tools, use the input file name
            input_file_path = Path(input_path)
            if tool_name == 'video_to_gif':
                output_filename = f"{input_file_path.stem}_{tool_name}.gif"
                output_path = output_dir / output_filename
            elif tool_name == 'split':
                # Split tool outputs to a directory, not a single file
                output_path = output_dir / f"{input_file_path.stem}_frames"
            else:
                output_filename = f"{input_file_path.stem}_{tool_name}{input_file_path.suffix}"
                output_path = output_dir / output_filename
        
        # Add to processing queue
        if tool_name == 'merge':
            # For merge tool, we don't have a single input path
            task = {
                'function': self._execute_tool,
                'args': (tool_name, None, str(output_path), settings),
                'kwargs': {},
                'task_id': f"{tool_name}_{int(time.time())}"
            }
        else:
            # For other tools, use the input path
            task = {
                'function': self._execute_tool,
                'args': (tool_name, str(input_path), str(output_path), settings),
                'kwargs': {},
                'task_id': f"{tool_name}_{int(time.time())}"
            }
        
        self.processing_queue.put(task)
        self.status_var.set(f"Processing {tool_name}...")
        self.progress_var.set(0)
        
        # Disable buttons during processing
        self.set_buttons_state(False)
    
    def _execute_tool(self, tool_name: str, input_path: str, output_path: str, settings: dict):
        """Execute a specific tool."""
        try:
            # Create progress callback
            def progress_callback(progress: int, message: str):
                self.root.after(0, lambda: self._update_progress(progress, message))
            
            if tool_name == 'rearrange':
                return rearrange_gif_frames(input_path, output_path,
                                          frame_order=settings['frame_order'],
                                          quality=settings.get('quality', 85),
                                          progress_callback=progress_callback)
            elif tool_name == 'video_to_gif':
                return convert_video_to_gif(
                    video_path=input_path,
                    output_path=output_path,
                    fps=settings.get('fps', 10),
                    duration=settings.get('duration'),
                    start_time=settings.get('start_time', 0.0),
                    quality=settings.get('quality', 85),
                    width=settings.get('width'),
                    height=settings.get('height'),
                    optimize=settings.get('optimize', True),
                    loop_count=settings.get('loop_count', 0),
                    progress_callback=progress_callback
                )
            elif tool_name == 'resize':
                return resize_gif(
                    input_path=input_path,
                    output_path=output_path,
                    width=settings.get('width'),
                    height=settings.get('height'),
                    size=settings.get('size'),
                    maintain_aspect_ratio=settings.get('maintain_aspect_ratio', True),
                    resample=settings.get('resample', 1),  # LANCZOS
                    quality=settings.get('quality', 85),
                    progress_callback=progress_callback
                )
            elif tool_name == 'rotate':
                return rotate_gif(
                    input_path=input_path,
                    output_path=output_path,
                    angle=settings.get('angle', 90),
                    quality=settings.get('quality', 85),
                    progress_callback=progress_callback
                )
            elif tool_name == 'crop':
                return crop_gif(
                    input_path=input_path,
                    output_path=output_path,
                    x=settings.get('x', 0),
                    y=settings.get('y', 0),
                    width=settings.get('width', 100),
                    height=settings.get('height', 100),
                    quality=settings.get('quality', 85),
                    progress_callback=progress_callback
                )
            elif tool_name == 'split':
                split_mode = settings.get('split_mode', 'extract_selected')
                
                if split_mode == 'split_two':
                    # Split into two GIFs at the start frame
                    return split_gif_into_two(
                        input_path=input_path,
                        output_dir=Path(output_path),
                        split_frame=settings.get('start_frame', 0),
                        progress_callback=progress_callback
                    )
                elif split_mode == 'extract_selected':
                    # Extract selected region as GIF
                    output_file = Path(output_path) / f"{Path(input_path).stem}_extracted.gif"
                    return extract_gif_region(
                        input_path=input_path,
                        output_path=output_file,
                        start_frame=settings.get('start_frame', 0),
                        end_frame=settings.get('end_frame', 10),
                        progress_callback=progress_callback
                    )
                elif split_mode == 'remove_selected':
                    # Remove selected region, keep the rest as GIF
                    output_file = Path(output_path) / f"{Path(input_path).stem}_removed.gif"
                    return remove_gif_region(
                        input_path=input_path,
                        output_path=output_file,
                        start_frame=settings.get('start_frame', 0),
                        end_frame=settings.get('end_frame', 10),
                        progress_callback=progress_callback
                    )
                else:
                    # Fallback to original split (extract frames as images)
                    return split_gif(
                        input_path=input_path,
                        output_dir=Path(output_path),
                        start_frame=settings.get('start_frame', 0),
                        end_frame=settings.get('end_frame', 10),
                        output_format=settings.get('output_format', 'png'),
                        naming_pattern=settings.get('naming_pattern', 'frame_{index:04d}'),
                        progress_callback=progress_callback
                    )
            elif tool_name == 'merge':
                # Merge multiple GIFs/images into one
                merge_mode = settings.get('mode', 'sequential')
                
                if merge_mode == 'sequential':
                    # Sequential merge - one after another
                    from gif_tools.core.merge import merge_gifs_sequential
                    return merge_gifs_sequential(
                        input_paths=settings.get('file_list', []),
                        output_path=output_path,
                        frame_duration=settings.get('duration', 100),
                        loop_count=settings.get('loop_count', 0),
                        quality=settings.get('quality', 85),
                        progress_callback=progress_callback
                    )
                else:
                    # Horizontal or vertical merge
                    return merge_gifs(
                        input_paths=settings.get('file_list', []),
                        output_path=output_path,
                        direction=settings.get('mode', 'horizontal'),
                        frame_duration=settings.get('duration', 100),
                        loop_count=settings.get('loop_count', 0),
                        quality=settings.get('quality', 85)
                    )
            elif tool_name == 'add_text':
                # Add text to GIF
                return add_text_to_gif(
                    input_path=input_file_path,
                    output_path=output_path,
                    text=settings.get('text', ''),
                    position=settings.get('position', (10, 10)),
                    font_family=settings.get('font_family', 'Arial'),
                    font_size=settings.get('font_size', 24),
                    color=settings.get('color', 'white'),
                    alignment=settings.get('alignment', 'left'),
                    background_color=settings.get('background_color'),
                    background_opacity=settings.get('background_opacity', 0.0),
                    stroke_width=settings.get('stroke_width', 0),
                    stroke_color=settings.get('stroke_color', 'black'),
                    quality=settings.get('quality', 85)
                )
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            raise Exception(f"Tool execution failed: {e}")
    
    def _update_progress(self, progress: int, message: str):
        """Update progress bar and status message."""
        self.progress_var.set(progress)
        self.status_var.set(message)
    
    # File operations
    def open_file(self):
        """Open a GIF file."""
        file_path = filedialog.askopenfilename(
            title="Open GIF File",
            filetypes=[
                ("GIF files", "*.gif"),
                ("All supported", "*.gif;*.webp;*.apng"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_file = Path(file_path)
            self.input_file_var.set(str(self.current_file))
            # Process button was removed, no action needed
            self.status_var.set(f"Loaded: {self.current_file.name}")
    
    def save_as(self):
        """Save the current file as a new file."""
        if not self.current_file:
            messagebox.showwarning("Warning", "No file loaded!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".gif",
            filetypes=[
                ("GIF files", "*.gif"),
                ("WebP files", "*.webp"),
                ("APNG files", "*.apng"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.output_file_var.set(file_path)
            self.status_var.set(f"Output: {Path(file_path).name}")
    
    def browse_output_dir(self):
        """Browse for output directory."""
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir_var.set(dir_path)
            self.output_dir = Path(dir_path)
    
    # Tool dialog methods
    def open_video_to_gif_dialog(self):
        """Open video to GIF conversion dialog."""
        self._open_tool_dialog("Video to GIF Converter", VideoToGifPanel)
    
    def open_resize_dialog(self):
        """Open resize dialog."""
        from desktop_app.gui.tool_panels.resize_panel import ResizePanel
        
        dialog = tk.Toplevel(self.root)
        dialog.title("GIF Resize Tool")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        dialog.minsize(600, 500)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create resize panel
        resize_panel = ResizePanel(dialog, self.process_tool)
        resize_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def open_rotate_dialog(self):
        """Open rotate dialog."""
        from desktop_app.gui.tool_panels.rotate_panel import RotatePanel
        
        dialog = tk.Toplevel(self.root)
        dialog.title("GIF Rotate Tool")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        dialog.minsize(600, 500)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create rotate panel
        rotate_panel = RotatePanel(dialog, self.process_tool)
        rotate_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def open_crop_dialog(self):
        """Open crop dialog."""
        from desktop_app.gui.tool_panels.crop_panel import CropPanel
        
        dialog = tk.Toplevel(self.root)
        dialog.title("GIF Crop Tool")
        dialog.geometry("800x700")
        dialog.resizable(True, True)
        dialog.minsize(800, 700)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create crop panel with current file
        crop_panel = CropPanel(dialog, self.process_tool, self.current_file)
        crop_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def open_split_dialog(self):
        """Open split dialog."""
        from desktop_app.gui.tool_panels.split_panel import SplitPanel
        
        dialog = tk.Toplevel(self.root)
        dialog.title("GIF Split Tool - Media Player")
        dialog.geometry("900x700")
        dialog.resizable(True, True)
        dialog.minsize(900, 700)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create split panel
        split_panel = SplitPanel(dialog, self.process_tool, self.current_file)
        split_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def open_merge_dialog(self):
        """Open merge dialog."""
        from desktop_app.gui.tool_panels.merge_panel import MergePanel
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("GIF Merge Tool")
        dialog.geometry("800x700")
        dialog.resizable(True, True)
        dialog.minsize(600, 500)
        
        # Create merge panel
        merge_panel = MergePanel(dialog, self.process_tool)
        
        # Pack the panel
        merge_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center on parent window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def open_reverse_dialog(self):
        """Open reverse dialog."""
        messagebox.showinfo("Reverse", "Reverse tool - Coming soon!")
    
    def open_optimize_dialog(self):
        """Open optimize dialog."""
        messagebox.showinfo("Optimize", "Optimize tool - Coming soon!")
    
    def _open_tool_dialog(self, title: str, panel_class):
        """Open a tool dialog with the specified panel."""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("800x700")
        dialog.resizable(True, True)
        dialog.minsize(600, 500)  # Set minimum size
        
        # Create panel
        panel = panel_class(dialog, on_process=self.process_tool)
        panel.get_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # If it's the rearrange panel and we have a current file, load it
        if hasattr(panel, 'load_gif') and self.current_file:
            panel.load_gif(self.current_file)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center on parent
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def open_add_text_dialog(self):
        """Open add text dialog."""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select a GIF file first.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Text to GIF")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        dialog.minsize(500, 400)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create add text panel
        add_text_panel = AddTextPanel(dialog, self.process_tool)
        add_text_panel.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Auto-load the current GIF
        if self.current_file:
            add_text_panel.auto_load_gif(self.current_file)
    
    def open_rearrange_dialog(self):
        """Open rearrange dialog."""
        self._open_tool_dialog("Rearrange GIF Frames", RearrangePanel)
    
    def open_speed_dialog(self):
        """Open speed control dialog."""
        messagebox.showinfo("Speed Control", "Speed Control tool - Coming soon!")
    
    def open_filter_dialog(self):
        """Open filter effects dialog."""
        messagebox.showinfo("Filter Effects", "Filter Effects tool - Coming soon!")
    
    def open_extract_frames_dialog(self):
        """Open extract frames dialog."""
        messagebox.showinfo("Extract Frames", "Extract Frames tool - Coming soon!")
    
    def open_loop_settings_dialog(self):
        """Open loop settings dialog."""
        messagebox.showinfo("Loop Settings", "Loop Settings tool - Coming soon!")
    
    def open_format_conversion_dialog(self):
        """Open format conversion dialog."""
        messagebox.showinfo("Format Conversion", "Format Conversion tool - Coming soon!")
    
    def open_watermark_dialog(self):
        """Open watermark dialog."""
        messagebox.showinfo("Watermark", "Watermark tool - Coming soon!")
    
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
GIF-Tools Desktop Application
Version 1.0.0

A comprehensive desktop GUI application for GIF manipulation with 17 powerful tools.

Features:
• Video to GIF conversion
• Resize, rotate, crop, split, merge
• Add text, rearrange frames, reverse
• Optimize, speed control, filter effects
• Extract frames, loop settings, format conversion
• Batch processing and watermarking

Author: Kamal Nady
License: MIT
        """
        messagebox.showinfo("About GIF-Tools", about_text)
    
    def show_documentation(self):
        """Show documentation."""
        messagebox.showinfo("Documentation", "Documentation - Coming soon!")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point for the desktop application."""
    try:
        app = GifToolsApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
