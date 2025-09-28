"""
Performance benchmarks for GIF-Tools.

Tests performance of various operations under different conditions.
"""

import pytest
import time
from pathlib import Path
from PIL import Image

from gif_tools.core import (
    resize_gif, rotate_gif, crop_gif, add_text_to_gif, optimize_gif,
    reverse_gif, change_gif_speed, apply_gif_filter, extract_gif_frames,
    merge_gifs, batch_processing
)


class TestPerformanceBenchmarks:
    """Test performance benchmarks for GIF operations."""
    
    def test_resize_performance(self, sample_gif_path, test_output_dir):
        """Test resize operation performance."""
        output_path = test_output_dir / "resized_perf.gif"
        
        start_time = time.time()
        resize_gif(sample_gif_path, output_path, 50, 50)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert output_path.exists()
    
    def test_rotate_performance(self, sample_gif_path, test_output_dir):
        """Test rotate operation performance."""
        output_path = test_output_dir / "rotated_perf.gif"
        
        start_time = time.time()
        rotate_gif(sample_gif_path, output_path, 90)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 3.0  # Should complete within 3 seconds
        assert output_path.exists()
    
    def test_crop_performance(self, sample_gif_path, test_output_dir):
        """Test crop operation performance."""
        output_path = test_output_dir / "cropped_perf.gif"
        
        start_time = time.time()
        crop_gif(sample_gif_path, output_path, 10, 10, 50, 50)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 3.0  # Should complete within 3 seconds
        assert output_path.exists()
    
    def test_add_text_performance(self, sample_gif_path, test_output_dir):
        """Test add text operation performance."""
        output_path = test_output_dir / "text_perf.gif"
        
        start_time = time.time()
        add_text_to_gif(
            sample_gif_path, output_path, "Performance Test",
            position=(10, 10), font_size=16
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert output_path.exists()
    
    def test_optimize_performance(self, sample_gif_path, test_output_dir):
        """Test optimize operation performance."""
        output_path = test_output_dir / "optimized_perf.gif"
        
        start_time = time.time()
        optimize_gif(sample_gif_path, output_path, quality=75)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 10.0  # Should complete within 10 seconds
        assert output_path.exists()
    
    def test_reverse_performance(self, sample_gif_path, test_output_dir):
        """Test reverse operation performance."""
        output_path = test_output_dir / "reversed_perf.gif"
        
        start_time = time.time()
        reverse_gif(sample_gif_path, output_path)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 3.0  # Should complete within 3 seconds
        assert output_path.exists()
    
    def test_speed_control_performance(self, sample_gif_path, test_output_dir):
        """Test speed control operation performance."""
        output_path = test_output_dir / "speed_perf.gif"
        
        start_time = time.time()
        change_gif_speed(sample_gif_path, output_path, 2.0)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 3.0  # Should complete within 3 seconds
        assert output_path.exists()
    
    def test_filter_performance(self, sample_gif_path, test_output_dir):
        """Test filter operation performance."""
        output_path = test_output_dir / "filtered_perf.gif"
        
        start_time = time.time()
        apply_gif_filter(sample_gif_path, output_path, "BLUR", intensity=1.0)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert output_path.exists()
    
    def test_extract_frames_performance(self, sample_gif_path, test_output_dir):
        """Test extract frames operation performance."""
        frames_dir = test_output_dir / "frames_perf"
        frames_dir.mkdir()
        
        start_time = time.time()
        extract_gif_frames(sample_gif_path, frames_dir)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert frames_dir.exists()
    
    def test_merge_performance(self, sample_gif_path, test_output_dir):
        """Test merge operation performance."""
        output_path = test_output_dir / "merged_perf.gif"
        
        start_time = time.time()
        merge_gifs([sample_gif_path, sample_gif_path], output_path)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert output_path.exists()


class TestMemoryUsage:
    """Test memory usage during operations."""
    
    def test_memory_usage_resize(self, sample_gif_path, test_output_dir):
        """Test memory usage during resize operation."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        output_path = test_output_dir / "memory_resize.gif"
        resize_gif(sample_gif_path, output_path, 50, 50)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024
        assert output_path.exists()
    
    def test_memory_usage_optimize(self, sample_gif_path, test_output_dir):
        """Test memory usage during optimize operation."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        output_path = test_output_dir / "memory_optimize.gif"
        optimize_gif(sample_gif_path, output_path, quality=75)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024
        assert output_path.exists()


class TestBatchPerformance:
    """Test batch processing performance."""
    
    def test_batch_resize_performance(self, sample_gif_path, test_output_dir):
        """Test batch resize performance."""
        # Create multiple copies for batch processing
        input_dir = test_output_dir / "batch_input"
        input_dir.mkdir()
        
        for i in range(3):
            copy_path = input_dir / f"copy_{i}.gif"
            with Image.open(sample_gif_path) as img:
                img.save(copy_path)
        
        output_dir = test_output_dir / "batch_output"
        
        start_time = time.time()
        result = batch_processing.resize_gif_batch(input_dir, output_dir, 50, 50)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 15.0  # Should complete within 15 seconds
        assert result['processed_files'] == 3
        assert result['failed_files'] == 0


class TestLargeFilePerformance:
    """Test performance with larger files."""
    
    def test_large_gif_performance(self, test_output_dir):
        """Test performance with larger GIF files."""
        # Create a larger GIF
        large_gif_path = test_output_dir / "large.gif"
        
        frames = []
        durations = []
        
        # Create 10 frames of 300x300
        for i in range(10):
            frame = Image.new('RGB', (300, 300), color=(i * 25, 100, 200 - i * 15))
            frames.append(frame)
            durations.append(100)
        
        frames[0].save(
            large_gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            optimize=True
        )
        
        # Test resize performance
        output_path = test_output_dir / "large_resized.gif"
        
        start_time = time.time()
        resize_gif(large_gif_path, output_path, 150, 150)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 30.0  # Should complete within 30 seconds
        assert output_path.exists()
        
        # Verify output
        with Image.open(output_path) as img:
            assert img.size == (150, 150)
