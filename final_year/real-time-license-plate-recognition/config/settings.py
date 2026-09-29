"""
Configuration settings for the Real-Time License Plate Recognition System.
All settings are loaded from environment variables (.env file).
No magic numbers should be scattered throughout the codebase.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Centralized configuration class.
    All environment variables and constants are defined here.
    """

    # ================================================
    # PROJECT DIRECTORIES
    # ================================================
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    MODELS_DIR = BASE_DIR / 'models'
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', './data/output'))
    PLATES_DIR = Path(os.getenv('PLATES_DIR', './data/plates'))
    DEBUG_DIR = Path(os.getenv('DEBUG_DIR', './data/debug'))
    INPUT_DIR = BASE_DIR / 'data' / 'input'

    # Create output directories if they don't exist
    @staticmethod
    def ensure_dirs_exist():
        """Create all required directories if they don't exist."""
        for directory in [
            Config.OUTPUT_DIR,
            Config.PLATES_DIR,
            Config.DEBUG_DIR,
            Config.INPUT_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    # ================================================
    # DATABASE CONFIGURATION
    # ================================================
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'license_plate_db')

    # ================================================
    # YOLO CONFIGURATION
    # ================================================
    YOLO_MODEL_PATH = os.getenv('YOLO_MODEL_PATH', './models/license_plate_detector.pt')
    YOLO_CONFIDENCE_THRESHOLD = float(os.getenv('YOLO_CONFIDENCE_THRESHOLD', 0.5))
    YOLO_IOU_THRESHOLD = float(os.getenv('YOLO_IOU_THRESHOLD', 0.4))
    YOLO_INPUT_SIZE = int(os.getenv('YOLO_INPUT_SIZE', 640))
    YOLO_GPU_ENABLED = os.getenv('YOLO_GPU_ENABLED', 'false').lower() == 'true'
    YOLO_DEVICE = 'cuda' if YOLO_GPU_ENABLED else 'cpu'

    # ================================================
    # OCR CONFIGURATION
    # ================================================
    OCR_ENGINE = os.getenv('OCR_ENGINE', 'easyocr')  # 'easyocr' or 'tesseract'
    OCR_LANGUAGE = os.getenv('OCR_LANGUAGE', 'en')
    OCR_CONFIDENCE_THRESHOLD = float(os.getenv('OCR_CONFIDENCE_THRESHOLD', 0.3))

    # ================================================
    # VIDEO/CAMERA CONFIGURATION
    # ================================================
    CAMERA_ID = int(os.getenv('CAMERA_ID', 0))
    VIDEO_INPUT_PATH = os.getenv('VIDEO_INPUT_PATH', './data/input')
    RESIZE_FRAME = os.getenv('RESIZE_FRAME', 'true').lower() == 'true'
    FRAME_WIDTH = int(os.getenv('FRAME_WIDTH', 1280))
    FRAME_HEIGHT = int(os.getenv('FRAME_HEIGHT', 720))
    TARGET_FPS = int(os.getenv('TARGET_FPS', 30))

    # ================================================
    # TRACKING CONFIGURATION (Temporal Stabilization)
    # ================================================
    TRACKING_MAX_AGE = int(os.getenv('TRACKING_MAX_AGE', 30))
    TRACKING_MIN_OBSERVATIONS = int(os.getenv('TRACKING_MIN_OBSERVATIONS', 3))
    TRACKING_CONFIDENCE_THRESHOLD = float(os.getenv('TRACKING_CONFIDENCE_THRESHOLD', 0.7))
    TRACKING_MAX_DISTANCE = float(os.getenv('TRACKING_MAX_DISTANCE', 100))

    # ================================================
    # OUTPUT CONFIGURATION
    # ================================================
    SAVE_PLATE_IMAGES = os.getenv('SAVE_PLATE_IMAGES', 'true').lower() == 'true'

    # ================================================
    # DEBUG CONFIGURATION
    # ================================================
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    DEBUG_SAVE_INTERMEDIATE = os.getenv('DEBUG_SAVE_INTERMEDIATE', 'false').lower() == 'true'
    VERBOSE_LOGGING = os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'

    # ================================================
    # APPLICATION METADATA
    # ================================================
    APPLICATION_NAME = os.getenv('APPLICATION_NAME', 'Real-Time License Plate Recognition')
    CAMERA_LOCATION = os.getenv('CAMERA_LOCATION', 'Main Gate')
    MAX_PLATES_PER_FRAME = int(os.getenv('MAX_PLATES_PER_FRAME', 5))

    # ================================================
    # VALIDATION CONFIGURATION (Indian Plates)
    # ================================================
    # Indian registration plate format: XX01AB1234
    # - First 2 chars: State code (letters)
    # - Next 2 digits: District code
    # - Next 2 letters: Series
    # - Next 4 digits: Registration number
    PLATE_MIN_LENGTH = 8
    PLATE_MAX_LENGTH = 12
    ALLOWED_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    # Character substitution rules (OCR correction)
    # These are contextual and should be used carefully
    CHARACTER_SUBSTITUTIONS = {
        '0': 'O',  # Zero to O (use cautiously)
        '1': 'I',  # One to I (use cautiously)
        '8': 'B',  # Eight to B (use cautiously)
        '5': 'S',  # Five to S (use cautiously)
    }

    # ================================================
    # PREPROCESSING CONFIGURATION
    # ================================================
    PREPROCESSING_RESIZE_WIDTH = 300
    PREPROCESSING_RESIZE_HEIGHT = 100
    PREPROCESSING_ENHANCE_CONTRAST = True
    PREPROCESSING_REDUCE_NOISE = True

    @classmethod
    def validate(cls):
        """
        Validate critical configuration values.
        Raises ValueError if critical settings are missing.
        """
        if not os.path.exists(cls.YOLO_MODEL_PATH):
            print(f"WARNING: YOLO model not found at {cls.YOLO_MODEL_PATH}")
            print("Download or train a license plate detection model and place it in the models/ directory")

    @classmethod
    def print_config(cls):
        """Print all configuration values (for debugging)."""
        print("\n" + "="*70)
        print("SYSTEM CONFIGURATION")
        print("="*70)
        print(f"Base Directory: {cls.BASE_DIR}")
        print(f"Debug Mode: {cls.DEBUG_MODE}")
        print(f"Database: {cls.DB_USER}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}")
        print(f"YOLO Model: {cls.YOLO_MODEL_PATH}")
        print(f"YOLO Device: {cls.YOLO_DEVICE}")
        print(f"YOLO Confidence: {cls.YOLO_CONFIDENCE_THRESHOLD}")
        print(f"OCR Engine: {cls.OCR_ENGINE}")
        print(f"Camera ID: {cls.CAMERA_ID}")
        print(f"Frame Size: {cls.FRAME_WIDTH}x{cls.FRAME_HEIGHT}")
        print(f"Target FPS: {cls.TARGET_FPS}")
        print(f"Output Directory: {cls.OUTPUT_DIR}")
        print(f"Plates Directory: {cls.PLATES_DIR}")
        print("="*70 + "\n")
