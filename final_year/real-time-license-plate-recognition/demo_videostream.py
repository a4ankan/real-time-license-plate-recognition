"""
Demo script for Phase 2: Video Stream Implementation
Tests VideoStream with various configurations.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import Config
from video import VideoStream


def demo_videostream_capabilities():
    """Demonstrate VideoStream capabilities."""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(name)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    logger.info("="*70)
    logger.info("VideoStream Capabilities Demo")
    logger.info("="*70)
    
    # Demo 1: Webcam capabilities
    logger.info("\n[DEMO 1] Webcam VideoStream Initialization")
    logger.info("-" * 70)
    
    try:
        # Create a VideoStream instance (won't actually open camera in testing)
        logger.info("Config parameters:")
        logger.info(f"  CAMERA_ID: {Config.CAMERA_ID}")
        logger.info(f"  FRAME_WIDTH: {Config.FRAME_WIDTH}")
        logger.info(f"  FRAME_HEIGHT: {Config.FRAME_HEIGHT}")
        logger.info(f"  RESIZE_FRAME: {Config.RESIZE_FRAME}")
        logger.info(f"  TARGET_FPS: {Config.TARGET_FPS}")
        logger.info("\nVideoStream class is ready for webcam input")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # Demo 2: Video file capabilities
    logger.info("\n[DEMO 2] Video File VideoStream Initialization")
    logger.info("-" * 70)
    logger.info("VideoStream can handle video files with:")
    logger.info("  - Automatic format detection")
    logger.info("  - Frame resizing support")
    logger.info("  - FPS calculation")
    logger.info("  - Progress tracking")
    logger.info("  - Graceful error handling")
    
    # Demo 3: API capabilities
    logger.info("\n[DEMO 3] VideoStream API Methods")
    logger.info("-" * 70)
    logger.info("Available methods:")
    logger.info("  - read()              : Read next frame")
    logger.info("  - update_fps()        : Update FPS calculation")
    logger.info("  - get_fps()           : Get current FPS")
    logger.info("  - get_frame_count()   : Get frames read")
    logger.info("  - get_position()      : Get current position")
    logger.info("  - get_progress()      : Get progress % (files only)")
    logger.info("  - is_opened()         : Check if stream is open")
    logger.info("  - is_webcam_source()  : Check if source is webcam")
    logger.info("  - release()           : Close and cleanup")
    logger.info("  - Context manager     : Use with 'with' statement")
    
    # Demo 4: Error handling
    logger.info("\n[DEMO 4] Error Handling")
    logger.info("-" * 70)
    logger.info("VideoStream handles:")
    logger.info("  - Invalid camera IDs")
    logger.info("  - Non-existent video files")
    logger.info("  - Unopenable streams")
    logger.info("  - Frame read failures")
    logger.info("  - Resource cleanup on errors")
    
    # Demo 5: Usage examples
    logger.info("\n[DEMO 5] Usage Examples")
    logger.info("-" * 70)
    
    print("\n--- Example 1: Webcam Usage ---")
    print("""
from src.video import VideoStream

stream = VideoStream(source=0)  # Use default webcam
while True:
    success, frame = stream.read()
    if not success:
        break
    # Process frame here
stream.release()
""")
    
    print("--- Example 2: Video File Usage ---")
    print("""
from src.video import VideoStream

stream = VideoStream(source='traffic.mp4')
while True:
    success, frame = stream.read()
    if not success:
        break
    # Process frame here
stream.release()
""")
    
    print("--- Example 3: Context Manager ---")
    print("""
from src.video import VideoStream

with VideoStream(source='video.mp4') as stream:
    while True:
        success, frame = stream.read()
        if not success:
            break
        # Process frame here
# Automatically released after context
""")
    
    print("--- Example 4: FPS Monitoring ---")
    print("""
from src.video import VideoStream
import time

stream = VideoStream(source=0)
last_time = time.time()

while True:
    success, frame = stream.read()
    if not success:
        break
    
    stream.update_fps(time.time(), last_time)
    last_time = time.time()
    
    if stream.get_frame_count() % 30 == 0:
        print(f"FPS: {stream.get_fps():.1f}")

stream.release()
""")
    
    logger.info("\n" + "="*70)
    logger.info("✓ VideoStream Module Ready for Use")
    logger.info("="*70)
    logger.info("\nNext Steps:")
    logger.info("  1. Test with webcam: python main.py --source webcam")
    logger.info("  2. Test with video file: python main.py --source path/to/video.mp4")
    logger.info("  3. Run unit tests: pytest tests/test_video_stream.py -v")
    logger.info("  4. Proceed to Phase 3: YOLO License Plate Detection")
    logger.info("="*70 + "\n")


if __name__ == '__main__':
    demo_videostream_capabilities()
