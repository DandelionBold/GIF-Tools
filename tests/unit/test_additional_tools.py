"""
Unit tests for additional GIF processing tools.

Tests extract_frames, loop_settings, format_conversion, batch_processing, and watermark functionality.
"""

import pytest
from pathlib import Path
from PIL import Image

from gif_tools.core import (
    GifFrameExtractor, extract_gif_frames, extract_gif_frame_range, get_gif_extraction_info,
    GifLoopController, set_gif_loop_count, set_gif_infinite_loop, get_gif_loop_info,
    GifFormatConverter, convert_gif_format, convert_gif_to_webp, get_gif_conversion_info,
    GifBatchProcessor, process_gif_batch, resize_gif_batch, get_gif_batch_info,
    GifWatermarker, add_text_watermark_to_gif, add_image_watermark_to_gif, get_gif_watermark_info
)
from gif_tools.utils import ValidationError


class TestGifFrameExtractor:
    """Test GIF frame extraction functionality."""
    
    def test_gif_frame_extractor_init(self):
        """Test GifFrameExtractor initialization."""
        extractor = GifFrameExtractor()
        assert extractor is not None
    
    def test_extract_frames_invalid_path(self, temp_dir):
        """Test extract frames with invalid input path."""
        output_dir = temp_dir / "output"
        
        with pytest.raises(ValidationError):
            extract_gif_frames("nonexistent.gif", output_dir)
    
    def test_extract_frames_invalid_indices(self, sample_gif_path, test_output_dir):
        """Test extract frames with invalid frame indices."""
        with pytest.raises(ValidationError):
            extract_gif_frames(sample_gif_path, test_output_dir, [0, 1, 5])  # Out of range
    
    def test_extract_frames_success(self, sample_gif_path, test_output_dir):
        """Test successful frame extraction."""
        result_paths = extract_gif_frames(sample_gif_path, test_output_dir, [0, 1, 2])
        
        assert len(result_paths) == 3
        assert all(path.exists() for path in result_paths)
        
        # Verify all files are valid images
        for path in result_paths:
            with Image.open(path) as img:
                assert img.size == (100, 100)
    
    def test_extract_frame_range(self, sample_gif_path, test_output_dir):
        """Test frame range extraction."""
        result_paths = extract_gif_frame_range(sample_gif_path, test_output_dir, 0, 2)
        
        assert len(result_paths) == 2  # 0 to 2 (exclusive)
        assert all(path.exists() for path in result_paths)
    
    def test_extract_every_nth_frame(self, sample_gif_path, test_output_dir):
        """Test every nth frame extraction."""
        result_paths = extract_gif_frames(sample_gif_path, test_output_dir, None, "PNG", 95, "frame")
        
        assert len(result_paths) == 3  # All frames
        assert all(path.suffix.lower() == '.png' for path in result_paths)
    
    def test_get_gif_extraction_info(self, sample_gif_path):
        """Test getting extraction information."""
        info = get_gif_extraction_info(sample_gif_path)
        
        assert 'frame_count' in info
        assert 'is_animated' in info
        assert 'can_extract' in info
        assert 'supported_formats' in info
        assert info['frame_count'] == 3
        assert info['is_animated'] is True


