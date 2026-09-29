"""
Unit tests for VideoStream module.
Tests video reading, FPS calculation, and error handling.
"""

import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from video import VideoStream
from config import Config


logger = logging.getLogger(__name__)


class TestVideoStream:
    """Test cases for VideoStream class."""
    
    def test_videostream_webcam_initialization(self):
        """Test VideoStream initialization with webcam."""
        # Mock cv2.VideoCapture
        with patch('video.video_stream.cv2.VideoCapture') as mock_cap:
            mock_instance = MagicMock()
            mock_instance.isOpened.return_value = True
            mock_instance.get.return_value = 30.0
            mock_cap.return_value = mock_instance
            
            # Create VideoStream with webcam
            stream = VideoStream(source=0)
            
            # Verify initialization
            assert stream.source == 0
            assert stream.is_webcam is True
            assert stream.is_opened() is True
            assert stream.frame_count == 0
            
            # Cleanup
            stream.release()
    
    def test_videostream_file_initialization(self):
        """Test VideoStream initialization with video file."""
        # Create a temporary video file path
        test_video = Path(__file__).parent / 'test_video.mp4'
        
        with patch('video.video_stream.cv2.VideoCapture') as mock_cap:
            mock_instance = MagicMock()
            mock_instance.isOpened.return_value = True
            mock_instance.get.side_effect = lambda x: {
                5: 100,  # CV_CAP_PROP_FRAME_COUNT
                3: 640,  # CV_CAP_PROP_FRAME_WIDTH
                4: 480,  # CV_CAP_PROP_FRAME_HEIGHT
                6: 30.0  # CV_CAP_PROP_FPS
            }.get(x, 30.0)
            mock_cap.return_value = mock_instance
            
            with patch('video.video_stream.Path.exists', return_value=True):
                stream = VideoStream(source=str(test_video))
                
                # Verify initialization
                assert stream.is_webcam is False
                assert stream.is_opened() is True
                assert stream.total_frames == 100
                
                # Cleanup
                stream.release()
    
    def test_videostream_file_not_found(self):
        """Test VideoStream with non-existent file."""
        with pytest.raises(FileNotFoundError):
            stream = VideoStream(source='/nonexistent/video.mp4')
    
    def test_videostream_invalid_source_type(self):
        """Test VideoStream with invalid source type."""
        with pytest.raises(ValueError):
            stream = VideoStream(source=3.14)  # Float is invalid
    
    def test_videostream_read_success(self):
        """Test successful frame reading."""
        with patch('video.video_stream.cv2.VideoCapture') as mock_cap:
            mock_instance = MagicMock()
            mock_instance.isOpened.return_value = True
            mock_instance.read.return_value = (True, MagicMock())  # Mock frame
            mock_instance.get.return_value = 30.0
            mock_cap.return_value = mock_instance
            
            stream = VideoStream(source=0)
            
            success, frame = stream.read()
            
            assert success is True
            assert frame is not None
            assert stream.frame_count == 1
            
            stream.release()
    
    def test_videostream_read_failure(self):
        """Test frame reading at end of stream."""
        with patch('video.video_stream.cv2.VideoCapture') as mock_cap:
            mock_instance = MagicMock()
            mock_instance.isOpened.return_value = True
            mock_instance.read.return_value = (False, None)  # End of stream
            mock_instance.get.return_value = 30.0
            mock_cap.return_value = mock_instance
            
            stream = VideoStream(source=0)
            
            success, frame = stream.read()
            
            assert success is False
            assert frame is None
            
            stream.release()
    
    def test_videostream_fps_calculation(self):
        """Test FPS calculation."""
        with patch('video.video_stream.cv2.VideoCapture') as mock_cap:
            mock_instance = MagicMock()
            mock_instance.isOpened.return_value = True
            mock_instance.read.return_value = (True, MagicMock())
            mock_instance.get.return_value = 30.0
            mock_cap.return_value = mock_instance
            
            stream = VideoStream(source=0)
            
            # Simulate reading frames and FPS calculation
            for _ in range(30):
                stream.read()
            
            # Update FPS (simulate 1 second elapsed)
            stream.update_fps(1.0, 0.0)
            
            fps = stream.get_fps()
            assert fps > 0  # FPS should be positive
            
            stream.release()
    
    def test_videostream_frame_resize(self):
        """Test frame resizing functionality."""
        with patch('video.video_stream.cv2.VideoCapture') as mock_cap:
            with patch('video.video_stream.cv2.resize') as mock_resize:
                mock_instance = MagicMock()
                mock_instance.isOpened.return_value = True
                mock_frame = MagicMock()
                mock_instance.read.return_value = (True, mock_frame)
                mock_instance.get.return_value = 30.0
                mock_cap.return_value = mock_instance
                
                # Create stream with resize enabled
                with patch.object(Config, 'RESIZE_FRAME', True):
                    stream = VideoStream(source=0)
                    mock_resize.return_value = mock_frame
                    
                    success, frame = stream.read()
                    
                    # Verify resize was called
                    mock_resize.assert_called_once()
                    
                    stream.release()
    
    def test_videostream_context_manager(self):
        """Test VideoStream as context manager."""
        with patch('video.video_stream.cv2.VideoCapture') as mock_cap:
            mock_instance = MagicMock()
            mock_instance.isOpened.return_value = True
            mock_instance.get.return_value = 30.0
            mock_cap.return_value = mock_instance
            
            with VideoStream(source=0) as stream:
                assert stream.is_opened() is True
            
            # After exiting context, stream should be released
            mock_instance.release.assert_called()
    
    def test_videostream_get_progress(self):
        """Test progress calculation."""
        with patch('video.video_stream.cv2.VideoCapture') as mock_cap:
            mock_instance = MagicMock()
            mock_instance.isOpened.return_value = True
            mock_instance.get.side_effect = lambda x: {
                5: 100,  # CV_CAP_PROP_FRAME_COUNT
                1: 50,   # CV_CAP_PROP_POS_FRAMES
                3: 640,
                4: 480,
                6: 30.0
            }.get(x, 30.0)
            mock_cap.return_value = mock_instance
            
            with patch('video.video_stream.Path.exists', return_value=True):
                stream = VideoStream(source='/test/video.mp4')
                progress = stream.get_progress()
                
                # Progress should be 50% (50/100)
                assert 49.0 <= progress <= 51.0
                
                stream.release()


class TestVideoStreamIntegration:
    """Integration tests for VideoStream."""
    
    def test_videostream_full_cycle(self):
        """Test full initialization -> read -> release cycle."""
        with patch('video.video_stream.cv2.VideoCapture') as mock_cap:
            mock_instance = MagicMock()
            mock_instance.isOpened.return_value = True
            mock_instance.read.side_effect = [
                (True, MagicMock()),  # Frame 1
                (True, MagicMock()),  # Frame 2
                (False, None)         # End of stream
            ]
            mock_instance.get.return_value = 30.0
            mock_cap.return_value = mock_instance
            
            # Create stream
            stream = VideoStream(source=0)
            assert stream.is_opened() is True
            
            # Read frames
            success1, _ = stream.read()
            assert success1 is True
            
            success2, _ = stream.read()
            assert success2 is True
            
            success3, _ = stream.read()
            assert success3 is False
            
            # Release
            stream.release()
            assert stream.cap is None


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
