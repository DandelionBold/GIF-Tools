"""
Unit tests for basic GIF processing tools.

Tests video_to_gif, resize, rotate, crop, split, and merge functionality.
"""

import pytest
from pathlib import Path
from PIL import Image

from gif_tools.core import (
    VideoToGifConverter, convert_video_to_gif, get_video_info,
    GifResizer, resize_gif, resize_gif_by_percentage, get_resize_info,
    GifRotator, rotate_gif, flip_gif_horizontal, flip_gif_vertical, get_rotation_info,
    GifCropper, crop_gif, crop_gif_center, get_crop_info,
    GifSplitter, split_gif, split_gif_to_images, get_split_info,
    GifMerger, merge_gifs, merge_gifs_horizontal, get_merge_info
)
from gif_tools.utils import ValidationError


class TestVideoToGif:
    """Test video to GIF conversion functionality."""
    
    def test_video_to_gif_converter_init(self):
        """Test VideoToGifConverter initialization."""
        converter = VideoToGifConverter()
        assert converter is not None
    
    def test_convert_video_to_gif_invalid_path(self, temp_dir):
        """Test video conversion with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            convert_video_to_gif("nonexistent.mp4", output_path)
    
    def test_get_video_info_invalid_path(self):
        """Test getting video info with invalid path."""
        with pytest.raises(ValidationError):
            get_video_info("nonexistent.mp4")
    
    def test_convert_video_to_gif_mock(self, sample_video_path, test_output_dir):
        """Test video conversion with mock video (will fail gracefully)."""
        output_path = test_output_dir / "output.gif"
        
        # This will fail because we don't have a real video file
        # but it tests the validation and error handling
        with pytest.raises(ValidationError):
            convert_video_to_gif(sample_video_path, output_path)


class TestGifResize:
    """Test GIF resizing functionality."""
    
    def test_gif_resizer_init(self):
        """Test GifResizer initialization."""
        resizer = GifResizer()
        assert resizer is not None
    
    def test_resize_gif_invalid_path(self, temp_dir):
        """Test resize with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            resize_gif("nonexistent.gif", output_path, 200, 200)
    
    def test_resize_gif_invalid_size(self, sample_gif_path, test_output_dir):
        """Test resize with invalid size parameters."""
        output_path = test_output_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            resize_gif(sample_gif_path, output_path, 0, 0)
        
        with pytest.raises(ValidationError):
            resize_gif(sample_gif_path, output_path, -1, 100)
    
    def test_resize_gif_success(self, sample_gif_path, test_output_dir):
        """Test successful GIF resize."""
        output_path = test_output_dir / "resized.gif"
        
        result_path = resize_gif(sample_gif_path, output_path, 50, 50)
        
        assert result_path == output_path
        assert output_path.exists()
        
        # Verify output is a valid GIF
        with Image.open(output_path) as img:
            assert img.size == (50, 50)
    
    def test_resize_gif_by_percentage(self, sample_gif_path, test_output_dir):
        """Test resize by percentage."""
        output_path = test_output_dir / "resized_percent.gif"
        
        result_path = resize_gif_by_percentage(sample_gif_path, output_path, 50)
        
        assert result_path == output_path
        assert output_path.exists()
        
        # Verify output size is 50% of original
        with Image.open(output_path) as img:
            assert img.size == (50, 50)  # 50% of 100x100
    
    def test_get_resize_info(self, sample_gif_path):
        """Test getting resize information."""
        info = get_resize_info(sample_gif_path)
        
        assert 'width' in info
        assert 'height' in info
        assert 'size' in info
        assert info['width'] == 100
        assert info['height'] == 100


