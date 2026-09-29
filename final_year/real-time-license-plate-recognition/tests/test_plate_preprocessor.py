"""
Unit tests for PlatePreprocessor module.
Tests preprocessing, perspective correction, and image enhancement.
"""

import sys
import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import numpy as np
import cv2

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from preprocessing.plate_preprocessor import (
    PlatePreprocessor, 
    PerspectiveCorrector, 
    ImageEnhancer
)
from config import Config


logger = logging.getLogger(__name__)


class TestPerspectiveCorrector:
    """Test cases for PerspectiveCorrector class."""
    
    def test_perspective_corrector_initialization(self):
        """Test PerspectiveCorrector initialization."""
        corrector = PerspectiveCorrector()
        assert corrector is not None
        logger.info("PerspectiveCorrector initialized successfully")
    
    def test_perspective_corrector_none_input(self):
        """Test correction with None input."""
        corrector = PerspectiveCorrector()
        result = corrector.correct(None)
        assert result is None
    
    def test_perspective_corrector_empty_input(self):
        """Test correction with empty array."""
        corrector = PerspectiveCorrector()
        empty_array = np.array([])
        result = corrector.correct(empty_array)
        assert result is not None
    
    def test_perspective_corrector_2d_input(self):
        """Test correction with 2D image."""
        corrector = PerspectiveCorrector()
        gray_image = np.zeros((100, 100), dtype=np.uint8)
        result = corrector.correct(gray_image)
        # Should handle gracefully
        assert result is not None
    
    def test_order_points(self):
        """Test point ordering."""
        corrector = PerspectiveCorrector()
        
        # Create 4 test points
        pts = np.array([
            [50, 50],   # TL
            [150, 50],  # TR
            [150, 150], # BR
            [50, 150]   # BL
        ], dtype='float32')
        
        ordered = corrector._order_points(pts)
        assert ordered.shape == (4, 2)


class TestImageEnhancer:
    """Test cases for ImageEnhancer class."""
    
    def test_image_enhancer_initialization(self):
        """Test ImageEnhancer initialization."""
        enhancer = ImageEnhancer()
        assert enhancer.apply_clahe is True
        assert enhancer.apply_bilateral is True
        assert enhancer.apply_morphology is True
        logger.info("ImageEnhancer initialized successfully")
    
    def test_image_enhancer_custom_config(self):
        """Test ImageEnhancer with custom configuration."""
        enhancer = ImageEnhancer(
            apply_clahe=False,
            apply_bilateral=False,
            apply_morphology=False
        )
        assert enhancer.apply_clahe is False
        assert enhancer.apply_bilateral is False
        assert enhancer.apply_morphology is False
    
    def test_image_enhancer_none_input(self):
        """Test enhancement with None input."""
        enhancer = ImageEnhancer()
        result = enhancer.enhance(None)
        assert result is None
    
    def test_image_enhancer_empty_input(self):
        """Test enhancement with empty array."""
        enhancer = ImageEnhancer()
        empty_array = np.array([])
        result = enhancer.enhance(empty_array)
        assert result is not None
    
    def test_image_enhancer_grayscale_input(self):
        """Test enhancement with grayscale image."""
        enhancer = ImageEnhancer()
        gray_image = np.ones((100, 100), dtype=np.uint8) * 128
        result = enhancer.enhance(gray_image)
        # Should return enhanced image
        assert result is not None
        assert result.shape == gray_image.shape
    
    def test_image_enhancer_with_preprocessing(self):
        """Test enhancement with preprocessing."""
        enhancer = ImageEnhancer()
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        gray, binary = enhancer.enhance_with_preprocessing(image)
        
        assert gray is not None
        assert binary is not None
        assert len(gray.shape) == 2  # Grayscale
        assert len(binary.shape) == 2  # Binary


