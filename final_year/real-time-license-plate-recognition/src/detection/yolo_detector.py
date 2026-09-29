"""
YOLO License Plate Detector.
Detects license plates in images/frames using pre-trained YOLO model.
"""

import sys
import logging
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import Config


class Detection:
    """
    Represents a single license plate detection.
    
    Attributes:
        x1, y1, x2, y2: Bounding box coordinates (top-left, bottom-right)
        confidence: Detection confidence score (0.0 to 1.0)
        class_id: Class ID (usually 0 for license_plate)
        class_name: Class name (usually 'license_plate')
    """
    
    def __init__(self, x1: float, y1: float, x2: float, y2: float, 
                 confidence: float, class_id: int = 0, class_name: str = 'license_plate'):
        """Initialize detection."""
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)
        self.confidence = float(confidence)
        self.class_id = int(class_id)
        self.class_name = class_name
    
    @property
    def width(self) -> float:
        """Get bounding box width."""
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        """Get bounding box height."""
        return self.y2 - self.y1
    
    @property
    def area(self) -> float:
        """Get bounding box area."""
        return self.width * self.height
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get bounding box center."""
        cx = (self.x1 + self.x2) / 2
        cy = (self.y1 + self.y2) / 2
        return (cx, cy)
    
    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        """Get bounding box as tuple."""
        return (self.x1, self.y1, self.x2, self.y2)
    
    def __repr__(self):
        """String representation."""
        return (f"Detection(box=[{self.x1:.1f},{self.y1:.1f},{self.x2:.1f},{self.y2:.1f}], "
                f"conf={self.confidence:.2f}, class={self.class_name})")
    
    def __str__(self):
        """User-friendly string."""
        return f"{self.class_name} @ ({self.x1:.0f},{self.y1:.0f}) - Conf: {self.confidence:.2%}"


class YOLODetector:
    """
    YOLO-based license plate detector.
    
    Detects license plates in images using a pre-trained YOLOv8 model.
    Supports both GPU and CPU inference with configurable thresholds.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize YOLO detector.
        
        Args:
            model_path (str, optional): Path to YOLO model file.
                If None, uses Config.YOLO_MODEL_PATH
                
        Raises:
            FileNotFoundError: If model file doesn't exist
            ImportError: If ultralytics not installed
            ValueError: If model fails to load
        """
        self.logger = logging.getLogger(__name__)
        
        # Use provided path or config default
        self.model_path = model_path or Config.YOLO_MODEL_PATH
        
        # Import YOLO
        try:
            from ultralytics import YOLO
            self.YOLO = YOLO
        except ImportError as e:
            self.logger.error("ultralytics not installed. Install with: pip install ultralytics")
            raise ImportError("ultralytics library required") from e
        
        # Load model
        self._load_model()
        
        # Configuration
        self.conf_threshold = Config.YOLO_CONFIDENCE_THRESHOLD
        self.iou_threshold = Config.YOLO_IOU_THRESHOLD
        self.input_size = Config.YOLO_INPUT_SIZE
        self.device = Config.YOLO_DEVICE
        
        self.logger.info(f"YOLODetector initialized successfully")
        self.logger.info(f"  Model: {self.model_path}")
        self.logger.info(f"  Device: {self.device}")
        self.logger.info(f"  Confidence Threshold: {self.conf_threshold}")
        self.logger.info(f"  IoU Threshold: {self.iou_threshold}")
    
    def _load_model(self):
        """
        Load YOLO model from file.
        
        Raises:
            FileNotFoundError: If model file doesn't exist
            ValueError: If model fails to load
        """
        model_file = Path(self.model_path)
        
        if not model_file.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {self.model_path}\n"
                f"Download or train a license plate detection model and place it in: {self.model_path}"
            )
        
        try:
            self.model = self.YOLO(self.model_path)
            self.logger.info(f"Loaded YOLO model from: {self.model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load YOLO model: {e}")
            raise ValueError(f"Failed to load model: {e}") from e
    
    def detect(self, frame: np.ndarray, conf: Optional[float] = None, 
               iou: Optional[float] = None) -> List[Detection]:
        """
        Detect license plates in frame.
        
        Args:
            frame (np.ndarray): Input frame (BGR format from OpenCV)
            conf (float, optional): Confidence threshold (overrides default)
            iou (float, optional): IoU threshold for NMS (overrides default)
            
        Returns:
            List[Detection]: List of detected license plates (sorted by confidence)
            
        Raises:
            ValueError: If frame is invalid
        """
        if frame is None or frame.size == 0:
            self.logger.warning("Invalid frame provided")
            return []
        
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            self.logger.warning(f"Invalid frame shape: {frame.shape}, expected (H, W, 3)")
            return []
        
        try:
            # Use provided thresholds or defaults
            conf_threshold = conf if conf is not None else self.conf_threshold
            iou_threshold = iou if iou is not None else self.iou_threshold
            
            # Run inference
            results = self.model(
                frame,
                conf=conf_threshold,
                iou=iou_threshold,
                device=self.device,
                verbose=False
            )
            
            # Parse results
            detections = []
            
            if results and len(results) > 0:
                result = results[0]
                
                # Extract boxes, confidences, and class IDs
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()      # [x1, y1, x2, y2]
                    confs = result.boxes.conf.cpu().numpy()       # Confidence
                    class_ids = result.boxes.cls.cpu().numpy()    # Class ID
                    
                    # Create Detection objects
                    for box, conf, class_id in zip(boxes, confs, class_ids):
                        x1, y1, x2, y2 = box
                        detection = Detection(
                            x1=x1, y1=y1, x2=x2, y2=y2,
                            confidence=conf,
                            class_id=int(class_id),
                            class_name='license_plate'
                        )
                        detections.append(detection)
            
            # Sort by confidence (descending)
            detections.sort(key=lambda d: d.confidence, reverse=True)
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Error during detection: {e}")
            return []
    
    def detect_batch(self, frames: List[np.ndarray]) -> List[List[Detection]]:
        """
        Detect license plates in multiple frames.
        
        Args:
            frames (List[np.ndarray]): List of input frames
            
        Returns:
            List[List[Detection]]: Detections for each frame
        """
        return [self.detect(frame) for frame in frames]
    
    def set_confidence_threshold(self, threshold: float):
        """
        Set confidence threshold.
        
        Args:
            threshold (float): Confidence threshold (0.0 to 1.0)
            
        Raises:
            ValueError: If threshold not in valid range
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Confidence threshold must be 0.0-1.0, got {threshold}")
        
        self.conf_threshold = threshold
        self.logger.info(f"Confidence threshold set to {threshold}")
    
    def set_iou_threshold(self, threshold: float):
        """
        Set IoU threshold for non-maximum suppression.
        
        Args:
            threshold (float): IoU threshold (0.0 to 1.0)
            
        Raises:
            ValueError: If threshold not in valid range
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"IoU threshold must be 0.0-1.0, got {threshold}")
        
        self.iou_threshold = threshold
        self.logger.info(f"IoU threshold set to {threshold}")
    
    def get_model_info(self) -> dict:
        """
        Get YOLO model information.
        
        Returns:
            dict: Model information (names, task, etc.)
        """
        return {
            'model_path': str(self.model_path),
            'device': self.device,
            'confidence_threshold': self.conf_threshold,
            'iou_threshold': self.iou_threshold,
            'input_size': self.input_size,
            'model_names': self.model.names if hasattr(self.model, 'names') else {}
        }
    
    def __repr__(self):
        """String representation."""
        return (f"YOLODetector(model={self.model_path}, device={self.device}, "
                f"conf={self.conf_threshold}, iou={self.iou_threshold})")
