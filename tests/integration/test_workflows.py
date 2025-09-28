"""
Integration tests for complete GIF processing workflows.

Tests end-to-end workflows combining multiple tools.
"""

import pytest
from pathlib import Path
from PIL import Image

from gif_tools.core import (
    resize_gif, rotate_gif, crop_gif, add_text_to_gif, optimize_gif,
    reverse_gif, change_gif_speed, apply_gif_filter, extract_gif_frames,
    merge_gifs, add_text_watermark_to_gif, convert_gif_format
)


class TestCompleteWorkflows:
    """Test complete GIF processing workflows."""
    
    def test_resize_rotate_crop_workflow(self, sample_gif_path, test_output_dir):
        """Test resize -> rotate -> crop workflow."""
        # Step 1: Resize
        resized_path = test_output_dir / "resized.gif"
        resize_gif(sample_gif_path, resized_path, 80, 80)
        
        # Step 2: Rotate
        rotated_path = test_output_dir / "rotated.gif"
        rotate_gif(resized_path, rotated_path, 90)
        
        # Step 3: Crop
        cropped_path = test_output_dir / "cropped.gif"
        crop_gif(rotated_path, cropped_path, 10, 10, 50, 50)
        
        # Verify final result
        assert cropped_path.exists()
        with Image.open(cropped_path) as img:
            assert img.size == (40, 40)  # 50-10, 50-10
    
    def test_add_text_optimize_workflow(self, sample_gif_path, test_output_dir):
        """Test add text -> optimize workflow."""
        # Step 1: Add text
        text_path = test_output_dir / "with_text.gif"
        add_text_to_gif(
            sample_gif_path, text_path, "Test Text",
            position=(10, 10), font_size=16, color=(255, 0, 0)
        )
        
        # Step 2: Optimize
        optimized_path = test_output_dir / "optimized.gif"
        optimize_gif(text_path, optimized_path, quality=75)
        
        # Verify final result
        assert optimized_path.exists()
        with Image.open(optimized_path) as img:
            assert img.size == (100, 100)
    
    def test_reverse_speed_control_workflow(self, sample_gif_path, test_output_dir):
        """Test reverse -> speed control workflow."""
        # Step 1: Reverse
        reversed_path = test_output_dir / "reversed.gif"
        reverse_gif(sample_gif_path, reversed_path)
        
        # Step 2: Change speed
        speed_path = test_output_dir / "speed_controlled.gif"
        change_gif_speed(reversed_path, speed_path, 2.0)
        
        # Verify final result
        assert speed_path.exists()
        with Image.open(speed_path) as img:
            assert img.size == (100, 100)
    
    def test_filter_effects_workflow(self, sample_gif_path, test_output_dir):
        """Test multiple filter effects workflow."""
        # Step 1: Apply blur filter
        blurred_path = test_output_dir / "blurred.gif"
        apply_gif_filter(sample_gif_path, blurred_path, "BLUR", intensity=1.0)
        
        # Step 2: Apply brightness adjustment
        bright_path = test_output_dir / "bright.gif"
        from gif_tools.core import adjust_gif_brightness
        adjust_gif_brightness(blurred_path, bright_path, 1.5)
        
        # Verify final result
        assert bright_path.exists()
        with Image.open(bright_path) as img:
            assert img.size == (100, 100)
    
    def test_extract_merge_workflow(self, sample_gif_path, test_output_dir):
        """Test extract frames -> merge workflow."""
        # Step 1: Extract frames
        frames_dir = test_output_dir / "frames"
        frames_dir.mkdir()
        frame_paths = extract_gif_frames(sample_gif_path, frames_dir, [0, 2])  # First and last frame
        
        # Step 2: Merge frames
        merged_path = test_output_dir / "merged.gif"
        merge_gifs(frame_paths, merged_path)
        
        # Verify final result
        assert merged_path.exists()
        with Image.open(merged_path) as img:
            assert img.size == (100, 100)
    
    def test_watermark_format_conversion_workflow(self, sample_gif_path, test_output_dir):
        """Test watermark -> format conversion workflow."""
        # Step 1: Add watermark
        watermarked_path = test_output_dir / "watermarked.gif"
        add_text_watermark_to_gif(
            sample_gif_path, watermarked_path, "Watermark",
            position="bottom_right", opacity=0.7
        )
        
        # Step 2: Convert format
        converted_path = test_output_dir / "converted.webp"
        convert_gif_format(watermarked_path, converted_path, "WEBP")
        
        # Verify final result
        assert converted_path.exists()
        with Image.open(converted_path) as img:
            assert img.size == (100, 100)
    
    def test_complex_workflow(self, sample_gif_path, test_output_dir):
        """Test complex multi-step workflow."""
        # Step 1: Resize
        resized_path = test_output_dir / "step1_resized.gif"
        resize_gif(sample_gif_path, resized_path, 60, 60)
        
        # Step 2: Rotate
        rotated_path = test_output_dir / "step2_rotated.gif"
        rotate_gif(resized_path, rotated_path, 180)
        
        # Step 3: Add text
        text_path = test_output_dir / "step3_text.gif"
        add_text_to_gif(
            rotated_path, text_path, "Processed",
            position=(5, 5), font_size=12, color=(0, 255, 0)
        )
        
        # Step 4: Apply filter
        filtered_path = test_output_dir / "step4_filtered.gif"
        apply_gif_filter(text_path, filtered_path, "SHARPEN", intensity=1.0)
        
        # Step 5: Optimize
        final_path = test_output_dir / "final.gif"
        optimize_gif(filtered_path, final_path, quality=80)
        
        # Verify final result
        assert final_path.exists()
        with Image.open(final_path) as img:
            assert img.size == (60, 60)


