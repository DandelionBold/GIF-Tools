# GIF-Tools Desktop Application

A comprehensive desktop GUI application for GIF manipulation with 17 powerful tools.

## Features

### Basic Tools
- **Video to GIF**: Convert video files to animated GIFs
- **Resize**: Change GIF dimensions while maintaining aspect ratio
- **Rotate**: Rotate GIFs by 90°, 180°, or 270° degrees
- **Crop**: Cut out specific rectangular areas from GIFs
- **Split**: Extract individual frames from GIFs
- **Merge**: Combine multiple GIFs or images into one

### Advanced Tools
- **Add Text**: Overlay text with customizable fonts and colors
- **Rearrange Frames**: Drag and drop frames to reorder them
- **Reverse**: Play GIF animations backwards
- **Optimize**: Reduce file size while maintaining quality
- **Speed Control**: Adjust playback speed
- **Filter Effects**: Apply visual effects like blur, sharpen, etc.

### Additional Tools
- **Extract Frames**: Save specific frames as static images
- **Loop Settings**: Control loop count and behavior
- **Format Conversion**: Convert between GIF, WebP, APNG formats
- **Watermark**: Add image or text watermarks
- **Batch Processing**: Process multiple files at once

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements/desktop.txt
```

2. Run the desktop application:
```bash
python run_gui.py
```

## Usage

1. **Open a GIF file** using the "Open GIF" button
2. **Select a tool** from the appropriate tab
3. **Configure the tool settings** using the interactive controls
4. **Process the file** using the "Process" button
5. **Save the result** using the "Save As" button

## Architecture

The desktop application is built with:
- **Tkinter**: Cross-platform GUI framework
- **Modular Design**: Separate panels for each tool
- **Background Processing**: Non-blocking file operations
- **Progress Tracking**: Real-time progress updates
- **Error Handling**: Comprehensive error management

## File Structure

```
desktop_app/
├── main.py                 # Main application entry point
├── gui/
│   ├── tool_panels/        # Individual tool panels
│   │   ├── resize_panel.py
│   │   ├── add_text_panel.py
│   │   └── ...
│   ├── components/         # Reusable GUI components
│   └── styles/            # GUI styling and themes
├── assets/                # Application assets (icons, images)
└── tests/                 # Desktop app tests
```

## Development

To add a new tool panel:

1. Create a new panel class in `gui/tool_panels/`
2. Implement the required methods:
   - `setup_ui()`: Create the panel UI
   - `get_settings()`: Get current settings
   - `process_*()`: Process the operation
3. Add the panel to the main application
4. Update the `__init__.py` file

## License

MIT License - see LICENSE file for details.
