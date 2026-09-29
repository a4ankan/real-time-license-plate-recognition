"""
Plate Preprocessing & Enhancement Engine.
Extracts, enhances, and prepares license plate regions for OCR.
"""

import sys
import logging
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
import cv2

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import Config


logger = logging.getLogger(__name__)


class PerspectiveCorrector:
    """
    Corrects perspective distortion in plate images.
    
    Handles cases where plates are captured at angles, using feature detection
    and homography transformation to rectify the plate region.
    """
    
    def __init__(self):
        """Initialize perspective corrector."""
        self.detector = cv2.SIFT_create() if hasattr(cv2, 'SIFT_create') else None
        self.matcher = None
        if self.detector:
            self.matcher = cv2.BFMatcher()
        logger.info("PerspectiveCorrector initialized")
    
    def correct(self, plate_crop: np.ndarray) -> np.ndarray:
        """
        Apply perspective correction to plate image.
        
        Args:
            plate_crop: Cropped plate region (BGR image)
            
        Returns:
            Perspective-corrected plate image
        """
        if plate_crop is None or plate_crop.size == 0:
            logger.warning("Invalid plate image for perspective correction")
            return plate_crop
        
        if len(plate_crop.shape) != 3:
            logger.warning("Perspective correction requires 3-channel image")
            return plate_crop
        
        # For basic implementation, return original
        # Advanced: Could use corner detection and homography
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
            
            # Simple edge detection for plate boundary
            edges = cv2.Canny(gray, 100, 200)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                logger.debug("No contours found for perspective correction")
                return plate_crop
            
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Approximate to quadrilateral
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            
            if len(approx) != 4:
                logger.debug(f"Expected 4 corners, found {len(approx)}")
                return plate_crop
            
            # Get ordered corners
            pts = approx.reshape(4, 2)
            rect = self._order_points(pts)
            
            # Compute homography
            (tl, tr, br, bl) = rect
            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            maxWidth = max(int(widthA), int(widthB))
            
            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            maxHeight = max(int(heightA), int(heightB))
            
            # Destination points
            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]
            ], dtype="float32")
            
            # Perspective transform
            M = cv2.getPerspectiveTransform(rect.astype("float32"), dst)
            warped = cv2.warpPerspective(plate_crop, M, (maxWidth, maxHeight))
            
            logger.debug(f"Perspective correction applied: {plate_crop.shape} -> {warped.shape}")
            return warped
            
        except Exception as e:
            logger.debug(f"Perspective correction failed: {e}")
            return plate_crop
    
    @staticmethod
    def _order_points(pts: np.ndarray) -> np.ndarray:
        """
        Order points in clockwise order: TL, TR, BR, BL.
        
        Args:
            pts: Array of 4 points
            
        Returns:
            Ordered points array
        """
        rect = np.zeros((4, 2), dtype="float32")
        
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        
        return rect


