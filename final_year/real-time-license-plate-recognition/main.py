"""
Real-Time License Plate Detection and Recognition System
Entry point for the application.

This is a modular, production-grade system for detecting and recognizing
vehicle license plates from live video streams or pre-recorded videos using
YOLO object detection and OCR.

Current Phase: Video Stream Implementation
"""

import sys
import logging
import argparse
import time
from pathlib import Path

import cv2

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import Config
from video import VideoStream
from detection import YOLODetector
from preprocessing import PlatePreprocessor


def setup_logging():
    """Configure logging for the application."""
    log_level = logging.DEBUG if Config.DEBUG_MODE else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('license_plate_recognition.log')
        ]
    )
    
    return logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Real-Time License Plate Recognition System'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        default='webcam',
        help='Video source: "webcam" for camera, or path to video file (default: webcam)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode (saves intermediate images)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


def phase2_test_video_stream(source='webcam', debug=False, verbose=False):
    """
    Phase 2: Test video stream functionality.
    
    Args:
        source (str): 'webcam' or path to video file
        debug (bool): Enable debug mode
        verbose (bool): Enable verbose logging
        
    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("\n" + "="*70)
        logger.info("PHASE 2: VIDEO STREAM IMPLEMENTATION")
        logger.info("="*70)
        
        # Determine video source
        if source.lower() == 'webcam':
            video_source = Config.CAMERA_ID
            logger.info(f"Using webcam (ID: {video_source})")
        else:
            video_source = source
            logger.info(f"Using video file: {video_source}")
        
        # Open video stream
        logger.info("Opening video stream...")
        stream = VideoStream(source=video_source)
        logger.info(f"[OK] Video stream opened: {stream}")
        
        # Read frames
        logger.info("\nReading frames (press 'q' to quit)...")
        logger.info("-" * 70)
        
        frame_num = 0
        last_fps_time = time.time()
        
        while True:
            # Read frame
            success, frame = stream.read()
            
            if not success:
                logger.info(f"\nEnd of stream reached after {stream.get_frame_count()} frames")
                break
            
            frame_num += 1
            current_time = time.time()
            
            # Update FPS calculation
            stream.update_fps(current_time, last_fps_time)
            last_fps_time = current_time
            
            # Display frame info periodically (every 30 frames)
            if frame_num % 30 == 0:
                fps = stream.get_fps()
                pos = stream.get_position()
                progress = stream.get_progress()
                
                log_msg = f"Frame {frame_num} | FPS: {fps:.1f} | Position: {pos}"
                
                if not stream.is_webcam_source() and stream.total_frames > 0:
                    log_msg += f" | Progress: {progress:.1f}%"
                
                logger.info(log_msg)
            
            # Add FPS overlay on frame
            fps = stream.get_fps()
            frame = add_fps_overlay(frame, fps)
            
            # Display frame
            cv2.imshow('Video Stream - Press Q to Quit', frame)
            
            # Wait for key press (1ms timeout)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("\nUser quit requested")
                break
        
        # Cleanup
        logger.info("-" * 70)
        stream.release()
        cv2.destroyAllWindows()
        
        logger.info(f"[OK] Video stream closed")
        logger.info(f"Total frames read: {stream.get_frame_count()}")
        logger.info(f"Average FPS: {stream.current_fps:.1f}")
        
        logger.info("\n" + "="*70)
        logger.info("PHASE 2 COMPLETE: Video Stream Working")
        logger.info("="*70)
        logger.info("\nNext Phase: YOLO License Plate Detection")
        logger.info("="*70 + "\n")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"[ERROR] {e}")
        return 1
    except ValueError as e:
        logger.error(f"[ERROR] {e}")
        return 1
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error: {e}", exc_info=True)
        return 1


def add_fps_overlay(frame, fps):
    """
    Add FPS text overlay on frame.
    
    Args:
        frame: OpenCV frame
        fps: Current FPS value
        
    Returns:
        frame: Frame with FPS overlay
    """
    text = f"FPS: {fps:.1f}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (10, 30)
    font_scale = 0.7
    color = (0, 255, 0)  # Green
    thickness = 2
    
    cv2.putText(frame, text, org, font, font_scale, color, thickness)
    return frame


def draw_detections(frame, detections):
    """
    Draw detection boxes on frame.
    
    Args:
        frame: OpenCV frame
        detections: List of Detection objects
        
    Returns:
        frame: Frame with detection boxes
    """
    for detection in detections:
        x1, y1, x2, y2 = int(detection.x1), int(detection.y1), int(detection.x2), int(detection.y2)
        
        # Draw bounding box
        color = (0, 255, 0)  # Green
        thickness = 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        
        # Draw label
        label = f"{detection.class_name}: {detection.confidence:.1%}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        label_y = max(y1 - 5, label_size[1])
        
        # Background for text
        cv2.rectangle(frame, (x1, label_y - label_size[1] - 4), 
                     (x1 + label_size[0], label_y), color, -1)
        
        # Text
        cv2.putText(frame, label, (x1, label_y - 2), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, (0, 0, 0), 1)
    
    return frame


def phase3_test_yolo_detector(source='webcam', debug=False, verbose=False):
    """
    Phase 3: Test YOLO license plate detection.
    
    Args:
        source (str): 'webcam' or path to video file
        debug (bool): Enable debug mode
        verbose (bool): Enable verbose logging
        
    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("\n" + "="*70)
        logger.info("PHASE 3: YOLO LICENSE PLATE DETECTION")
        logger.info("="*70)
        
        # Initialize YOLO detector
        logger.info("\nInitializing YOLO detector...")
        try:
            detector = YOLODetector()
            logger.info(f"[OK] Detector loaded: {detector}")
        except FileNotFoundError as e:
            logger.error(f"[ERROR] {e}")
            logger.error("\nTo continue with Phase 3, you need a trained YOLO model:")
            logger.error("  1. Train on license plate dataset, OR")
            logger.error("  2. Download pre-trained model, OR")
            logger.error("  3. Use transfer learning from YOLOv8")
            logger.error(f"\nPlace model at: {Config.YOLO_MODEL_PATH}")
            return 1
        except ImportError as e:
            logger.error(f"[ERROR] Missing dependency: {e}")
            logger.error("Install with: pip install ultralytics")
            return 1
        
        # Determine video source
        if source.lower() == 'webcam':
            video_source = Config.CAMERA_ID
            logger.info(f"Using webcam (ID: {video_source})")
        else:
            video_source = source
            logger.info(f"Using video file: {video_source}")
        
        # Open video stream
        logger.info("Opening video stream...")
        stream = VideoStream(source=video_source)
        logger.info(f"[OK] Video stream opened")
        
        # Detection loop
        logger.info("\nDetecting license plates (press 'q' to quit)...")
        logger.info("-" * 70)
        
        frame_num = 0
        detection_count = 0
        last_fps_time = time.time()
        
        while True:
            # Read frame
            success, frame = stream.read()
            
            if not success:
                logger.info(f"\nEnd of stream reached after {stream.get_frame_count()} frames")
                break
            
            frame_num += 1
            current_time = time.time()
            
            # Update FPS calculation
            stream.update_fps(current_time, last_fps_time)
            last_fps_time = current_time
            
            # Run detection
            detections = detector.detect(frame)
            detection_count += len(detections)
            
            # Display frame info periodically (every 30 frames)
            if frame_num % 30 == 0:
                fps = stream.get_fps()
                pos = stream.get_position()
                progress = stream.get_progress()
                
                log_msg = f"Frame {frame_num} | FPS: {fps:.1f} | Detections: {len(detections)}"
                
                if not stream.is_webcam_source() and stream.total_frames > 0:
                    log_msg += f" | Progress: {progress:.1f}%"
                
                logger.info(log_msg)
                
                # Log detection details
                if detections:
                    for det in detections:
                        logger.info(f"  └─ {det}")
            
            # Add overlays
            fps = stream.get_fps()
            frame = add_fps_overlay(frame, fps)
            frame = draw_detections(frame, detections)
            
            # Add detection count overlay
            det_text = f"Detections: {len(detections)}"
            cv2.putText(frame, det_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow('YOLO Detection - Press Q to Quit', frame)
            
            # Wait for key press (1ms timeout)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("\nUser quit requested")
                break
        
        # Cleanup
        logger.info("-" * 70)
        stream.release()
        cv2.destroyAllWindows()
        
        logger.info(f"[OK] Video stream closed")
        logger.info(f"Total frames processed: {stream.get_frame_count()}")
        logger.info(f"Total detections: {detection_count}")
        logger.info(f"Average detections/frame: {detection_count/max(stream.get_frame_count(), 1):.2f}")
        
        logger.info("\n" + "="*70)
        logger.info("PHASE 3 COMPLETE: YOLO Detection Working")
        logger.info("="*70)
        logger.info("\nNext Phase: Plate Preprocessing & OCR Integration")
        logger.info("="*70 + "\n")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"[ERROR] {e}")
        return 1
    except ValueError as e:
        logger.error(f"[ERROR] {e}")
        return 1
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error: {e}", exc_info=True)
        return 1


