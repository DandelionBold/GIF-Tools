"""
Combine Frames Tool Panel

GUI panel for combining extracted frames back into a GIF using CSV file.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.extract_frames import extract_gif_frames


class CombineFramesPanel:
    """Panel for combining extracted frames back into a GIF."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None, default_output_dir: str = "frames_output"):
        """
        Initialize the combine frames panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
            default_output_dir: Default output directory path
        """
        self.parent = parent
        self.on_process = on_process
        self.default_output_dir = default_output_dir
        self.setup_ui()
    
    def setup_ui(self):
        """Create the combine frames panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Combine Frames", padding="10")
        
        # Description
        desc_text = "Combine extracted frames back into a GIF using the CSV file created during frame extraction."
        ttk.Label(self.frame, text=desc_text, wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # CSV file selection
        ttk.Label(self.frame, text="CSV File:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        self.csv_file_var = tk.StringVar()
        csv_frame = ttk.Frame(self.frame)
        csv_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Entry(
            csv_frame,
            textvariable=self.csv_file_var,
            width=40,
            state="readonly"
        ).grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Button(
            csv_frame,
            text="Browse",
            command=self.browse_csv_file,
            width=10
        ).grid(row=0, column=1)
        
        # Output settings
        self.output_frame = ttk.LabelFrame(self.frame, text="Output Settings", padding="10")
        self.output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Output GIF path
        ttk.Label(self.output_frame, text="Output GIF:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.output_gif_var = tk.StringVar()
        output_frame = ttk.Frame(self.output_frame)
        output_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(
            output_frame,
            textvariable=self.output_gif_var,
            width=40,
            state="readonly"
        ).grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Button(
            output_frame,
            text="Browse",
            command=self.browse_output_gif,
            width=10
        ).grid(row=0, column=1)
        
        # Quality setting
        ttk.Label(self.output_frame, text="Quality:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.quality_var = tk.DoubleVar(value=85)
        quality_frame = ttk.Frame(self.output_frame)
        quality_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.quality_scale = ttk.Scale(
            quality_frame,
            from_=1,
            to=100,
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            command=self.update_quality_label
        )
        self.quality_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.quality_label = ttk.Label(quality_frame, text="85")
        self.quality_label.grid(row=0, column=1)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame,
            text="🔄 Combine Frames",
            command=self.process_combine_frames
        )
        self.process_btn.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.progress_bar = ttk.Progressbar(
            self.frame,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="No CSV file selected", foreground="gray")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
        csv_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        quality_frame.grid_columnconfigure(0, weight=1)
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def browse_csv_file(self):
        """Browse for CSV file."""
        csv_file = filedialog.askopenfilename(
            title="Select Frame List CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=self.default_output_dir
        )
        if csv_file:
            self.csv_file_var.set(csv_file)
            self.status_label.config(text=f"CSV loaded: {Path(csv_file).name}", foreground="green")
    
    def browse_output_gif(self):
        """Browse for output GIF file."""
        output_gif = filedialog.asksaveasfilename(
            title="Save Combined GIF As",
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")],
            initialdir=self.default_output_dir
        )
        if output_gif:
            self.output_gif_var.set(output_gif)
    
    def process_combine_frames(self):
        """Process frame combination from CSV."""
        try:
            csv_file = self.csv_file_var.get()
            output_gif = self.output_gif_var.get()
            
            if not csv_file:
                messagebox.showerror("Error", "Please select a CSV file!")
                return
            
            if not output_gif:
                messagebox.showerror("Error", "Please select an output GIF file!")
                return
            
            if not Path(csv_file).exists():
                messagebox.showerror("Error", f"CSV file not found: {csv_file}")
                return
            
            # Create settings for combine operation
            settings = {
                'csv_file': csv_file,
                'output_path': output_gif,
                'quality': int(self.quality_var.get()),
                'operation': 'combine_frames'
            }
            
            if self.on_process:
                self.on_process('combine_frames', settings)
            else:
                messagebox.showinfo("Combine Frames", f"Combine frames settings: {settings}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Combine frames failed: {e}")
    
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
    
    def set_output_directory(self, output_dir: str):
        """Set the output directory."""
        self.default_output_dir = output_dir
