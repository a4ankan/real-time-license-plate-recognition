"""
Unit tests for YOLODetector module.
Tests detection functionality, error handling, and API methods.
"""

import sys
import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from unittest.mock import mock_open

import numpy as np

# Mock ultralytics before importing
sys.modules['ultralytics'] = MagicMock()
sys.modules['ultralytics.YOLO'] = MagicMock()

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from detection.yolo_detector import YOLODetector, Detection
from config import Config


logger = logging.getLogger(__name__)


class TestDetection:
    """Test cases for Detection class."""
    
    def test_detection_initialization(self):
        """Test Detection object creation."""
        det = Detection(x1=10, y1=20, x2=100, y2=120, confidence=0.95)
        
        assert det.x1 == 10
        assert det.y1 == 20
        assert det.x2 == 100
        assert det.y2 == 120
        assert det.confidence == 0.95
        assert det.class_name == 'license_plate'
    
    def test_detection_properties(self):
        """Test Detection property calculations."""
        det = Detection(x1=10, y1=20, x2=110, y2=120, confidence=0.9)
        
        # Width and height
        assert det.width == 100
        assert det.height == 100
        
        # Area
        assert det.area == 10000
        
        # Center
        cx, cy = det.center
        assert cx == 60
        assert cy == 70
        
        # Bounding box
        bbox = det.bbox
        assert bbox == (10, 20, 110, 120)
    
    def test_detection_string_repr(self):
        """Test Detection string representations."""
        det = Detection(x1=10, y1=20, x2=100, y2=120, confidence=0.95)
        
        # __repr__
        repr_str = repr(det)
        assert 'Detection' in repr_str
        
        # __str__
        str_str = str(det)
        assert 'license_plate' in str_str
        assert '95' in str_str  # Check for 95 in string