class TestErrorRecovery:
    """Test error recovery in workflows."""
    
    def test_workflow_with_invalid_step(self, sample_gif_path, test_output_dir):
        """Test workflow continues after invalid step."""
        # Step 1: Valid resize
        resized_path = test_output_dir / "resized.gif"
        resize_gif(sample_gif_path, resized_path, 50, 50)
        
        # Step 2: Invalid crop (should fail gracefully)
        with pytest.raises(Exception):
            crop_gif(resized_path, test_output_dir / "invalid.gif", 100, 100, 200, 200)
        
        # Step 3: Valid operation should still work
        rotated_path = test_output_dir / "rotated.gif"
        rotate_gif(resized_path, rotated_path, 90)
        
        assert rotated_path.exists()
    
    def test_workflow_with_missing_file(self, test_output_dir):
        """Test workflow handles missing files gracefully."""
        with pytest.raises(Exception):
            resize_gif("nonexistent.gif", test_output_dir / "output.gif", 50, 50)


class TestPerformanceWorkflows:
    """Test performance of complete workflows."""
    
    def test_large_gif_workflow(self, sample_gif_path, test_output_dir):
        """Test workflow performance with larger GIF."""
        # Create a larger GIF for testing
        large_gif_path = test_output_dir / "large.gif"
        
        # Create larger frames
        frames = []
        durations = []
        
        for i in range(5):  # 5 frames
            frame = Image.new('RGB', (200, 200), color=(i * 50, 100, 200 - i * 30))
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
        
        # Test workflow
        resized_path = test_output_dir / "large_resized.gif"
        resize_gif(large_gif_path, resized_path, 100, 100)
        
        rotated_path = test_output_dir / "large_rotated.gif"
        rotate_gif(resized_path, rotated_path, 90)
        
        optimized_path = test_output_dir / "large_optimized.gif"
        optimize_gif(rotated_path, optimized_path, quality=75)
        
        # Verify results
        assert optimized_path.exists()
        with Image.open(optimized_path) as img:
            assert img.size == (100, 100)
