"""
Unit tests for advanced GIF processing tools.

Tests add_text, rearrange, reverse, optimize, speed_control, and filter_effects functionality.
"""

import pytest
from pathlib import Path
from PIL import Image

from gif_tools.core import (
    GifTextAdder, add_text_to_gif, add_multiple_text_to_gif, get_text_info,
    GifRearranger, rearrange_gif_frames, move_gif_frame, get_gif_frame_info,
    GifReverser, reverse_gif, reverse_gif_with_info, get_reverse_info,
    GifOptimizer, optimize_gif, optimize_gif_by_quality, get_optimization_info,
    GifSpeedController, change_gif_speed, slow_down_gif, speed_up_gif, get_gif_speed_info,
    GifFilterApplier, apply_gif_filter, adjust_gif_brightness, get_gif_filter_info
)
from gif_tools.utils import ValidationError


class TestGifTextAdder:
    """Test GIF text addition functionality."""
    
    def test_gif_text_adder_init(self):
        """Test GifTextAdder initialization."""
        adder = GifTextAdder()
        assert adder is not None
    
    def test_add_text_invalid_path(self, temp_dir):
        """Test add text with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            add_text_to_gif("nonexistent.gif", output_path, "Test text")
    
    def test_add_text_empty_text(self, sample_gif_path, test_output_dir):
        """Test add text with empty text."""
        output_path = test_output_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            add_text_to_gif(sample_gif_path, output_path, "")
    
    def test_add_text_success(self, sample_gif_path, test_output_dir):
        """Test successful text addition."""
        output_path = test_output_dir / "text_added.gif"
        
        result_path = add_text_to_gif(
            sample_gif_path, output_path, "Test Text",
            position=(10, 10), font_size=20, color=(255, 0, 0)
        )
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_add_multiple_text(self, sample_gif_path, test_output_dir):
        """Test adding multiple text elements."""
        output_path = test_output_dir / "multiple_text.gif"
        
        text_elements = [
            {"text": "Text 1", "position": (10, 10), "color": (255, 0, 0)},
            {"text": "Text 2", "position": (10, 30), "color": (0, 255, 0)}
        ]
        
        result_path = add_multiple_text_to_gif(sample_gif_path, output_path, text_elements)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_get_text_info(self, sample_gif_path):
        """Test getting text information."""
        info = get_text_info(sample_gif_path)
        
        assert 'width' in info
        assert 'height' in info
        assert 'frame_count' in info
        assert 'is_animated' in info
        assert 'available_fonts' in info


class TestGifRearranger:
    """Test GIF frame rearrangement functionality."""
    
    def test_gif_rearranger_init(self):
        """Test GifRearranger initialization."""
        rearranger = GifRearranger()
        assert rearranger is not None
    
    def test_rearrange_frames_invalid_path(self, temp_dir):
        """Test rearrange with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            rearrange_gif_frames("nonexistent.gif", output_path, [0, 1, 2])
    
    def test_rearrange_frames_invalid_order(self, sample_gif_path, test_output_dir):
        """Test rearrange with invalid frame order."""
        output_path = test_output_dir / "output.gif"
        
        # Invalid frame order (wrong length)
        with pytest.raises(ValidationError):
            rearrange_gif_frames(sample_gif_path, output_path, [0, 1])
        
        # Invalid frame order (out of range)
        with pytest.raises(ValidationError):
            rearrange_gif_frames(sample_gif_path, output_path, [0, 1, 5])
    
    def test_rearrange_frames_success(self, sample_gif_path, test_output_dir):
        """Test successful frame rearrangement."""
        output_path = test_output_dir / "rearranged.gif"
        
        # Reverse the frame order
        result_path = rearrange_gif_frames(sample_gif_path, output_path, [2, 1, 0])
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_move_gif_frame(self, sample_gif_path, test_output_dir):
        """Test moving a single frame."""
        output_path = test_output_dir / "moved_frame.gif"
        
        result_path = move_gif_frame(sample_gif_path, output_path, 0, 2)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_get_gif_frame_info(self, sample_gif_path):
        """Test getting frame information."""
        info = get_gif_frame_info(sample_gif_path)
        
        assert 'frame_count' in info
        assert 'is_animated' in info
        assert 'frames' in info
        assert info['frame_count'] == 3
        assert info['is_animated'] is True