class TestGifRotate:
    """Test GIF rotation functionality."""
    
    def test_gif_rotator_init(self):
        """Test GifRotator initialization."""
        rotator = GifRotator()
        assert rotator is not None
    
    def test_rotate_gif_invalid_path(self, temp_dir):
        """Test rotate with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            rotate_gif("nonexistent.gif", output_path, 90)
    
    def test_rotate_gif_invalid_angle(self, sample_gif_path, test_output_dir):
        """Test rotate with invalid angle."""
        output_path = test_output_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            rotate_gif(sample_gif_path, output_path, 45)  # Invalid angle
    
    def test_rotate_gif_90_degrees(self, sample_gif_path, test_output_dir):
        """Test rotate 90 degrees."""
        output_path = test_output_dir / "rotated_90.gif"
        
        result_path = rotate_gif(sample_gif_path, output_path, 90)
        
        assert result_path == output_path
        assert output_path.exists()
        
        # Verify output is rotated
        with Image.open(output_path) as img:
            assert img.size == (100, 100)  # Size should be preserved
    
    def test_rotate_gif_180_degrees(self, sample_gif_path, test_output_dir):
        """Test rotate 180 degrees."""
        output_path = test_output_dir / "rotated_180.gif"
        
        result_path = rotate_gif(sample_gif_path, output_path, 180)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_rotate_gif_270_degrees(self, sample_gif_path, test_output_dir):
        """Test rotate 270 degrees."""
        output_path = test_output_dir / "rotated_270.gif"
        
        result_path = rotate_gif(sample_gif_path, output_path, 270)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_flip_gif_horizontal(self, sample_gif_path, test_output_dir):
        """Test horizontal flip."""
        output_path = test_output_dir / "flipped_h.gif"
        
        result_path = flip_gif_horizontal(sample_gif_path, output_path)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_flip_gif_vertical(self, sample_gif_path, test_output_dir):
        """Test vertical flip."""
        output_path = test_output_dir / "flipped_v.gif"
        
        result_path = flip_gif_vertical(sample_gif_path, output_path)
        
        assert result_path == output_path
        assert output_path.exists()
    
    def test_get_rotation_info(self, sample_gif_path):
        """Test getting rotation information."""
        info = get_rotation_info(sample_gif_path)
        
        assert 'width' in info
        assert 'height' in info
        assert 'size' in info
        assert 'can_rotate' in info


class TestGifCrop:
    """Test GIF cropping functionality."""
    
    def test_gif_cropper_init(self):
        """Test GifCropper initialization."""
        cropper = GifCropper()
        assert cropper is not None
    
    def test_crop_gif_invalid_path(self, temp_dir):
        """Test crop with invalid input path."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            crop_gif("nonexistent.gif", output_path, 10, 10, 50, 50)
    
    def test_crop_gif_invalid_region(self, sample_gif_path, test_output_dir):
        """Test crop with invalid crop region."""
        output_path = test_output_dir / "output.gif"
        
        # Invalid crop region (negative coordinates)
        with pytest.raises(ValidationError):
            crop_gif(sample_gif_path, output_path, -1, -1, 50, 50)
        
        # Invalid crop region (outside image bounds)
        with pytest.raises(ValidationError):
            crop_gif(sample_gif_path, output_path, 50, 50, 200, 200)
    
    def test_crop_gif_success(self, sample_gif_path, test_output_dir):
        """Test successful GIF crop."""
        output_path = test_output_dir / "cropped.gif"
        
        result_path = crop_gif(sample_gif_path, output_path, 10, 10, 50, 50)
        
        assert result_path == output_path
        assert output_path.exists()
        
        # Verify output size
        with Image.open(output_path) as img:
            assert img.size == (40, 40)  # 50-10, 50-10
    
    def test_crop_gif_center(self, sample_gif_path, test_output_dir):
        """Test center crop."""
        output_path = test_output_dir / "cropped_center.gif"
        
        result_path = crop_gif_center(sample_gif_path, output_path, 50, 50)
        
        assert result_path == output_path
        assert output_path.exists()
        
        # Verify output size
        with Image.open(output_path) as img:
            assert img.size == (50, 50)
    
    def test_get_crop_info(self, sample_gif_path):
        """Test getting crop information."""
        info = get_crop_info(sample_gif_path)
        
        assert 'width' in info
        assert 'height' in info
        assert 'size' in info
        assert 'can_crop' in info


class TestGifSplit:
    """Test GIF splitting functionality."""
    
    def test_gif_splitter_init(self):
        """Test GifSplitter initialization."""
        splitter = GifSplitter()
        assert splitter is not None
    
    def test_split_gif_invalid_path(self, temp_dir):
        """Test split with invalid input path."""
        output_dir = temp_dir / "output"
        
        with pytest.raises(ValidationError):
            split_gif("nonexistent.gif", output_dir)
    
    def test_split_gif_success(self, sample_gif_path, test_output_dir):
        """Test successful GIF split."""
        result_paths = split_gif(sample_gif_path, test_output_dir)
        
        assert len(result_paths) == 3  # Should have 3 frames
        assert all(path.exists() for path in result_paths)
        
        # Verify all files are valid images
        for path in result_paths:
            with Image.open(path) as img:
                assert img.size == (100, 100)
    
    def test_split_gif_to_images(self, sample_gif_path, test_output_dir):
        """Test split to images with specific format."""
        result_paths = split_gif_to_images(sample_gif_path, test_output_dir, "PNG")
        
        assert len(result_paths) == 3
        assert all(path.suffix.lower() == '.png' for path in result_paths)
    
    def test_get_split_info(self, sample_gif_path):
        """Test getting split information."""
        info = get_split_info(sample_gif_path)
        
        assert 'frame_count' in info
        assert 'is_animated' in info
        assert 'can_split' in info
        assert info['frame_count'] == 3
        assert info['is_animated'] is True


class TestGifMerge:
    """Test GIF merging functionality."""
    
    def test_gif_merger_init(self):
        """Test GifMerger initialization."""
        merger = GifMerger()
        assert merger is not None
    
    def test_merge_gifs_invalid_paths(self, temp_dir):
        """Test merge with invalid input paths."""
        output_path = temp_dir / "output.gif"
        
        with pytest.raises(ValidationError):
            merge_gifs(["nonexistent1.gif", "nonexistent2.gif"], output_path)
    
    def test_merge_gifs_success(self, sample_gif_path, test_output_dir):
        """Test successful GIF merge."""
        output_path = test_output_dir / "merged.gif"
        
        # Merge the same GIF with itself
        result_path = merge_gifs([sample_gif_path, sample_gif_path], output_path)
        
        assert result_path == output_path
        assert output_path.exists()
        
        # Verify output has more frames
        with Image.open(output_path) as img:
            assert getattr(img, 'n_frames', 1) == 6  # 3 + 3 frames
    
    def test_merge_gifs_horizontal(self, sample_gif_path, test_output_dir):
        """Test horizontal merge."""
        output_path = test_output_dir / "merged_h.gif"
        
        result_path = merge_gifs_horizontal([sample_gif_path, sample_gif_path], output_path)
        
        assert result_path == output_path
        assert output_path.exists()
        
        # Verify output size (should be wider)
        with Image.open(output_path) as img:
            assert img.size[0] == 200  # 100 + 100 width
            assert img.size[1] == 100  # height should be same
    
    def test_get_merge_info(self, sample_gif_path):
        """Test getting merge information."""
        info = get_merge_info(sample_gif_path)
        
        assert 'width' in info
        assert 'height' in info
        assert 'frame_count' in info
        assert 'can_merge' in info
