"""
Unit tests for utility modules.

Tests file_handlers, image_utils, validation, and constants functionality.
"""

import pytest
from pathlib import Path
from PIL import Image

from gif_tools.utils import (
    validate_animated_file, validate_output_path, validate_quality,
    validate_size, validate_position, validate_color, validate_speed_multiplier,
    get_image_processor, get_temp_file, get_temp_directory,
    load_image, save_image, resize_image, crop_image, rotate_image,
    SUPPORTED_ANIMATED_FORMATS, SUPPORTED_IMAGE_FORMATS,
    DEFAULT_QUALITY, DEFAULT_SIZE, QUALITY_LEVELS
)
from gif_tools.utils import ValidationError


class TestValidation:
    """Test validation functions."""
    
    def test_validate_animated_file_valid(self, sample_gif_path):
        """Test validate animated file with valid path."""
        result = validate_animated_file(sample_gif_path)
        assert result == sample_gif_path
    
    def test_validate_animated_file_invalid(self):
        """Test validate animated file with invalid path."""
        with pytest.raises(ValidationError):
            validate_animated_file("nonexistent.gif")
        
        with pytest.raises(ValidationError):
            validate_animated_file("")
    
    def test_validate_output_path_valid(self, temp_dir):
        """Test validate output path with valid path."""
        output_path = temp_dir / "output.gif"
        result = validate_output_path(output_path)
        assert result == output_path
    
    def test_validate_output_path_invalid(self):
        """Test validate output path with invalid path."""
        with pytest.raises(ValidationError):
            validate_output_path("")
    
    def test_validate_quality_valid(self):
        """Test validate quality with valid values."""
        assert validate_quality(50) == 50
        assert validate_quality(85) == 85
        assert validate_quality(100) == 100
    
    def test_validate_quality_invalid(self):
        """Test validate quality with invalid values."""
        with pytest.raises(ValidationError):
            validate_quality(0)
        
        with pytest.raises(ValidationError):
            validate_quality(150)
    
    def test_validate_size_valid(self):
        """Test validate size with valid values."""
        assert validate_size((100, 100)) == (100, 100)
        assert validate_size((50, 200)) == (50, 200)
    
    def test_validate_size_invalid(self):
        """Test validate size with invalid values."""
        with pytest.raises(ValidationError):
            validate_size((0, 0))
        
        with pytest.raises(ValidationError):
            validate_size((-1, 100))
    
    def test_validate_position_valid(self):
        """Test validate position with valid values."""
        assert validate_position((10, 20)) == (10, 20)
        assert validate_position((0, 0)) == (0, 0)
    
    def test_validate_position_invalid(self):
        """Test validate position with invalid values."""
        with pytest.raises(ValidationError):
            validate_position((-1, 10))
        
        with pytest.raises(ValidationError):
            validate_position((10, -5))
    
    def test_validate_color_valid(self):
        """Test validate color with valid values."""
        assert validate_color((255, 0, 0)) == (255, 0, 0, 255)
        assert validate_color((255, 0, 0, 128)) == (255, 0, 0, 128)
        assert validate_color("red") == (255, 0, 0, 255)
    
    def test_validate_color_invalid(self):
        """Test validate color with invalid values."""
        with pytest.raises(ValidationError):
            validate_color((-1, 0, 0))
        
        with pytest.raises(ValidationError):
            validate_color((256, 0, 0))
    
    def test_validate_speed_multiplier_valid(self):
        """Test validate speed multiplier with valid values."""
        assert validate_speed_multiplier(0.5) == 0.5
        assert validate_speed_multiplier(1.0) == 1.0
        assert validate_speed_multiplier(2.0) == 2.0
    
    def test_validate_speed_multiplier_invalid(self):
        """Test validate speed multiplier with invalid values."""
        with pytest.raises(ValidationError):
            validate_speed_multiplier(0)
        
        with pytest.raises(ValidationError):
            validate_speed_multiplier(-1.0)