class TestYOLODetector:
    """Test cases for YOLODetector class."""
    
    def test_yolo_detector_init_missing_model(self):
        """Test YOLODetector initialization with missing model."""
        with patch('detection.yolo_detector.Path.exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                detector = YOLODetector()
    
    def test_yolo_detector_init_success(self):
        """Test successful YOLODetector initialization."""
        with patch('detection.yolo_detector.Path.exists', return_value=True):
            with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: MagicMock() if name == 'ultralytics' else __import__(name, *args, **kwargs)):
                with patch.object(YOLODetector, '_load_model'):
                    detector = YOLODetector()
                    
                    assert detector.conf_threshold == Config.YOLO_CONFIDENCE_THRESHOLD
                    assert detector.iou_threshold == Config.YOLO_IOU_THRESHOLD
                    assert detector.input_size == Config.YOLO_INPUT_SIZE
                    assert detector.device == Config.YOLO_DEVICE
    
    def test_yolo_detector_detect_invalid_frame(self):
        """Test detection with invalid frame."""
        with patch('detection.yolo_detector.Path.exists', return_value=True):
            with patch.object(YOLODetector, '_load_model'):
                detector = YOLODetector()
                
                # None frame
                detections = detector.detect(None)
                assert detections == []
                
                # Empty frame
                detections = detector.detect(np.array([]))
                assert detections == []
                
                # Wrong shape (grayscale)
                frame = np.zeros((100, 100))
                detections = detector.detect(frame)
                assert detections == []
    
    def test_yolo_detector_detect_valid_frame(self):
        """Test detection with valid frame."""
        with patch('detection.yolo_detector.Path.exists', return_value=True):
            with patch.object(YOLODetector, '_load_model'):
                detector = YOLODetector()
                detector.model = MagicMock()
                
                # Mock YOLO model
                mock_result = MagicMock()
                mock_boxes = MagicMock()
                
                # Simulate detection results
                mock_boxes.xyxy.cpu.return_value.numpy.return_value = np.array([
                    [10, 20, 100, 120],
                    [150, 50, 250, 150]
                ])
                mock_boxes.conf.cpu.return_value.numpy.return_value = np.array([0.95, 0.87])
                mock_boxes.cls.cpu.return_value.numpy.return_value = np.array([0, 0])
                
                mock_result.boxes = mock_boxes
                detector.model.return_value = [mock_result]
                
                # Create valid frame
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                
                detections = detector.detect(frame)
                
                # Check results
                assert len(detections) == 2
                assert detections[0].confidence > detections[1].confidence  # Sorted by confidence
                assert detections[0].confidence == 0.95
                assert detections[1].confidence == 0.87
    
    def test_yolo_detector_set_confidence_threshold(self):
        """Test setting confidence threshold."""
        with patch('detection.yolo_detector.Path.exists', return_value=True):
            with patch.object(YOLODetector, '_load_model'):
                detector = YOLODetector()
                
                # Valid threshold
                detector.set_confidence_threshold(0.7)
                assert detector.conf_threshold == 0.7
                
                # Invalid threshold (too high)
                with pytest.raises(ValueError):
                    detector.set_confidence_threshold(1.5)
                
                # Invalid threshold (negative)
                with pytest.raises(ValueError):
                    detector.set_confidence_threshold(-0.1)
    
    def test_yolo_detector_set_iou_threshold(self):
        """Test setting IoU threshold."""
        with patch('detection.yolo_detector.Path.exists', return_value=True):
            with patch.object(YOLODetector, '_load_model'):
                detector = YOLODetector()
                
                # Valid threshold
                detector.set_iou_threshold(0.5)
                assert detector.iou_threshold == 0.5
                
                # Invalid threshold
                with pytest.raises(ValueError):
                    detector.set_iou_threshold(1.5)
    
    def test_yolo_detector_get_model_info(self):
        """Test getting model information."""
        with patch('detection.yolo_detector.Path.exists', return_value=True):
            with patch.object(YOLODetector, '_load_model'):
                detector = YOLODetector()
                # Add mock model attribute
                detector.model = MagicMock()
                
                info = detector.get_model_info()
                
                assert 'model_path' in info
                assert 'device' in info
                assert 'confidence_threshold' in info
                assert 'iou_threshold' in info
                assert 'input_size' in info
    
    def test_yolo_detector_detect_batch(self):
        """Test batch detection."""
        with patch('detection.yolo_detector.Path.exists', return_value=True):
            with patch.object(YOLODetector, '_load_model'):
                with patch.object(YOLODetector, 'detect') as mock_detect:
                    detector = YOLODetector()
                    
                    # Mock detect to return empty list
                    mock_detect.return_value = []
                    
                    frames = [
                        np.zeros((100, 100, 3), dtype=np.uint8),
                        np.zeros((100, 100, 3), dtype=np.uint8)
                    ]
                    
                    results = detector.detect_batch(frames)
                    
                    assert len(results) == 2
    
    def test_yolo_detector_repr(self):
        """Test YOLODetector string representation."""
        with patch('detection.yolo_detector.Path.exists', return_value=True):
            with patch.object(YOLODetector, '_load_model'):
                detector = YOLODetector()
                
                repr_str = repr(detector)
                assert 'YOLODetector' in repr_str
                assert 'device' in repr_str


class TestYOLODetectorIntegration:
    """Integration tests for YOLODetector."""
    
    def test_detection_sorting(self):
        """Test that detections are sorted by confidence."""
        with patch('detection.yolo_detector.Path.exists', return_value=True):
            with patch.object(YOLODetector, '_load_model'):
                detector = YOLODetector()
                detector.model = MagicMock()
                
                # Mock YOLO model with unsorted detections
                mock_result = MagicMock()
                mock_boxes = MagicMock()
                
                # Return detections with lower confidence first (unsorted)
                mock_boxes.xyxy.cpu.return_value.numpy.return_value = np.array([
                    [10, 20, 100, 120],
                    [150, 50, 250, 150]
                ])
                mock_boxes.conf.cpu.return_value.numpy.return_value = np.array([0.75, 0.95])
                mock_boxes.cls.cpu.return_value.numpy.return_value = np.array([0, 0])
                
                mock_result.boxes = mock_boxes
                detector.model.return_value = [mock_result]
                
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                detections = detector.detect(frame)
                
                # Check sorting
                assert detections[0].confidence == 0.95
                assert detections[1].confidence == 0.75


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