class TestGifReverser:
    """Test GIF reversal functionality."""
    
    def test_gif_reverser_init(self):
        """Test GifReverser initialization."""
        reverser = GifReverser()
        assert reverser is not None
    
    def test_reverse_gif_invalid_path(self, temp_dir):
        """Test reverse with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            reverse_gif("nonexistent.gif", output_path)
    
    def test_reverse_gif_success(self, sample_gif_path, test_output_dir):
        """Test successful GIF reversal."""
        output_path = test_output_dir / "reversed.gif"
        
        result_path = reverse_gif(sample_gif_path, output_path)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_reverse_gif_with_info(self, sample_gif_path, test_output_dir):
        """Test reverse with detailed information."""
        output_path = test_output_dir / "reversed_info.gif"
        
        info = reverse_gif_with_info(sample_gif_path, output_path)
        
        assert 'input_path' in info
        assert 'output_path' in info
        assert 'frame_count' in info
        assert 'reversed' in info
        assert info['reversed'] is True
    
    def test_get_reverse_info(self, sample_gif_path):
        """Test getting reverse information."""
        info = get_reverse_info(sample_gif_path)
        
        assert 'frame_count' in info
        assert 'is_animated' in info
        assert 'can_reverse' in info
        assert info['can_reverse'] is True


class TestGifOptimizer:
    """Test GIF optimization functionality."""
    
    def test_gif_optimizer_init(self):
        """Test GifOptimizer initialization."""
        optimizer = GifOptimizer()
        assert optimizer is not None
    
    def test_optimize_gif_invalid_path(self, temp_dir):
        """Test optimize with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            optimize_gif("nonexistent.gif", output_path)
    
    def test_optimize_gif_invalid_quality(self, sample_gif_path, test_output_dir):
        """Test optimize with invalid quality."""
        output_path = test_output_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            optimize_gif(sample_gif_path, output_path, quality=0)
        
        with pytest.raises(ValidationError):
            optimize_gif(sample_gif_path, output_path, quality=150)
    
    def test_optimize_gif_success(self, sample_gif_path, test_output_dir):
        """Test successful GIF optimization."""
        output_path = test_output_dir / "optimized.gif"
        
        result_path = optimize_gif(sample_gif_path, output_path, quality=75)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_optimize_gif_by_quality(self, sample_gif_path, test_output_dir):
        """Test optimize by quality level."""
        output_path = test_output_dir / "optimized_quality.gif"
        
        result_path = optimize_gif_by_quality(sample_gif_path, output_path, "medium")
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_get_optimization_info(self, sample_gif_path):
        """Test getting optimization information."""
        info = get_optimization_info(sample_gif_path)
        
        assert 'file_size' in info
        assert 'width' in info
        assert 'height' in info
        assert 'color_count' in info
        assert 'optimization_potential' in info


class TestGifSpeedController:
    """Test GIF speed control functionality."""
    
    def test_gif_speed_controller_init(self):
        """Test GifSpeedController initialization."""
        controller = GifSpeedController()
        assert controller is not None
    
    def test_change_speed_invalid_path(self, temp_dir):
        """Test change speed with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            change_gif_speed("nonexistent.gif", output_path, 2.0)
    
    def test_change_speed_invalid_multiplier(self, sample_gif_path, test_output_dir):
        """Test change speed with invalid multiplier."""
        output_path = test_output_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            change_gif_speed(sample_gif_path, output_path, -1.0)
    
    def test_change_speed_success(self, sample_gif_path, test_output_dir):
        """Test successful speed change."""
        output_path = test_output_dir / "speed_changed.gif"
        
        result_path = change_gif_speed(sample_gif_path, output_path, 2.0)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_slow_down_gif(self, sample_gif_path, test_output_dir):
        """Test slow down functionality."""
        output_path = test_output_dir / "slowed.gif"
        
        result_path = slow_down_gif(sample_gif_path, output_path, 0.5)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_speed_up_gif(self, sample_gif_path, test_output_dir):
        """Test speed up functionality."""
        output_path = test_output_dir / "sped_up.gif"
        
        result_path = speed_up_gif(sample_gif_path, output_path, 2.0)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_get_gif_speed_info(self, sample_gif_path):
        """Test getting speed information."""
        info = get_gif_speed_info(sample_gif_path)
        
        assert 'frame_count' in info
        assert 'is_animated' in info
        assert 'can_change_speed' in info
        assert 'fps' in info


class TestGifFilterApplier:
    """Test GIF filter effects functionality."""
    
    def test_gif_filter_applier_init(self):
        """Test GifFilterApplier initialization."""
        applier = GifFilterApplier()
        assert applier is not None
    
    def test_apply_filter_invalid_path(self, temp_dir):
        """Test apply filter with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            apply_gif_filter("nonexistent.gif", output_path, "BLUR")
    
    def test_apply_filter_invalid_filter(self, sample_gif_path, test_output_dir):
        """Test apply filter with invalid filter name."""
        output_path = test_output_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            apply_gif_filter(sample_gif_path, output_path, "INVALID_FILTER")
    
    def test_apply_filter_success(self, sample_gif_path, test_output_dir):
        """Test successful filter application."""
        output_path = test_output_dir / "filtered.gif"
        
        result_path = apply_gif_filter(sample_gif_path, output_path, "BLUR", intensity=1.0)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_adjust_brightness(self, sample_gif_path, test_output_dir):
        """Test brightness adjustment."""
        output_path = test_output_dir / "brightness.gif"
        
        result_path = adjust_gif_brightness(sample_gif_path, output_path, 1.5)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_get_gif_filter_info(self, sample_gif_path):
        """Test getting filter information."""
        info = get_gif_filter_info(sample_gif_path)
        
        assert 'width' in info
        assert 'height' in info
        assert 'available_filters' in info
        assert 'supports_filters' in info
