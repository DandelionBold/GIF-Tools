# GIF-Tools

A comprehensive library and desktop application for GIF processing and manipulation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## 🚀 Features

### ✅ **IMPLEMENTED TOOLS** (Ready to Use)

- **Video to GIF** - Convert video files to animated GIFs with auto-optimization
- **Resize** - Change GIF dimensions with aspect ratio control and quality settings
- **Rotate** - Rotate GIFs by 90°, 180°, or 270° degrees with progress tracking
- **Crop** - Professional visual crop tool with aspect ratio presets and drag selection
- **Rearrange** - Advanced drag-and-drop frame reordering with visual preview

### 🔄 **IN PROGRESS** (Partially Implemented)

- **Split** - Extract individual frames from GIFs
- **Merge** - Combine multiple GIFs or images into one
- **Add Text** - Overlay text with customizable fonts and colors

### 📋 **PLANNED TOOLS** (Coming Soon)

- **Reverse** - Play GIF animations backwards
- **Optimize** - Reduce file size while maintaining quality
- **Speed Control** - Adjust playback speed
- **Filter Effects** - Apply visual effects like blur, sharpen, etc.
- **Extract Frames** - Save specific frames as static images
- **Loop Settings** - Control loop count and behavior
- **Format Conversion** - Convert between GIF, WebP, APNG formats
- **Batch Processing** - Process multiple files at once
- **Watermark** - Add image or text watermarks

### 🎨 **Desktop Application Features**

- **Modern GUI** - Professional interface built with tkinter
- **Visual Crop Tool** - Click-and-drag cropping with 15+ aspect ratio presets
- **Auto-Loading** - Tools automatically load selected GIFs from main dashboard
- **Progress Tracking** - Real-time progress bars with detailed status messages
- **Error Handling** - Robust error messages and validation
- **Resizable Windows** - All tool dialogs are resizable for better workflow
- **Aspect Ratio Presets** - Free, Square, Classic, Camera, Widescreen, Portrait, Vertical, and more

### 🌐 **Future Web API**

- RESTful API for web integration
- Async processing for large files
- Docker containerization ready

## 📊 **Current Development Status**

### **Phase 1: Core Infrastructure** ✅ **COMPLETED**

- Project structure and architecture
- Core library with modular design
- Desktop GUI framework
- Basic tool integration

### **Phase 2: Basic Tools** ✅ **COMPLETED**

- Video to GIF conversion with auto-optimization
- Resize tool with aspect ratio control
- Rotate tool with progress tracking
- Professional visual crop tool with 15+ aspect ratios
- Advanced rearrange tool with drag-and-drop

### **Phase 3: Advanced Tools** 🔄 **IN PROGRESS**

- Split tool (frames extraction)
- Merge tool (combine GIFs)
- Add Text tool (text overlay)

### **Phase 4: Polish & Optimization** 📋 **PLANNED**

- Performance optimization
- Additional effects and filters
- Batch processing
- Web API development

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for video processing)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/KamalNady/GIF-Tools.git
cd GIF-Tools

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the desktop application
python -m desktop_app.main
```

### Development Installation

```bash
# Install development dependencies
pip install -r requirements/dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
flake8 gif_tools desktop_app web_api tests
```

## 🛠️ Usage

### Desktop Application

```bash
python -m desktop_app.main
```

### Python Library

```python
from gif_tools import video_to_gif, resize, rotate

# Convert video to GIF
video_to_gif.convert('input.mp4', 'output.gif', fps=10)

# Resize GIF
resize.resize_gif('input.gif', 'output.gif', width=500, height=300)

# Rotate GIF
rotate.rotate_gif('input.gif', 'output.gif', angle=90)
```

## 🏗️ Project Structure

```
GIF-Tools/
├── gif_tools/                 # Core processing library
│   ├── core/                  # Core processing modules
│   ├── utils/                 # Utility modules
│   └── tests/                 # Core library tests
├── desktop_app/               # Desktop GUI application
│   ├── gui/                   # GUI modules
│   ├── assets/                # GUI assets
│   └── tests/                 # Desktop app tests
├── web_api/                   # Future web API
├── docs/                      # Documentation
├── requirements/              # Dependency management
├── tests/                     # Integration tests
└── scripts/                   # Utility scripts
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gif_tools --cov=desktop_app --cov=web_api

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Run integration tests
pytest -m performance  # Run performance tests
```

## 📚 Documentation

- [User Guide](docs/user_guide.md) - How to use the application
- [Developer Guide](docs/developer_guide.md) - Contributing to the project
- [API Reference](docs/api_reference.md) - Core library documentation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pillow](https://python-pillow.org/) - Python Imaging Library
- [OpenCV](https://opencv.org/) - Computer Vision Library
- [MoviePy](https://zulko.github.io/moviepy/) - Video editing library
- [FFmpeg](https://ffmpeg.org/) - Multimedia framework

## 📞 Support

- 🐛 [Report a bug](https://github.com/KamalNady/GIF-Tools/issues)
- 💡 [Request a feature](https://github.com/KamalNady/GIF-Tools/issues)
- 📧 [Contact us](mailto:kamalnady@example.com)

---

**Made with ❤️ by Kamal Nady**
