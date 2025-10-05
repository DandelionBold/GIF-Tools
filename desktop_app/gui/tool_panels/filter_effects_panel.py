"""
Filter Effects Tool Panel

GUI panel for the GIF filter effects tool with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Callable, Any
import threading

from gif_tools.core.filter_effects import apply_gif_filter, apply_gif_filters
from gif_tools.utils.constants import FILTER_EFFECTS


class FilterEffectsPanel:
    """Panel for GIF filter effects operations."""
    
    def __init__(self, parent: tk.Widget, on_process: Optional[Callable] = None):
        """
        Initialize the filter effects panel.
        
        Args:
            parent: Parent widget
            on_process: Callback function for processing
        """
        self.parent = parent
        self.on_process = on_process
        self.current_gif_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """Create the filter effects panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Filter Effects", padding="10")
        
        # Description
        desc_text = "Apply visual effects and filters to your GIF. Choose from various effects like blur, sharpen, brightness, and more."
        ttk.Label(self.frame, text=desc_text, wraplength=400, justify=tk.LEFT).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Filter selection
        ttk.Label(self.frame, text="Select Filter:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        self.filter_var = tk.StringVar(value="blur")
        filter_frame = ttk.Frame(self.frame)
        filter_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Filter categories
        self.filter_category_var = tk.StringVar(value="basic")
        category_frame = ttk.LabelFrame(filter_frame, text="Filter Categories", padding="5")
        category_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        categories = [
            ("Basic", "basic"),
            ("Enhancement", "enhancement"),
            ("Artistic", "artistic"),
            ("Color", "color"),
        ]
        
        for i, (text, value) in enumerate(categories):
            ttk.Radiobutton(
                category_frame,
                text=text,
                variable=self.filter_category_var,
                value=value,
                command=self.update_filter_list
            ).grid(row=0, column=i, padx=(0, 15), sticky=tk.W)
        
        # Filter list
        self.filter_listbox = tk.Listbox(
            filter_frame,
            height=6,
            selectmode=tk.SINGLE
        )
        self.filter_listbox.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Filter intensity
        ttk.Label(self.frame, text="Filter Intensity:").grid(row=2, column=0, sticky=tk.W, pady=10)
        
        self.intensity_var = tk.DoubleVar(value=1.0)
        intensity_scale = ttk.Scale(
            self.frame,
            from_=0.1,
            to=2.0,
            variable=self.intensity_var,
            orient=tk.HORIZONTAL,
            length=300,
            command=self.update_intensity_label
        )
        intensity_scale.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=10)
        
        self.intensity_label = ttk.Label(self.frame, text="1.0 (Normal)")
        self.intensity_label.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Multiple filters section
        self.multiple_frame = ttk.LabelFrame(self.frame, text="Multiple Filters", padding="10")
        self.multiple_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.multiple_frame, text="Applied Filters:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Filter list for multiple filters
        self.applied_filters_listbox = tk.Listbox(
            self.multiple_frame,
            height=4,
            selectmode=tk.SINGLE
        )
        self.applied_filters_listbox.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Add/Remove filter buttons
        filter_buttons_frame = ttk.Frame(self.multiple_frame)
        filter_buttons_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(
            filter_buttons_frame,
            text="Add Filter",
            command=self.add_filter_to_list
        ).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(
            filter_buttons_frame,
            text="Remove Selected",
            command=self.remove_selected_filter
        ).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(
            filter_buttons_frame,
            text="Clear All",
            command=self.clear_all_filters
        ).grid(row=0, column=2, padx=(0, 5))
        
        # Processing mode
        ttk.Label(self.frame, text="Processing Mode:").grid(row=5, column=0, sticky=tk.W, pady=10)
        
        self.mode_var = tk.StringVar(value="single")
        mode_frame = ttk.Frame(self.frame)
        mode_frame.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        mode_options = [
            ("Single Filter", "single"),
            ("Multiple Filters", "multiple"),
        ]
        
        for i, (text, value) in enumerate(mode_options):
            ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode_var,
                value=value,
                command=self.update_mode_controls
            ).grid(row=0, column=i, padx=(0, 20), sticky=tk.W)
        
        # Quality control
        ttk.Label(self.frame, text="Quality:").grid(row=6, column=0, sticky=tk.W, pady=10)
        
        self.quality_var = tk.DoubleVar(value=85)
        quality_scale = ttk.Scale(
            self.frame,
            from_=1,
            to=100,
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_quality_label
        )
        quality_scale.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=10)
        
        self.quality_label = ttk.Label(self.frame, text="85")
        self.quality_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Process button
        self.process_btn = ttk.Button(
            self.frame,
            text="🎨 Apply Filters",
            command=self.process_filter_effects
        )
        self.progress_bar = ttk.Progressbar(
            self.frame,
            mode='indeterminate'
        )
        self.process_btn.grid(row=8, column=0, columnspan=3, pady=10)
        self.progress_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="No GIF loaded", foreground="gray")
        self.status_label.grid(row=10, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
        filter_frame.grid_columnconfigure(1, weight=1)
        self.multiple_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize controls
        self.update_filter_list()
        self.update_mode_controls()
        
        # Bind listbox selection
        self.filter_listbox.bind('<<ListboxSelect>>', self.on_filter_select)
    
    def update_filter_list(self):
        """Update the filter list based on selected category."""
        category = self.filter_category_var.get()
        self.filter_listbox.delete(0, tk.END)
        
        # Define filter categories
        filter_categories = {
            "basic": {
                "Blur": "blur",
                "Sharpen": "sharpen",
                "Smooth": "smooth",
                "Smooth More": "smooth_more",
            },
            "enhancement": {
                "Edge Enhance": "edge_enhance",
                "Edge Enhance More": "edge_enhance_more",
                "Detail": "detail",
            },
            "artistic": {
                "Emboss": "emboss",
                "Find Edges": "find_edges",
                "Contour": "contour",
            },
            "color": {
                "Brightness": "brightness",
                "Contrast": "contrast",
                "Saturation": "saturation",
                "Color": "color",
            }
        }
        
        if category in filter_categories:
            for display_name, filter_name in filter_categories[category].items():
                self.filter_listbox.insert(tk.END, display_name)
        
        # Select first item
        if self.filter_listbox.size() > 0:
            self.filter_listbox.selection_set(0)
            self.on_filter_select(None)
    
    def on_filter_select(self, event):
        """Handle filter selection."""
        selection = self.filter_listbox.curselection()
        if selection:
            # Update filter_var based on selection
            category = self.filter_category_var.get()
            filter_categories = {
                "basic": {
                    "Blur": "blur",
                    "Sharpen": "sharpen",
                    "Smooth": "smooth",
                    "Smooth More": "smooth_more",
                },
                "enhancement": {
                    "Edge Enhance": "edge_enhance",
                    "Edge Enhance More": "edge_enhance_more",
                    "Detail": "detail",
                },
                "artistic": {
                    "Emboss": "emboss",
                    "Find Edges": "find_edges",
                    "Contour": "contour",
                },
                "color": {
                    "Brightness": "brightness",
                    "Contrast": "contrast",
                    "Saturation": "saturation",
                    "Color": "color",
                }
            }
            
            if category in filter_categories:
                filter_names = list(filter_categories[category].keys())
                selected_filter = filter_names[selection[0]]
                self.filter_var.set(filter_categories[category][selected_filter])
    
    def update_intensity_label(self, value):
        """Update the intensity label when scale changes."""
        intensity = float(value)
        if intensity < 0.5:
            label = f"{intensity:.1f} (Weak)"
        elif intensity == 1.0:
            label = f"{intensity:.1f} (Normal)"
        elif intensity <= 1.5:
            label = f"{intensity:.1f} (Strong)"
        else:
            label = f"{intensity:.1f} (Very Strong)"
        
        self.intensity_label.config(text=label)
    
    def update_quality_label(self, value):
        """Update the quality label when scale changes."""
        self.quality_label.config(text=str(int(float(value))))
    
    def update_mode_controls(self):
        """Update control visibility based on processing mode."""
        mode = self.mode_var.get()
        
        if mode == "single":
            self.multiple_frame.grid_remove()
        elif mode == "multiple":
            self.multiple_frame.grid()
    
    def add_filter_to_list(self):
        """Add selected filter to the applied filters list."""
        filter_name = self.filter_var.get()
        intensity = self.intensity_var.get()
        
        # Get display name
        category = self.filter_category_var.get()
        filter_categories = {
            "basic": {
                "blur": "Blur",
                "sharpen": "Sharpen",
                "smooth": "Smooth",
                "smooth_more": "Smooth More",
            },
            "enhancement": {
                "edge_enhance": "Edge Enhance",
                "edge_enhance_more": "Edge Enhance More",
                "detail": "Detail",
            },
            "artistic": {
                "emboss": "Emboss",
                "find_edges": "Find Edges",
                "contour": "Contour",
            },
            "color": {
                "brightness": "Brightness",
                "contrast": "Contrast",
                "saturation": "Saturation",
                "color": "Color",
            }
        }
        
        display_name = filter_categories.get(category, {}).get(filter_name, filter_name)
        filter_text = f"{display_name} ({intensity:.1f}x)"
        
        # Add to listbox if not already present
        for i in range(self.applied_filters_listbox.size()):
            if self.applied_filters_listbox.get(i) == filter_text:
                messagebox.showinfo("Info", "Filter already added!")
                return
        
        self.applied_filters_listbox.insert(tk.END, filter_text)
    
    def remove_selected_filter(self):
        """Remove selected filter from the applied filters list."""
        selection = self.applied_filters_listbox.curselection()
        if selection:
            self.applied_filters_listbox.delete(selection[0])
    
    def clear_all_filters(self):
        """Clear all applied filters."""
        self.applied_filters_listbox.delete(0, tk.END)
    
    def get_settings(self) -> dict:
        """Get current filter effects settings."""
        if not self.current_gif_path:
            raise ValueError("No GIF file loaded")
        
        settings = {
            'input_path': self.current_gif_path,
            'quality': int(self.quality_var.get()),
            'mode': self.mode_var.get(),
        }
        
        if self.mode_var.get() == "single":
            settings.update({
                'filter_name': self.filter_var.get(),
                'intensity': self.intensity_var.get(),
            })
        else:
            # Multiple filters mode
            filters = []
            for i in range(self.applied_filters_listbox.size()):
                filter_text = self.applied_filters_listbox.get(i)
                # Parse filter text to extract name and intensity
                # Format: "Filter Name (intensity)"
                if '(' in filter_text and ')' in filter_text:
                    name_part = filter_text.split('(')[0].strip()
                    intensity_part = filter_text.split('(')[1].split(')')[0].strip()
                    
                    # Convert display name back to filter name
                    category = self.filter_category_var.get()
                    filter_categories = {
                        "basic": {
                            "Blur": "blur",
                            "Sharpen": "sharpen",
                            "Smooth": "smooth",
                            "Smooth More": "smooth_more",
                        },
                        "enhancement": {
                            "Edge Enhance": "edge_enhance",
                            "Edge Enhance More": "edge_enhance_more",
                            "Detail": "detail",
                        },
                        "artistic": {
                            "Emboss": "emboss",
                            "Find Edges": "find_edges",
                            "Contour": "contour",
                        },
                        "color": {
                            "Brightness": "brightness",
                            "Contrast": "contrast",
                            "Saturation": "saturation",
                            "Color": "color",
                        }
                    }
                    
                    # Find the filter name
                    filter_name = None
                    for cat, filters in filter_categories.items():
                        if name_part in filters:
                            filter_name = filters[name_part]
                            break
                    
                    if filter_name:
                        filters.append({
                            'name': filter_name,
                            'intensity': float(intensity_part)
                        })
            
            settings['filters'] = filters
        
        return settings
    
    def process_filter_effects(self):
        """Process the filter effects operation."""
        try:
            settings = self.get_settings()
            
            if self.mode_var.get() == "multiple" and not settings.get('filters'):
                messagebox.showwarning("Warning", "Please add at least one filter!")
                return
            
            if self.on_process:
                self.on_process('filter_effects', settings)
            else:
                messagebox.showinfo("Filter Effects", f"Filter settings: {settings}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Filter effects failed: {e}")
    
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
        """Auto-load GIF for filter effects."""
        # Store the path and update status
        self.current_gif_path = gif_path
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"GIF loaded: {Path(gif_path).name}")