def phase4_test_plate_preprocessor(source='webcam', debug=False, verbose=False):
    """
    Phase 4: Test plate preprocessing & enhancement.
    
    Tests extraction, perspective correction, and image enhancement
    on detected plate regions.
    
    Args:
        source (str): 'webcam' or path to video file
        debug (bool): Enable debug mode
        verbose (bool): Enable verbose logging
        
    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("\n" + "="*70)
        logger.info("PHASE 4: PLATE PREPROCESSING & ENHANCEMENT")
        logger.info("="*70)
        
        # Initialize detector
        logger.info("\nInitializing YOLO detector...")
        try:
            detector = YOLODetector()
            logger.info(f"[OK] Detector loaded")
        except FileNotFoundError as e:
            logger.error(f"[ERROR] {e}")
            return 1
        except ImportError as e:
            logger.error(f"[ERROR] Missing dependency: {e}")
            return 1
        
        # Initialize preprocessor
        logger.info("Initializing plate preprocessor...")
        try:
            preprocessor = PlatePreprocessor(
                target_size=(400, 150),
                apply_perspective_correction=True,
                apply_enhancement=True
            )
            logger.info(f"[OK] Preprocessor initialized: {preprocessor}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize preprocessor: {e}")
            return 1
        
        # Determine video source
        if source.lower() == 'webcam':
            video_source = Config.CAMERA_ID
            logger.info(f"Using webcam (ID: {video_source})")
        else:
            video_source = source
            logger.info(f"Using video file: {video_source}")
        
        # Open video stream
        logger.info("Opening video stream...")
        stream = VideoStream(source=video_source)
        logger.info(f"[OK] Video stream opened")
        
        # Processing loop
        logger.info("\nProcessing plates (press 'q' to quit)...")
        logger.info("-" * 70)
        
        frame_num = 0
        detection_count = 0
        preprocessing_success = 0
        preprocessing_fail = 0
        last_fps_time = time.time()
        
        while True:
            # Read frame
            success, frame = stream.read()
            
            if not success:
                logger.info(f"\nEnd of stream reached after {stream.get_frame_count()} frames")
                break
            
            frame_num += 1
            current_time = time.time()
            
            # Update FPS calculation
            stream.update_fps(current_time, last_fps_time)
            last_fps_time = current_time
            
            # Run detection
            detections = detector.detect(frame)
            detection_count += len(detections)
            
            # Process each detection
            processed_plates = []
            for det in detections:
                try:
                    # Extract and preprocess plate
                    plate_image = preprocessor.extract_and_preprocess(frame, det.bbox)
                    
                    if plate_image is not None:
                        processed_plates.append({
                            'bbox': det.bbox,
                            'confidence': det.confidence,
                            'plate_image': plate_image,
                            'size': plate_image.shape
                        })
                        preprocessing_success += 1
                    else:
                        preprocessing_fail += 1
                
                except Exception as e:
                    logger.debug(f"Failed to preprocess detection: {e}")
                    preprocessing_fail += 1
            
            # Log progress periodically
            if frame_num % 30 == 0:
                fps = stream.get_fps()
                
                log_msg = f"Frame {frame_num} | FPS: {fps:.1f} | Detections: {len(detections)}"
                
                if not stream.is_webcam_source() and stream.total_frames > 0:
                    progress = stream.get_progress()
                    log_msg += f" | Progress: {progress:.1f}%"
                
                log_msg += f" | Processed: {preprocessing_success}/{detection_count}"
                logger.info(log_msg)
                
                if processed_plates:
                    for i, plate_data in enumerate(processed_plates):
                        logger.info(f"  └─ Plate {i+1}: {plate_data['size']} @ {plate_data['confidence']:.1%}")
            
            # Add overlays to frame
            fps = stream.get_fps()
            frame = add_fps_overlay(frame, fps)
            frame = draw_detections(frame, detections)
            
            # Add processing stats overlay
            stats_text = f"Detected: {len(detections)} | Processed: {preprocessing_success}"
            cv2.putText(frame, stats_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow('Plate Preprocessing - Press Q to Quit', frame)
            
            # Wait for key press (1ms timeout)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("\nUser quit requested")
                break
        
        # Cleanup
        logger.info("-" * 70)
        stream.release()
        cv2.destroyAllWindows()
        
        logger.info(f"[OK] Video stream closed")
        logger.info(f"Total frames processed: {stream.get_frame_count()}")
        logger.info(f"Total detections: {detection_count}")
        logger.info(f"Successfully preprocessed: {preprocessing_success}")
        logger.info(f"Failed preprocessing: {preprocessing_fail}")
        
        if detection_count > 0:
            logger.info(f"Success rate: {preprocessing_success/detection_count*100:.1f}%")
        
        logger.info("\n" + "="*70)
        logger.info("PHASE 4 COMPLETE: Plate Preprocessing Working")
        logger.info("="*70)
        logger.info("\nNext Phase: OCR & Character Recognition")
        logger.info("="*70 + "\n")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"[ERROR] {e}")
        return 1
    except ValueError as e:
        logger.error(f"[ERROR] {e}")
        return 1
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error: {e}", exc_info=True)
        return 1



def main():
    """
    Main entry point for the application.
    Supports different phases and modes.
    """
    
    logger = setup_logging()
    
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Override config debug/verbose settings from args
        if args.debug:
            Config.DEBUG_MODE = True
        if args.verbose:
            Config.VERBOSE_LOGGING = True
        
        # Initialize configuration
        logger.info("="*70)
        logger.info("Real-Time License Plate Detection and Recognition System")
        logger.info("="*70)
        
        # Ensure all required directories exist
        Config.ensure_dirs_exist()
        logger.info("[OK] All required directories created/verified")
        
        # Validate configuration
        Config.validate()
        logger.info("[OK] Configuration validated")
        
        # Print configuration (useful for debugging)
        if Config.DEBUG_MODE or Config.VERBOSE_LOGGING:
            Config.print_config()
        
        logger.info("[OK] System initialized successfully")
        
        # Phase 4: Test plate preprocessing
        return phase4_test_plate_preprocessor(
            source=args.source,
            debug=args.debug,
            verbose=args.verbose
        )
        
    except Exception as e:
        logger.error(f"[FAILED] Error during initialization: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
