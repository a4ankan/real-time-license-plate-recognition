"""
Video stream handler for webcam and video file input.
Provides a unified interface for reading frames with FPS calculation.
"""

import cv2
import logging
from pathlib import Path
from config import Config


class VideoStream:
    """
    Unified interface for reading video frames from:
    - Webcam (by camera ID)
    - Video file (by file path)
    
    Features:
    - Real-time FPS calculation
    - Frame resizing based on configuration
    - Graceful error handling
    - Resource management
    """
    
    def __init__(self, source=None):
        """
        Initialize video stream.
        
        Args:
            source (int, str, or None): 
                - None or int: Webcam ID (default: Config.CAMERA_ID)
                - str: Path to video file
                
        Raises:
            ValueError: If source is invalid
            FileNotFoundError: If video file doesn't exist
        """
        self.logger = logging.getLogger(__name__)
        
        self.source = source if source is not None else Config.CAMERA_ID
        self.cap = None
        self.frame_count = 0
        self.fps_counter = 0
        self.current_fps = 0
        self.is_webcam = False
        self.total_frames = 0
        
        # Frame properties
        self.frame_width = Config.FRAME_WIDTH
        self.frame_height = Config.FRAME_HEIGHT
        self.resize_enabled = Config.RESIZE_FRAME
        
        self._open_stream()
    
    def _open_stream(self):
        """
        Open video stream (webcam or file).
        
        Raises:
            ValueError: If source is invalid or unopenable
            FileNotFoundError: If video file doesn't exist
        """
        try:
            # Handle string source (video file path)
            if isinstance(self.source, str):
                file_path = Path(self.source)
                
                if not file_path.exists():
                    raise FileNotFoundError(f"Video file not found: {self.source}")
                
                self.cap = cv2.VideoCapture(self.source)
                self.is_webcam = False
                
                # Get total frames for video file
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                self.logger.info(f"Opened video file: {self.source}")
                self.logger.info(f"Total frames: {self.total_frames}")
                
            # Handle int source (webcam by camera ID)
            elif isinstance(self.source, int):
                self.cap = cv2.VideoCapture(self.source)
                self.is_webcam = True
                self.total_frames = -1  # Unknown for webcam
                
                self.logger.info(f"Opened webcam (ID: {self.source})")
                
            else:
                raise ValueError(f"Invalid source type: {type(self.source)}")
            
            # Check if stream opened successfully
            if not self.cap.isOpened():
                raise ValueError(f"Failed to open video stream: {self.source}")
            
            # Get actual stream properties
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            self.logger.info(f"Stream resolution: {actual_width}x{actual_height}")
            if actual_fps > 0:
                self.logger.info(f"Stream FPS: {actual_fps:.1f}")
            
            if not self.is_opened():
                raise ValueError("Failed to open video stream")
                
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Invalid stream: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error opening stream: {e}")
            raise
    
    def read(self):
        """
        Read next frame from stream.
        
        Returns:
            tuple: (success: bool, frame: numpy.ndarray or None)
                - success: True if frame read successfully, False if end of stream
                - frame: Resized frame if success=True, None otherwise
                
        Updates:
            - Increments frame counter
            - Updates FPS calculation
        """
        if not self.is_opened():
            self.logger.warning("Stream not open")
            return False, None
        
        try:
            success, frame = self.cap.read()
            
            if not success:
                self.logger.debug("End of stream or read error")
                return False, None
            
            # Increment frame counter
            self.frame_count += 1
            self.fps_counter += 1
            
            # Resize frame if enabled
            if self.resize_enabled:
                frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            
            return True, frame
            
        except Exception as e:
            self.logger.error(f"Error reading frame: {e}")
            return False, None
    
    def update_fps(self, current_time, last_time):
        """
        Update FPS calculation based on elapsed time.
        
        Args:
            current_time (float): Current timestamp
            last_time (float): Last timestamp
            
        Updates FPS every 1 second of real time.
        """
        elapsed = current_time - last_time
        
        if elapsed >= 1.0:  # Update FPS every 1 second
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
    
    def get_fps(self):
        """
        Get current frames per second.
        
        Returns:
            float: Current FPS (updated approximately every second)
        """
        return self.current_fps
    
    def get_frame_count(self):
        """
        Get number of frames read so far.
        
        Returns:
            int: Frame count
        """
        return self.frame_count
    
    def get_position(self):
        """
        Get current position in video (for video files only).
        
        Returns:
            int: Current frame index (0 for webcam)
        """
        if self.is_webcam:
            return 0
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
    
    def get_progress(self):
        """
        Get progress percentage (for video files only).
        
        Returns:
            float: Progress as percentage (0.0 to 100.0), or 0 for webcam
        """
        if self.is_webcam or self.total_frames <= 0:
            return 0.0
        
        current = self.get_position()
        return (current / self.total_frames) * 100.0
    
    def is_opened(self):
        """
        Check if video stream is open.
        
        Returns:
            bool: True if stream is open, False otherwise
        """
        return self.cap is not None and self.cap.isOpened()
    
    def is_webcam_source(self):
        """
        Check if source is webcam.
        
        Returns:
            bool: True if webcam, False if video file
        """
        return self.is_webcam
    
    def release(self):
        """
        Release video stream and clean up resources.
        Should be called when done reading frames.
        """
        if self.cap is not None:
            self.cap.release()
            self.logger.info(f"Released stream (read {self.frame_count} frames)")
        
        self.cap = None
        self.frame_count = 0
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
    
    def __repr__(self):
        """String representation."""
        source_type = "webcam" if self.is_webcam else "video file"
        status = "open" if self.is_opened() else "closed"
        return f"VideoStream({self.source}, type={source_type}, status={status})"
