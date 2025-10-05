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

```powershell
# Clone the repository
git clone https://github.com/DandelionBold/GIF-Tools.git
cd GIF-Tools

# Create a virtual environment
python -m venv venv

# Activate (Windows PowerShell)
./venv/Scripts/Activate.ps1

# Install desktop dependencies
pip install -r requirements/desktop.txt

# Run the desktop application
python run_gui.py
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

## 🛠️ Usage (GUI)

1) Launch the app

```powershell
python run_gui.py
```

2) Pick an input and output folder
- Use the dashboard to select the current GIF/video
- Set the Output Directory (all tools will save there)

3) Open a tool (from tabs or menu)

- Video → GIF: convert videos with auto‑optimization
- Resize: change dimensions (maintain aspect)
- Rotate: rotate 90°/180°/270°
- Crop: drag to select; choose aspect ratio
- Split: move the timeline head; split at point or extract a range
- Merge: add multiple files; choose horizontal/vertical/sequential
- Rearrange: select frames; drag to reorder; export
- Reverse: one‑click reverse (or ping‑pong)
- Speed Control: slower/faster playback; timing kept per frame
- Filter Effects: apply effects like blur/sharpen/brightness/contrast
- Extract Frames: export frames (PNG/JPG) + CSV metadata
- Combine Frames: rebuild a GIF from a CSV (original timing)
- Free Play: layer multiple GIFs; click‑to‑place with anchor options

Tip: All exports use transparency‑safe settings to avoid glitches.

### Extract → CSV → Combine flow

1) Open Extract Frames, choose method (All / Specific / Range / Interval)
2) Enable “Export frame list to CSV” and Process
3) Open Combine Frames, select the CSV, choose output path, Process

CSV example (header + first frame rows):

```csv
# GIF Metadata
total_frames,429
is_animated,True
width,320
height,240
mode,P
format,GIF
loop_count,0
background,0
transparency,0
duration_total_ms,15380
fps,27.89

# Frame Data
frame_number,filename,original_frame_index,file_path,duration_ms,disposal_method
1,frame_0000.png,0,C:/path/frames/frame_0000.png,40,2
2,frame_0001.png,1,C:/path/frames/frame_0001.png,60,2
3,frame_0002.png,2,C:/path/frames/frame_0002.png,20,2
```

The Combine step restores original timing (per‑frame duration) and key GIF properties (loop, background, transparency).

## 🧼 Output quality & transparency

- All tools write with transparency‑safe settings to avoid trails/ghosting:
  - `disposal=2` (clear to background between frames)
  - `optimize=False` (prevents palette merges that break alpha)
  - `transparency` index preserved when applicable
- Sequential merge centers each source on a common canvas to prevent jumpy alignment.
- Free Play and layered exports composite in RGBA before saving to GIF palette.
- Speed and Reverse preserve per‑frame durations; single‑frame GIFs are handled cleanly.

## 🚀 Performance tips (large media)

- Prefer shorter clips and lower resolutions for long videos (e.g., 720p → 480p)
- Reduce FPS for GIF export (e.g., 30 → 10–15) to cut size dramatically
- Use the Video → GIF tool’s auto‑optimization when files exceed 100MB
- Avoid extreme color effects on very long animations (palette bloat)
- Close other heavy apps while processing to keep UI responsive

## 🏗️ Project Structure

```
GIF-Tools/
├── gif_tools/                 # Core processing library
│   ├── core/                  # Algorithms: video_to_gif, split, merge, reverse, etc.
│   └── utils/                 # Utilities: constants, image utils, validation
├── desktop_app/               # Desktop GUI (Tkinter)
│   ├── gui/
│   │   └── tool_panels/       # Each tool panel (Resize, Split, Merge, Free Play, ...)
│   ├── assets/                # Images/icons/fonts for the UI
│   └── main.py                # App entry and dialogs
├── docs/                      # Sphinx docs
├── requirements/              # requirements/*.txt (desktop, base, dev, web)
├── run_gui.py                 # Simple launcher (python run_gui.py)
├── web_api/                   # Future: REST API scaffolding
├── pyproject.toml             # Packaging and tooling config
└── README.md                  # This file
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