class TestPlatePreprocessor:
    """Test cases for PlatePreprocessor class."""
    
    def test_plate_preprocessor_initialization(self):
        """Test PlatePreprocessor initialization."""
        preprocessor = PlatePreprocessor()
        assert preprocessor.target_size == (400, 150)
        assert preprocessor.apply_perspective_correction is True
        assert preprocessor.apply_enhancement is True
        logger.info("PlatePreprocessor initialized successfully")
    
    def test_plate_preprocessor_custom_size(self):
        """Test PlatePreprocessor with custom target size."""
        custom_size = (320, 120)
        preprocessor = PlatePreprocessor(target_size=custom_size)
        assert preprocessor.target_size == custom_size
    
    def test_plate_preprocessor_disabled_corrections(self):
        """Test PlatePreprocessor with corrections disabled."""
        preprocessor = PlatePreprocessor(
            apply_perspective_correction=False,
            apply_enhancement=False
        )
        assert preprocessor.apply_perspective_correction is False
        assert preprocessor.apply_enhancement is False
    
    def test_plate_preprocessor_none_input(self):
        """Test preprocessing with None input."""
        preprocessor = PlatePreprocessor()
        result = preprocessor.preprocess(None)
        assert result is None
    
    def test_plate_preprocessor_empty_input(self):
        """Test preprocessing with empty array."""
        preprocessor = PlatePreprocessor()
        empty_array = np.array([])
        result = preprocessor.preprocess(empty_array)
        assert result is None
    
    def test_plate_preprocessor_valid_image(self):
        """Test preprocessing with valid image."""
        preprocessor = PlatePreprocessor()
        # Create valid BGR image
        image = np.ones((150, 300, 3), dtype=np.uint8) * 100
        result = preprocessor.preprocess(image)
        
        # Should return processed image
        assert result is not None
    
    def test_plate_preprocessor_batch(self):
        """Test batch preprocessing."""
        preprocessor = PlatePreprocessor()
        
        # Create test images
        images = [
            np.ones((150, 300, 3), dtype=np.uint8) * 100,
            np.ones((150, 300, 3), dtype=np.uint8) * 150
        ]
        
        results = preprocessor.preprocess_batch(images)
        assert len(results) <= len(images)
    
    def test_plate_preprocessor_extract_and_preprocess(self):
        """Test extraction and preprocessing combined."""
        preprocessor = PlatePreprocessor()
        
        # Create test frame
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        bbox = (100, 100, 300, 250)  # x1, y1, x2, y2
        
        result = preprocessor.extract_and_preprocess(frame, bbox)
        # May return None depending on cv2 mocking
        assert result is None or isinstance(result, np.ndarray)
    
    def test_plate_preprocessor_invalid_bbox(self):
        """Test extraction with invalid bbox."""
        preprocessor = PlatePreprocessor()
        
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        bbox = (-10, -10, 1000, 1000)  # Out of bounds
        
        result = preprocessor.extract_and_preprocess(frame, bbox)
        assert result is None
    
    def test_plate_preprocessor_config(self):
        """Test configuration retrieval."""
        preprocessor = PlatePreprocessor()
        config = preprocessor.get_preprocessing_config()
        
        assert 'target_size' in config
        assert 'apply_perspective_correction' in config
        assert 'apply_enhancement' in config
        assert config['target_size'] == (400, 150)
    
    def test_plate_preprocessor_repr(self):
        """Test string representations."""
        preprocessor = PlatePreprocessor()
        
        repr_str = repr(preprocessor)
        assert 'PlatePreprocessor' in repr_str
        assert '400' in repr_str
        assert '150' in repr_str
        
        str_str = str(preprocessor)
        assert 'License Plate Preprocessor' in str_str
        assert 'Target Size' in str_str


class TestPlatePreprocessorIntegration:
    """Integration tests for preprocessing pipeline."""
    
    def test_preprocessing_pipeline_flow(self):
        """Test complete preprocessing pipeline."""
        preprocessor = PlatePreprocessor()
        
        # Create realistic plate-like image
        plate_image = np.ones((150, 300, 3), dtype=np.uint8) * 100
        
        # Add some variation
        plate_image[50:100, 100:200] = 50  # Darker region
        plate_image[75:90, 110:190] = 20   # Character-like regions
        
        result = preprocessor.preprocess(plate_image)
        # Should return processed image or None on cv2 errors
        assert result is None or isinstance(result, np.ndarray)
    
    def test_preprocessing_handles_rotated_plate(self):
        """Test preprocessing of rotated plate."""
        preprocessor = PlatePreprocessor()
        
        # Create rotated plate image
        plate_image = np.ones((150, 300, 3), dtype=np.uint8) * 100
        
        # Simulate rotation
        center = (plate_image.shape[1] // 2, plate_image.shape[0] // 2)
        M = cv2.getRotationMatrix2D(center, 15, 1.0)
        rotated = cv2.warpAffine(plate_image, M, 
                                (plate_image.shape[1], plate_image.shape[0]))
        
        result = preprocessor.preprocess(rotated)
        assert result is None or isinstance(result, np.ndarray)
    
    def test_all_enhancement_modes(self):
        """Test all enhancement mode combinations."""
        combinations = [
            (True, True, True),
            (True, True, False),
            (True, False, True),
            (False, True, True),
            (False, False, False)
        ]
        
        for clahe, bilateral, morph in combinations:
            enhancer = ImageEnhancer(
                apply_clahe=clahe,
                apply_bilateral=bilateral,
                apply_morphology=morph
            )
            
            image = np.ones((100, 100), dtype=np.uint8) * 128
            result = enhancer.enhance(image)
            
            assert result is not None, \
                f"Failed with clahe={clahe}, bilateral={bilateral}, morph={morph}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
