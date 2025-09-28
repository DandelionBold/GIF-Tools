"""
Pytest configuration and fixtures for GIF-Tools tests.

This module provides shared fixtures and configuration for all tests.
"""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from PIL import Image

from gif_tools.utils import get_image_processor


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_gif_path(temp_dir: Path) -> Path:
    """Create a sample animated GIF for testing."""
    # Create a simple animated GIF with 3 frames
    frames = []
    durations = []
    
    for i in range(3):
        # Create a simple colored frame
        frame = Image.new('RGB', (100, 100), color=(i * 80, 100, 200 - i * 50))
        frames.append(frame)
        durations.append(100)  # 100ms per frame
    
    # Save as GIF
    gif_path = temp_dir / "sample.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    
    return gif_path


@pytest.fixture
def sample_static_gif_path(temp_dir: Path) -> Path:
    """Create a sample static GIF for testing."""
    # Create a simple static image
    frame = Image.new('RGB', (100, 100), color=(255, 0, 0))
    
    # Save as GIF
    gif_path = temp_dir / "sample_static.gif"
    frame.save(gif_path, format='GIF')
    
    return gif_path


@pytest.fixture
def sample_image_path(temp_dir: Path) -> Path:
    """Create a sample image for testing."""
    # Create a simple image
    image = Image.new('RGB', (100, 100), color=(0, 255, 0))
    
    # Save as PNG
    image_path = temp_dir / "sample.png"
    image.save(image_path, format='PNG')
    
    return image_path


@pytest.fixture
def sample_video_path(temp_dir: Path) -> Path:
    """Create a sample video for testing (mock)."""
    # For now, create a mock video file
    # In real tests, you would use an actual video file
    video_path = temp_dir / "sample.mp4"
    video_path.write_bytes(b"mock video content")
    
    return video_path


@pytest.fixture
def image_processor():
    """Get image processor instance."""
    return get_image_processor()


@pytest.fixture
def test_output_dir(temp_dir: Path) -> Path:
    """Create output directory for test results."""
    output_dir = temp_dir / "output"
    output_dir.mkdir()
    return output_dir


# Test data constants
TEST_GIF_SIZE = (100, 100)
TEST_FRAME_COUNT = 3
TEST_DURATION = 100  # ms
TEST_COLORS = [(0, 100, 200), (80, 100, 150), (160, 100, 100)]

# Test parameters
TEST_QUALITY_LEVELS = [50, 75, 85, 95]
TEST_SIZES = [(50, 50), (100, 100), (200, 200)]
TEST_ROTATION_ANGLES = [90, 180, 270]
TEST_CROP_REGIONS = [(10, 10, 50, 50), (25, 25, 75, 75)]

# Error test cases
INVALID_PATHS = [
    "nonexistent_file.gif",
    "/invalid/path/file.gif",
    "",
    None
]

INVALID_SIZES = [
    (0, 0),
    (-1, -1),
    (0, 100),
    (100, 0)
]

INVALID_QUALITIES = [0, -1, 101, 150]
