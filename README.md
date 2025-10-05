# GIF-Tools

Professional desktop application and core library for high‑quality GIF processing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🚀 What’s Inside

### ✅ 14 Production‑Ready Tools
- Video to GIF (auto‑optimize for large files)
- Resize
- Rotate
- Crop (visual, aspect‑ratio presets)
- Split (timeline + single split bar / regions)
- Merge (horizontal, vertical, sequential with centering + transparency fixes)
- Rearrange (drag‑and‑drop frames)
- Reverse
- Optimize
- Speed Control
- Filter Effects
- Extract Frames (with detailed CSV metadata)
- Combine Frames (rebuild from CSV with original timing)
- Free Play (multi‑GIF layering with positioning and canvas control)

### 🧰 Desktop App Highlights
- Modern Tkinter UI, resizable dialogs
- Live previews with progress indicators
- Auto‑load selected GIF across tools
- Strong error messages and validation
- Transparency‑safe saving (disposal=2, transparency=0, optimize=False)

## 📦 Installation

### Prerequisites
- Python 3.8+
- FFmpeg in PATH (for video → GIF)

### Quick Start
```bash
# Clone
git clone https://github.com/DandelionBold/GIF-Tools.git
cd GIF-Tools

# Virtual environment
python -m venv venv
"venv\Scripts\activate"   # Windows
# source venv/bin/activate  # macOS/Linux

# Install
pip install -r requirements.txt

# Run GUI
python run_gui.py
# or
python -m desktop_app.main
```

## 🛠️ Usage Tips
- Use the dashboard to select an input GIF once; tools will auto‑load it.
- For large videos, Video→GIF auto‑reduces resolution/FPS to stay under size limits.
- Extract Frames exports a CSV with exact per‑frame durations and GIF metadata; Combine Frames restores timing precisely.

## 🏗️ Project Structure
```
GIF-Tools/
├── gif_tools/                 # Core processing library
│   ├── core/                  # Tool implementations
│   └── utils/                 # Utilities and constants
├── desktop_app/               # Desktop GUI
│   └── gui/tool_panels/       # All tool panels (14)
├── web_api/                   # Placeholder (future)
├── docs/                      # Sphinx docs
├── requirements/              # Environment lockfiles
└── run_gui.py                 # Launcher
```

## 📚 Documentation
- Docs live in `docs/`. Build with Sphinx if needed.
- High‑level roadmap: see `DEVELOPMENT_PLAN.md`.

## 🤝 Contributing
- Conventional commits are welcomed (feat:, fix:, docs:, chore:, perf:, refactor:, ci:, build:).
- Open issues and PRs on `https://github.com/DandelionBold/GIF-Tools`.

## 📄 License
MIT © Kamal Nady

## 📞 Support
- Issues/Features: `https://github.com/DandelionBold/GIF-Tools/issues`
- Contact: `kamalnadykamal@gmail.com`

—
Made with ❤️ by Kamal Nady