class TestGifLoopController:
    """Test GIF loop settings functionality."""
    
    def test_gif_loop_controller_init(self):
        """Test GifLoopController initialization."""
        controller = GifLoopController()
        assert controller is not None
    
    def test_set_loop_count_invalid_path(self, temp_dir):
        """Test set loop count with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            set_gif_loop_count("nonexistent.gif", output_path, 2)
    
    def test_set_loop_count_invalid_count(self, sample_gif_path, test_output_dir):
        """Test set loop count with invalid count."""
        output_path = test_output_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            set_gif_loop_count(sample_gif_path, output_path, -1)
    
    def test_set_loop_count_success(self, sample_gif_path, test_output_dir):
        """Test successful loop count setting."""
        output_path = test_output_dir / "looped.gif"
        
        result_path = set_gif_loop_count(sample_gif_path, output_path, 2)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_set_infinite_loop(self, sample_gif_path, test_output_dir):
        """Test infinite loop setting."""
        output_path = test_output_dir / "infinite_loop.gif"
        
        result_path = set_gif_infinite_loop(sample_gif_path, output_path)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_get_gif_loop_info(self, sample_gif_path):
        """Test getting loop information."""
        info = get_gif_loop_info(sample_gif_path)
        
        assert 'frame_count' in info
        assert 'is_animated' in info
        assert 'can_set_loop' in info
        assert 'loop_count' in info
        assert info['is_animated'] is True


class TestGifFormatConverter:
    """Test GIF format conversion functionality."""
    
    def test_gif_format_converter_init(self):
        """Test GifFormatConverter initialization."""
        converter = GifFormatConverter()
        assert converter is not None
    
    def test_convert_format_invalid_path(self, temp_dir):
        """Test convert format with invalid input path."""
        output_path = temp_dir / "output.webp"
        
        with pytest.raises(ValidationError):
            convert_gif_format("nonexistent.gif", output_path, "WEBP")
    
    def test_convert_format_invalid_format(self, sample_gif_path, test_output_dir):
        """Test convert format with invalid target format."""
        output_path = test_output_dir / "output.invalid"
        
        with pytest.raises(ValidationError):
            convert_gif_format(sample_gif_path, output_path, "INVALID")
    
    def test_convert_format_success(self, sample_gif_path, test_output_dir):
        """Test successful format conversion."""
        output_path = test_output_dir / "converted.webp"
        
        result_path = convert_gif_format(sample_gif_path, output_path, "WEBP")
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_convert_to_webp(self, sample_gif_path, test_output_dir):
        """Test convert to WebP."""
        output_path = test_output_dir / "converted.webp"
        
        result_path = convert_gif_to_webp(sample_gif_path, output_path)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_get_gif_conversion_info(self, sample_gif_path):
        """Test getting conversion information."""
        info = get_gif_conversion_info(sample_gif_path)
        
        assert 'current_format' in info
        assert 'supported_formats' in info
        assert 'can_convert' in info
        assert 'conversion_options' in info


class TestGifBatchProcessor:
    """Test GIF batch processing functionality."""
    
    def test_gif_batch_processor_init(self):
        """Test GifBatchProcessor initialization."""
        processor = GifBatchProcessor()
        assert processor is not None
    
    def test_process_batch_invalid_dir(self, temp_dir):
        """Test process batch with invalid input directory."""
        output_dir = temp_dir / "output"
        
        with pytest.raises(ValidationError):
            process_gif_batch("nonexistent_dir", output_dir, "resize", width=100, height=100)
    
    def test_process_batch_empty_dir(self, temp_dir):
        """Test process batch with empty directory."""
        input_dir = temp_dir / "empty"
        input_dir.mkdir()
        output_dir = temp_dir / "output"
        
        with pytest.raises(ValidationError):
            process_gif_batch(input_dir, output_dir, "resize", width=100, height=100)
    
    def test_process_batch_success(self, sample_gif_path, test_output_dir):
        """Test successful batch processing."""
        # Create input directory with sample GIF
        input_dir = sample_gif_path.parent
        output_dir = test_output_dir / "batch_output"
        
        result = process_gif_batch(input_dir, output_dir, "resize", width=50, height=50)
        
        assert 'total_files' in result
        assert 'processed_files' in result
        assert 'failed_files' in result
        assert result['total_files'] >= 1
        assert result['processed_files'] >= 1
    
    def test_resize_gif_batch(self, sample_gif_path, test_output_dir):
        """Test resize batch processing."""
        input_dir = sample_gif_path.parent
        output_dir = test_output_dir / "resize_batch"
        
        result = resize_gif_batch(input_dir, output_dir, 50, 50)
        
        assert 'total_files' in result
        assert 'processed_files' in result
        assert result['operation'] == 'resize'
    
    def test_get_gif_batch_info(self, sample_gif_path):
        """Test getting batch information."""
        input_dir = sample_gif_path.parent
        
        info = get_gif_batch_info(input_dir)
        
        assert 'total_files' in info
        assert 'total_size' in info
        assert 'file_info' in info
        assert 'supported_operations' in info
        assert info['total_files'] >= 1


class TestGifWatermarker:
    """Test GIF watermarking functionality."""
    
    def test_gif_watermarker_init(self):
        """Test GifWatermarker initialization."""
        watermarker = GifWatermarker()
        assert watermarker is not None
    
    def test_add_text_watermark_invalid_path(self, temp_dir):
        """Test add text watermark with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            add_text_watermark_to_gif("nonexistent.gif", output_path, "Test")
    
    def test_add_text_watermark_empty_text(self, sample_gif_path, test_output_dir):
        """Test add text watermark with empty text."""
        output_path = test_output_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            add_text_watermark_to_gif(sample_gif_path, output_path, "")
    
    def test_add_text_watermark_success(self, sample_gif_path, test_output_dir):
        """Test successful text watermark addition."""
        output_path = test_output_dir / "watermarked.gif"
        
        result_path = add_text_watermark_to_gif(
            sample_gif_path, output_path, "Test Watermark",
            position="bottom_right", opacity=0.7
        )
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_add_image_watermark_success(self, sample_gif_path, sample_image_path, test_output_dir):
        """Test successful image watermark addition."""
        output_path = test_output_dir / "image_watermarked.gif"
        
        result_path = add_image_watermark_to_gif(
            sample_gif_path, output_path, sample_image_path,
            position="bottom_right", opacity=0.7, scale=0.2
        )
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_get_gif_watermark_info(self, sample_gif_path):
        """Test getting watermark information."""
        info = get_gif_watermark_info(sample_gif_path)
        
        assert 'width' in info
        assert 'height' in info
        assert 'watermark_positions' in info
        assert 'supports_watermarks' in info
        assert 'recommended_watermark_size' in info
