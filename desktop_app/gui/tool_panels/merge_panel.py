"""
Merge Tool Panel

GUI panel for the GIF merge tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Callable, Any, List
import threading

from gif_tools.core.merge import merge_gifs


class MergePanel(ttk.Frame):
    """Panel for GIF merge operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the merge panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        super().__init__(parent)
        self.on_process = on_process
        self.file_list: List[str] = []
        self.setup_ui()
    
    def setup_ui(self):
        """Create the merge panel UI."""
        # File list
        ttk.Label(self, text="Files to Merge:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # File listbox with scrollbar
        list_frame = ttk.Frame(self)
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.file_listbox = tk.Listbox(list_frame, height=6, width=50)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File controls
        file_controls = ttk.Frame(self)
        file_controls.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(file_controls, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_controls, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_controls, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=(0, 5))
        
        # Move controls
        move_controls = ttk.Frame(self)
        move_controls.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(move_controls, text="Move Up", command=self.move_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(move_controls, text="Move Down", command=self.move_down).pack(side=tk.LEFT, padx=(0, 5))
        
        # Merge options
        ttk.Label(self, text="Merge Options:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Merge mode
        self.merge_mode_var = tk.StringVar(value="sequential")
        mode_frame = ttk.Frame(self)
        mode_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        mode_options = [
            ("Sequential", "sequential"),
            ("Horizontal", "horizontal"),
            ("Vertical", "vertical"),
        ]
        
        for i, (text, value) in enumerate(mode_options):
            btn = ttk.Radiobutton(
                mode_frame, 
                text=text, 
                variable=self.merge_mode_var, 
                value=value
            )
            btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Timing controls
        timing_frame = ttk.LabelFrame(self, text="Timing", padding="5")
        timing_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(timing_frame, text="Frame Duration (ms):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.duration_var = tk.StringVar(value="100")
        ttk.Entry(timing_frame, textvariable=self.duration_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Loop settings
        ttk.Label(self, text="Loop Count:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.loop_var = tk.StringVar(value="0")
        loop_combo = ttk.Combobox(
            self, 
            textvariable=self.loop_var,
            values=["0 (infinite)", "1", "2", "3", "5", "10"],
            state="readonly",
            width=15
        )
        loop_combo.grid(row=6, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Quality controls
        ttk.Label(self, text="Quality:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(
            self, 
            from_=1, 
            to=100, 
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        quality_scale.grid(row=7, column=1, columnspan=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Quality value label
        self.quality_label = ttk.Label(self, text="85")
        self.quality_label.grid(row=7, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Update quality label when scale changes
        quality_scale.configure(command=self.update_quality_label)
        
        # Process button
        self.process_btn = ttk.Button(
            self, 
            text="Merge GIFs", 
            command=self.process_merge
        )
        self.process_btn.grid(row=8, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self, 
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
    
    def add_files(self):
        """Add files to the merge list."""
        file_paths = filedialog.askopenfilenames(
            title="Select GIF Files to Merge",
            filetypes=[
                ("GIF files", "*.gif"),
                ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),
                ("All files", "*.*")
            ]
        )
        
        for file_path in file_paths:
            if file_path not in self.file_list:
                self.file_list.append(file_path)
                self.file_listbox.insert(tk.END, Path(file_path).name)
    
    def remove_selected(self):
        """Remove selected file from the list."""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.file_listbox.delete(index)
            self.file_list.pop(index)
    
    def clear_all(self):
        """Clear all files from the list."""
        self.file_listbox.delete(0, tk.END)
        self.file_list.clear()
    
    def move_up(self):
        """Move selected file up in the list."""
        selection = self.file_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            # Swap in list
            self.file_list[index], self.file_list[index-1] = self.file_list[index-1], self.file_list[index]
            # Update listbox
            self.file_listbox.delete(0, tk.END)
            for file_path in self.file_list:
                self.file_listbox.insert(tk.END, Path(file_path).name)
            # Reselect moved item
            self.file_listbox.selection_set(index-1)
    
    def move_down(self):
        """Move selected file down in the list."""
        selection = self.file_listbox.curselection()
        if selection and selection[0] < len(self.file_list) - 1:
            index = selection[0]
            # Swap in list
            self.file_list[index], self.file_list[index+1] = self.file_list[index+1], self.file_list[index]
            # Update listbox
            self.file_listbox.delete(0, tk.END)
            for file_path in self.file_list:
                self.file_listbox.insert(tk.END, Path(file_path).name)
            # Reselect moved item
            self.file_listbox.selection_set(index+1)
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def get_settings(self) -> dict:
        """Get current merge settings."""
        try:
            duration = int(self.duration_var.get())
            quality = self.quality_var.get()
            
            # Parse loop count
            loop_text = self.loop_var.get()
            if loop_text.startswith("0"):
                loop_count = 0
            else:
                loop_count = int(loop_text)
                
        except ValueError as e:
            raise ValueError(f"Invalid numeric value: {e}")
        
        return {
            'mode': self.merge_mode_var.get(),
            'duration': duration,
            'loop_count': loop_count,
            'quality': quality,
            'file_list': self.file_list.copy()
        }
    
    def process_merge(self):
        """Process the merge operation."""
        try:
            if not self.file_list:
                messagebox.showwarning("Warning", "Please add files to merge!")
                return
            
            settings = self.get_settings()
            
            if self.on_process:
                # For merge, we don't need a single input file, so pass None
                self.on_process('merge', settings, None)
            else:
                messagebox.showinfo("Merge", f"Merge settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Merge failed: {e}")
    
    def start_progress(self):
        """Start the progress bar."""
        self.progress_bar.start()
        self.process_btn.config(state=tk.DISABLED)
    
    def stop_progress(self):
        """Stop the progress bar."""
        self.progress_bar.stop()
        self.process_btn.config(state=tk.NORMAL)
    
