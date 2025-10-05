# GIF-Tools

Professional, open‑source desktop suite for fast, high‑quality GIF creation and editing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

### Visual Highlights

<!-- Replace the placeholder paths below with real screenshots/GIFs in `desktop_app/assets/images/` -->

Dashboard (Home)

![Dashboard](desktop_app/assets/images/preview_dashboard.png)

Key Tools in Action

- Rearrange Frames: drag-and-drop grid with live preview

  ![Rearrange](desktop_app/assets/images/preview_rearrange.gif)

- Merge (Sequential): perfectly centered sequences with transparency-safe export

  ![Merge Sequential](desktop_app/assets/images/preview_merge_sequential.gif)

- Extract → CSV → Combine: preserve original timing and metadata

  ![Extract Combine](desktop_app/assets/images/preview_extract_combine.gif)

- Free Play (Layer GIFs): click-to-place with anchor positions and canvas control

  ![Free Play](desktop_app/assets/images/preview_free_play.gif)

## 🚀 Features

### Core Tools (ready to use)

- **Video → GIF**: Convert videos with smart auto‑optimization (resolution/FPS/quality)
- **Resize**: Resize with aspect ratio control and quality settings
- **Rotate**: 90°/180°/270° rotations with progress feedback
- **Crop**: Visual crop with drag handles and aspect‑ratio presets
- **Split**: Media‑player timeline to split or extract ranges
- **Merge**: Horizontal, vertical, and sequential modes (centered, transparency‑safe)
- **Rearrange**: Drag‑and‑drop frame reordering with live preview
- **Reverse**: One‑click reverse and ping‑pong styles

### Advanced Toolkit

- **Speed Control**: Change playback speed with safe per‑frame timing
- **Filter Effects**: Apply visual filters (blur, sharpen, brightness, contrast, etc.)
- **Extract Frames**: Export frames to images and CSV with full GIF metadata
- **Combine Frames**: Rebuild GIFs from CSV (original timing and properties)
- **Free Play (Layer GIFs)**: Click‑to‑place layers with 9 anchor positions and canvas control

### Why outputs don’t glitch

All writers use transparency‑safe parameters (e.g., `disposal=2`, `optimize=False`, correct `transparency`) for clean playback across viewers.

### 📋 Roadmap (next)

- Web API (FastAPI) for server use
- Batch pipelines and presets
- Optional format converters (WebP/APNG) and loop settings
- Optional watermarking and additional effects

### 🎨 **Desktop Application Features**

- **Modern GUI** - Professional interface built with tkinter
- **Split Tool with Media Player** - Timeline scrubber, frame navigation, visual selection
- **Three Split Modes** - Split into Two GIFs, Extract Selected Region, Remove Selected Region
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

### **Phase 3: Advanced Tools** ✅ **COMPLETED**

- Split tool (media player interface with timeline) ✅ **COMPLETED**
- Merge tool (horizontal, vertical, sequential modes) ✅ **COMPLETED**
- Reverse tool (one-click GIF reversal) ✅ **COMPLETED**
- Free Play tool (multi-GIF layering with positioning) ✅ **COMPLETED**

### **Phase 4: Polish & Optimization** 📋 **PLANNED**

- Performance optimization
- Additional effects and filters
- Batch processing
- Web API development

## 🎉 **MAJOR MILESTONE ACHIEVED!**

**All 9 core tools are now fully implemented and working perfectly!** The GIF-Tools application is production-ready with:

- ✅ **9/9 Tools Functional** - Every core tool working flawlessly
- ✅ **Professional Interface** - Clean, intuitive desktop GUI
- ✅ **Advanced Features** - Multi-GIF layering, transparency support, real-time preview
- ✅ **Error Handling** - Comprehensive error management
- ✅ **Performance** - Optimized for production use

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for video processing)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/DandelionBold/GIF-Tools.git
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

- 🐛 [Report a bug](https://github.com/DandelionBold/GIF-Tools/issues)
- 💡 [Request a feature](https://github.com/DandelionBold/GIF-Tools/issues)
- 📧 [Contact us](mailto:kamalnadykamal@gmail.com)

---

**Made with ❤️ by Kamal Nady**
