"""Coordinate detection, OCR, validation, tracking, and optional persistence."""

import logging
import uuid
from dataclasses import dataclass
from typing import List, Optional, Protocol, Sequence

import cv2
import numpy as np

from config import Config
from src.database import DatabaseConnectionError, PlateRepository, PlateRepositoryError
from src.detection.yolo_detector import Detection
from src.preprocessing.plate_preprocessor import PlatePreprocessor
from src.recognition.ocr_engine import OCREngine, OCRResult
from src.tracking.plate_tracker import PlateObservation, PlateTracker, TrackState
from src.validation.plate_validator import PlateValidator


logger = logging.getLogger(__name__)


class Detector(Protocol):
    def detect(self, frame: np.ndarray) -> List[Detection]:
        ...


@dataclass(frozen=True)
class FrameProcessingResult:
    """Aligned results for a single processed video frame."""

    detections: Sequence[Detection]
    ocr_results: Sequence[Optional[OCRResult]]
    track_states: Sequence[TrackState]


class PlatePipeline:
    """Run the modular ALPR pipeline for one frame at a time."""

    def __init__(
        self,
        detector: Detector,
        preprocessor: PlatePreprocessor,
        ocr_engine: Optional[OCREngine],
        validator: PlateValidator,
        tracker: PlateTracker,
        repository: Optional[PlateRepository] = None,
    ) -> None:
        self.detector = detector
        self.preprocessor = preprocessor
        self.ocr_engine = ocr_engine
        self.validator = validator
        self.tracker = tracker
        self.repository = repository
        self.ocr_frame_interval = Config.OCR_EVERY_N_FRAMES
        if self.ocr_frame_interval < 1:
            raise ValueError("OCR_EVERY_N_FRAMES must be a positive integer")

    def process_frame(self, frame: np.ndarray, frame_index: int) -> FrameProcessingResult:
        """Process a frame and keep all returned results aligned by detection."""
        detections = self.detector.detect(frame)
        crops = []
        ocr_results: List[Optional[OCRResult]] = []
        observations = []

        for detection in detections:
            crop = self._crop(frame, detection)
            crops.append(crop)
            ocr_result = self._recognize(crop, frame_index)
            ocr_results.append(ocr_result)

            accepted_plate = None
            if ocr_result is not None and self._passes_ocr_threshold(ocr_result):
                validation = self.validator.validate(ocr_result.text)
                if validation.is_valid:
                    accepted_plate = validation.normalized_text
                else:
                    logger.debug(
                        "Rejected OCR text %r: %s",
                        ocr_result.text,
                        validation.reason,
                    )

            observations.append(
                PlateObservation(
                    bbox=detection.bbox,
                    plate_number=accepted_plate,
                    detection_confidence=detection.confidence,
                    ocr_confidence=(
                        ocr_result.confidence if ocr_result is not None else None
                    ),
                )
            )

        track_states = self.tracker.update(observations, frame_index=frame_index)
        if self.repository is not None:
            for detection, crop, track in zip(detections, crops, track_states):
                if not track.should_save or not track.plate_number or crop is None:
                    continue
                confidence = (
                    track.confidence
                    if track.confidence is not None
                    else detection.confidence
                )
                try:
                    detection_id = self.repository.insert_detection(
                        plate_number=track.plate_number,
                        confidence=confidence,
                        camera_id=Config.CAMERA_ID,
                        image=crop if Config.SAVE_PLATE_IMAGES else None,
                    )
                except (DatabaseConnectionError, PlateRepositoryError, OSError):
                    logger.exception(
                        "Could not persist confirmed plate %s",
                        track.plate_number,
                    )
                else:
                    if detection_id is None:
                        logger.info("Skipped recent duplicate plate %s", track.plate_number)
                    else:
                        logger.info(
                            "Saved plate detection %s as record %s",
                            track.plate_number,
                            detection_id,
                        )

        return FrameProcessingResult(
            detections=detections,
            ocr_results=ocr_results,
            track_states=track_states,
        )

    def _recognize(
        self,
        crop: Optional[np.ndarray],
        frame_index: int,
    ) -> Optional[OCRResult]:
        if crop is None or self.ocr_engine is None:
            return None
        if (frame_index - 1) % self.ocr_frame_interval != 0:
            return None
        try:
            self._save_debug_image("plate_crop", crop)
            preprocessed = self.preprocessor.preprocess(crop)
            if preprocessed is None:
                logger.debug("Skipping OCR because plate preprocessing failed")
                return None
            self._save_debug_image("ocr_input", preprocessed)
            return self.ocr_engine.recognize(preprocessed)
        except (cv2.error, ImportError, OSError, RuntimeError, ValueError):
            logger.exception("Could not preprocess or OCR a detected plate")
            return None

    @staticmethod
    def _save_debug_image(stage: str, image: np.ndarray) -> None:
        if not (Config.DEBUG_MODE or Config.DEBUG_SAVE_INTERMEDIATE):
            return
        try:
            Config.DEBUG_DIR.mkdir(parents=True, exist_ok=True)
            path = Config.DEBUG_DIR / f"{stage}_{uuid.uuid4().hex}.png"
            if not cv2.imwrite(str(path), image):
                raise OSError(f"Could not save debug image: {path}")
        except (OSError, cv2.error):
            logger.exception("Could not save %s debug image", stage)

    @staticmethod
    def _passes_ocr_threshold(result: OCRResult) -> bool:
        return (
            result.confidence is None
            or result.confidence >= Config.OCR_CONFIDENCE_THRESHOLD
        )

    @staticmethod
    def _crop(
        frame: np.ndarray,
        detection: Detection,
    ) -> Optional[np.ndarray]:
        if frame is None or frame.size == 0:
            return None
        height, width = frame.shape[:2]
        x1 = max(0, min(width, int(detection.x1)))
        y1 = max(0, min(height, int(detection.y1)))
        x2 = max(0, min(width, int(detection.x2)))
        y2 = max(0, min(height, int(detection.y2)))
        if x2 <= x1 or y2 <= y1:
            return None
        return frame[y1:y2, x1:x2]