class ImageEnhancer:
    """
    Enhances plate image for OCR readability.
    
    Applies contrast stretching, brightness normalization, and noise reduction
    to improve character recognition accuracy.
    """
    
    def __init__(self, 
                 apply_clahe: bool = True,
                 apply_bilateral: bool = True,
                 apply_morphology: bool = True):
        """
        Initialize image enhancer.
        
        Args:
            apply_clahe: Apply CLAHE for contrast enhancement
            apply_bilateral: Apply bilateral filter for denoising
            apply_morphology: Apply morphological operations
        """
        self.apply_clahe = apply_clahe
        self.apply_bilateral = apply_bilateral
        self.apply_morphology = apply_morphology
        
        # CLAHE parameters
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        logger.info(f"ImageEnhancer initialized: CLAHE={apply_clahe}, "
                   f"Bilateral={apply_bilateral}, Morphology={apply_morphology}")
    
    def enhance(self, image: np.ndarray) -> np.ndarray:
        """
        Apply enhancement pipeline to plate image.
        
        Args:
            image: Input image (BGR or grayscale)
            
        Returns:
            Enhanced image
        """
        if image is None or image.size == 0:
            logger.warning("Invalid image for enhancement")
            return image
        
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 1. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            if self.apply_clahe:
                gray = self.clahe.apply(gray)
                logger.debug("CLAHE applied")
            
            # 2. Apply bilateral filter (denoising while preserving edges)
            if self.apply_bilateral:
                gray = cv2.bilateralFilter(gray, 9, 75, 75)
                logger.debug("Bilateral filter applied")
            
            # 3. Apply morphological operations
            if self.apply_morphology:
                # Morphological opening (remove small noise)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
                logger.debug("Morphological opening applied")
            
            # 4. Optional: Apply threshold
            _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            logger.debug("Otsu thresholding applied")
            
            logger.debug(f"Enhancement complete: {image.shape} -> {gray.shape}")
            return gray
            
        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            return image
    
    def enhance_with_preprocessing(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Enhanced preprocessing with intermediate steps.
        
        Returns both grayscale and binary versions.
        
        Args:
            image: Input image
            
        Returns:
            Tuple of (grayscale, binary) images
        """
        enhanced_gray = self.enhance(image)
        
        # Create binary version
        if len(enhanced_gray.shape) == 3:
            enhanced_gray = cv2.cvtColor(enhanced_gray, cv2.COLOR_BGR2GRAY)
        
        _, binary = cv2.threshold(enhanced_gray, 0, 255, 
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return enhanced_gray, binary


class PlatePreprocessor:
    """
    Main preprocessing engine for license plate images.
    
    Orchestrates extraction, perspective correction, and enhancement
    to prepare plates for OCR.
    """
    
    def __init__(self,
                 target_size: Tuple[int, int] = (400, 150),
                 apply_perspective_correction: bool = True,
                 apply_enhancement: bool = True):
        """
        Initialize plate preprocessor.
        
        Args:
            target_size: Target output size (width, height)
            apply_perspective_correction: Enable perspective correction
            apply_enhancement: Enable image enhancement
        """
        self.target_size = target_size
        self.apply_perspective_correction = apply_perspective_correction
        self.apply_enhancement = apply_enhancement
        
        # Initialize sub-processors
        self.perspective_corrector = (PerspectiveCorrector() 
                                     if apply_perspective_correction else None)
        self.enhancer = (ImageEnhancer() if apply_enhancement else None)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"PlatePreprocessor initialized: target_size={target_size}")
    
    def preprocess(self, plate_crop: np.ndarray) -> np.ndarray:
        """
        Complete preprocessing pipeline for plate region.
        
        Steps:
        1. Validate input
        2. Apply perspective correction
        3. Resize to target size
        4. Apply enhancement
        5. Return processed image
        
        Args:
            plate_crop: Cropped plate region (BGR image)
            
        Returns:
            Preprocessed plate image (grayscale, ready for OCR)
        """
        if plate_crop is None or plate_crop.size == 0:
            self.logger.warning("Invalid plate crop for preprocessing")
            return None
        
        try:
            # Step 1: Perspective correction
            if self.apply_perspective_correction and self.perspective_corrector:
                plate_crop = self.perspective_corrector.correct(plate_crop)
            
            # Step 2: Resize to target size
            resized = cv2.resize(plate_crop, self.target_size, 
                                interpolation=cv2.INTER_LINEAR)
            self.logger.debug(f"Resized to {self.target_size}")
            
            # Step 3: Enhancement
            if self.apply_enhancement and self.enhancer:
                enhanced = self.enhancer.enhance(resized)
            else:
                # Fallback: just convert to grayscale
                if len(resized.shape) == 3:
                    enhanced = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                else:
                    enhanced = resized
            
            self.logger.debug(f"Preprocessing complete: {plate_crop.shape} -> {enhanced.shape}")
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Preprocessing failed: {e}")
            return None
    
    def preprocess_batch(self, plate_crops: list) -> list:
        """
        Preprocess multiple plate crops.
        
        Args:
            plate_crops: List of cropped plate regions
            
        Returns:
            List of preprocessed images
        """
        results = []
        for i, crop in enumerate(plate_crops):
            processed = self.preprocess(crop)
            if processed is not None:
                results.append(processed)
            else:
                self.logger.warning(f"Failed to preprocess crop {i}")
        
        return results
    
    def extract_and_preprocess(self, frame: np.ndarray, bbox: Tuple[float, float, float, float]) -> Optional[np.ndarray]:
        """
        Extract plate region from frame and preprocess it.
        
        Args:
            frame: Full frame (BGR image)
            bbox: Bounding box (x1, y1, x2, y2) from detection
            
        Returns:
            Preprocessed plate image or None on failure
        """
        if frame is None or frame.size == 0:
            self.logger.warning("Invalid frame for extraction")
            return None
        
        try:
            x1, y1, x2, y2 = bbox
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Validate coordinates
            if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
                self.logger.warning(f"Invalid bbox for frame shape {frame.shape}")
                return None
            
            # Extract region
            plate_crop = frame[y1:y2, x1:x2]
            
            if plate_crop.size == 0:
                self.logger.warning("Empty plate crop after extraction")
                return None
            
            # Preprocess
            return self.preprocess(plate_crop)
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return None
    
    def get_preprocessing_config(self) -> dict:
        """
        Get preprocessing configuration.
        
        Returns:
            Dictionary with configuration details
        """
        return {
            'target_size': self.target_size,
            'apply_perspective_correction': self.apply_perspective_correction,
            'apply_enhancement': self.apply_enhancement,
            'clahe_enabled': self.enhancer.apply_clahe if self.enhancer else False,
            'bilateral_filter_enabled': self.enhancer.apply_bilateral if self.enhancer else False,
            'morphology_enabled': self.enhancer.apply_morphology if self.enhancer else False,
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"PlatePreprocessor(target_size={self.target_size}, "
                f"perspective={self.apply_perspective_correction}, "
                f"enhancement={self.apply_enhancement})")
    
    def __str__(self) -> str:
        """Friendly string representation."""
        return (f"License Plate Preprocessor\n"
                f"  Target Size: {self.target_size}\n"
                f"  Perspective Correction: {'Enabled' if self.apply_perspective_correction else 'Disabled'}\n"
                f"  Enhancement: {'Enabled' if self.apply_enhancement else 'Disabled'}")