class TestFileHandlers:
    """Test file handling functions."""
    
    def test_get_image_processor(self):
        """Test get image processor."""
        processor = get_image_processor()
        assert processor is not None
    
    def test_get_temp_file(self, temp_dir):
        """Test get temporary file."""
        temp_file = get_temp_file(temp_dir, "test", "gif")
        assert temp_file.parent == temp_dir
        assert temp_file.suffix == ".gif"
        assert "test" in temp_file.name
    
    def test_get_temp_directory(self, temp_dir):
        """Test get temporary directory."""
        temp_dir_path = get_temp_directory(temp_dir, "test")
        assert temp_dir_path.parent == temp_dir
        assert "test" in temp_dir_path.name


class TestImageUtils:
    """Test image utility functions."""
    
    def test_load_image_valid(self, sample_gif_path):
        """Test load image with valid path."""
        image = load_image(sample_gif_path)
        assert isinstance(image, Image.Image)
        assert image.size == (100, 100)
    
    def test_load_image_invalid(self):
        """Test load image with invalid path."""
        with pytest.raises(ValidationError):
            load_image("nonexistent.gif")
    
    def test_save_image(self, sample_gif_path, temp_dir):
        """Test save image."""
        output_path = temp_dir / "saved.gif"
        
        with Image.open(sample_gif_path) as img:
            save_image(img, output_path)
        
        assert output_path.exists()
        
        # Verify saved image
        with Image.open(output_path) as saved_img:
            assert saved_img.size == (100, 100)
    
    def test_resize_image(self, sample_gif_path):
        """Test resize image."""
        with Image.open(sample_gif_path) as img:
            resized = resize_image(img, (50, 50))
            assert resized.size == (50, 50)
    
    def test_crop_image(self, sample_gif_path):
        """Test crop image."""
        with Image.open(sample_gif_path) as img:
            cropped = crop_image(img, 10, 10, 50, 50)
            assert cropped.size == (40, 40)
    
    def test_rotate_image(self, sample_gif_path):
        """Test rotate image."""
        with Image.open(sample_gif_path) as img:
            rotated = rotate_image(img, 90)
            assert rotated.size == (100, 100)  # Size preserved for 90° rotation


class TestConstants:
    """Test constants and configuration."""
    
    def test_supported_animated_formats(self):
        """Test supported animated formats."""
        assert 'GIF' in SUPPORTED_ANIMATED_FORMATS
        assert 'WEBP' in SUPPORTED_ANIMATED_FORMATS
        assert 'APNG' in SUPPORTED_ANIMATED_FORMATS
    
    def test_supported_image_formats(self):
        """Test supported image formats."""
        assert 'PNG' in SUPPORTED_IMAGE_FORMATS
        assert 'JPEG' in SUPPORTED_IMAGE_FORMATS
        assert 'BMP' in SUPPORTED_IMAGE_FORMATS
    
    def test_default_quality(self):
        """Test default quality value."""
        assert DEFAULT_QUALITY == 85
        assert 1 <= DEFAULT_QUALITY <= 100
    
    def test_default_size(self):
        """Test default size value."""
        assert DEFAULT_SIZE == (100, 100)
        assert len(DEFAULT_SIZE) == 2
        assert all(size > 0 for size in DEFAULT_SIZE)
    
    def test_quality_levels(self):
        """Test quality levels."""
        assert 'low' in QUALITY_LEVELS
        assert 'medium' in QUALITY_LEVELS
        assert 'high' in QUALITY_LEVELS
        assert 'ultra' in QUALITY_LEVELS
        
        # Check quality values are valid
        for level, quality in QUALITY_LEVELS.items():
            assert 1 <= quality <= 100


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_validation_error_messages(self):
        """Test validation error messages are informative."""
        try:
            validate_quality(0)
        except ValidationError as e:
            assert "quality" in str(e).lower()
        
        try:
            validate_size((0, 0))
        except ValidationError as e:
            assert "size" in str(e).lower()
    
    def test_file_not_found_handling(self):
        """Test file not found error handling."""
        with pytest.raises(ValidationError):
            validate_animated_file("nonexistent_file.gif")
    
    def test_invalid_input_types(self):
        """Test invalid input type handling."""
        with pytest.raises(ValidationError):
            validate_quality("invalid")
        
        with pytest.raises(ValidationError):
            validate_size("invalid")
        
        with pytest.raises(ValidationError):
            validate_position("invalid")
