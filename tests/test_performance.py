"""
Performance tests for GIF-Tools.

This module contains performance benchmarks and tests to ensure
the GIF processing tools meet performance requirements.
"""

import pytest
import tempfile
from pathlib import Path
from PIL import Image

from gif_tools.core import (
    resize_gif, rotate_gif, crop_gif, add_text_to_gif,
    optimize_gif, reverse_gif, change_gif_speed
)


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    @pytest.fixture
    def sample_gif_path(self, tmp_path):
        """Create a sample GIF for testing."""
        gif_path = tmp_path / "sample.gif"
        
        # Create a simple animated GIF
        frames = []
        for i in range(3):
            img = Image.new('RGB', (100, 100), color=(i * 80, 100, 150))
            frames.append(img)
        
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )
        
        return gif_path
    
    def test_resize_performance(self, sample_gif_path, benchmark):
        """Test GIF resize performance."""
        output_path = sample_gif_path.parent / "resized.gif"
        
        def resize():
            return resize_gif(sample_gif_path, output_path, 50, 50)
        
        result = benchmark(resize)
        assert result.exists()
    
    def test_rotate_performance(self, sample_gif_path, benchmark):
        """Test GIF rotation performance."""
        output_path = sample_gif_path.parent / "rotated.gif"
        
        def rotate():
            return rotate_gif(sample_gif_path, output_path, 90)
        
        result = benchmark(rotate)
        assert result.exists()
    
    def test_crop_performance(self, sample_gif_path, benchmark):
        """Test GIF crop performance."""
        output_path = sample_gif_path.parent / "cropped.gif"
        
        def crop():
            return crop_gif(sample_gif_path, output_path, 10, 10, 50, 50)
        
        result = benchmark(crop)
        assert result.exists()
    
    def test_add_text_performance(self, sample_gif_path, benchmark):
        """Test GIF text addition performance."""
        output_path = sample_gif_path.parent / "text.gif"
        
        def add_text():
            return add_text_to_gif(sample_gif_path, output_path, "Test")
        
        result = benchmark(add_text)
        assert result.exists()
    
    def test_optimize_performance(self, sample_gif_path, benchmark):
        """Test GIF optimization performance."""
        output_path = sample_gif_path.parent / "optimized.gif"
        
        def optimize():
            return optimize_gif(sample_gif_path, output_path)
        
        result = benchmark(optimize)
        assert result.exists()
    
    def test_reverse_performance(self, sample_gif_path, benchmark):
        """Test GIF reverse performance."""
        output_path = sample_gif_path.parent / "reversed.gif"
        
        def reverse():
            return reverse_gif(sample_gif_path, output_path)
        
        result = benchmark(reverse)
        assert result.exists()
    
    def test_speed_control_performance(self, sample_gif_path, benchmark):
        """Test GIF speed control performance."""
        output_path = sample_gif_path.parent / "speed.gif"
        
        def change_speed():
            return change_gif_speed(sample_gif_path, output_path, 2.0)
        
        result = benchmark(change_speed)
        assert result.exists()


class TestMemoryUsage:
    """Memory usage tests."""
    
    @pytest.fixture
    def large_gif_path(self, tmp_path):
        """Create a larger GIF for memory testing."""
        gif_path = tmp_path / "large.gif"
        
        # Create a larger animated GIF
        frames = []
        for i in range(5):
            img = Image.new('RGB', (200, 200), color=(i * 50, 100, 200))
            frames.append(img)
        
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )
        
        return gif_path
    
    def test_memory_usage_resize(self, large_gif_path):
        """Test memory usage during resize operations."""
        output_path = large_gif_path.parent / "resized.gif"
        
        # This is a basic test - in a real scenario, you'd use memory profiling
        result = resize_gif(large_gif_path, output_path, 100, 100)
        assert result.exists()
    
    def test_memory_usage_optimize(self, large_gif_path):
        """Test memory usage during optimization."""
        output_path = large_gif_path.parent / "optimized.gif"
        
        result = optimize_gif(large_gif_path, output_path)
        assert result.exists()


class TestLargeFilePerformance:
    """Large file performance tests."""
    
    @pytest.fixture
    def large_gif_path(self, tmp_path):
        """Create a large GIF for performance testing."""
        gif_path = tmp_path / "large.gif"
        
        # Create a larger animated GIF with more frames
        frames = []
        for i in range(10):
            img = Image.new('RGB', (300, 300), color=(i * 25, 150, 250))
            frames.append(img)
        
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )
        
        return gif_path
    
    def test_large_gif_performance(self, large_gif_path, benchmark):
        """Test performance with larger GIF files."""
        output_path = large_gif_path.parent / "processed.gif"
        
        def process():
            return resize_gif(large_gif_path, output_path, 150, 150)
        
        result = benchmark(process)
        assert result.exists()


if __name__ == "__main__":
    pytest.main([__file__])
