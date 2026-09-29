# Real-Time License Plate Detection and Recognition System

A production-grade, modular system for detecting and recognizing vehicle license plates in real-time from live webcam feeds or pre-recorded videos using YOLO object detection and OCR.

## Project Overview

This system demonstrates a complete computer vision and deep learning pipeline suitable for a B.Tech Computer Science placement portfolio. It combines:

- **YOLO Object Detection** for license plate localization
- **OCR (Optical Character Recognition)** for text extraction
- **Image Preprocessing** for enhanced recognition accuracy
- **Temporal Stabilization** for noise reduction across video frames
- **MySQL Database** for storing confirmed detections
- **Modular Architecture** for maintainability and extensibility

## Problem Statement

Automatic license plate recognition (ALPR) is essential for:
- Traffic management systems
- Parking lot entry/exit monitoring
- Vehicle toll collection
- Law enforcement
- Parking enforcement

Traditional rule-based methods struggle with:
- Varying lighting conditions
- Different plate formats
- Occlusion and perspective angles
- Real-time performance requirements

This system uses YOLO deep learning for robust detection and stabilizes predictions across multiple frames to achieve production-grade accuracy.

## Features

- ✅ Real-time license plate detection from webcam
- ✅ Video file processing with progress tracking
- ✅ YOLO-based plate localization (GPU/CPU)
- ✅ OCR with character recognition and confidence scoring
- ✅ Temporal frame-to-frame stabilization using majority voting
- ✅ MySQL database storage with duplicate prevention
- ✅ Plate image extraction and storage
- ✅ Debug mode with intermediate image saving
- ✅ Configurable validation rules (Indian format support)
- ✅ FPS measurement and performance monitoring
- ✅ Graceful error handling
- ✅ Modular, testable architecture

## Architecture

### High-Level Pipeline

```
Video/Webcam Input
       ↓
   Video Stream Handler
       ↓
   YOLO License Plate Detector
       ↓
   Plate Image Preprocessing
       ↓
   OCR Engine
       ↓
   Text Normalization & Validation
       ↓
   Multi-frame Tracking & Stabilization
       ↓
   Confirmed License Plate
       ↓
   MySQL Database Storage
       ↓
   Visualization & Display
```

### Module Responsibilities

1. **VideoStream** (`src/video/video_stream.py`)
   - Handles webcam and video file input
   - Manages frame reading and FPS calculation
   - Provides clean frame interface

2. **YOLODetector** (`src/detection/yolo_detector.py`)
   - YOLO model loading and inference
   - Bounding box extraction
   - Configurable confidence and IoU thresholds
   - GPU/CPU selection

3. **PlatePreprocessor** (`src/preprocessing/plate_preprocessor.py`)
   - Plate image cropping and normalization
   - Perspective correction (optional)
   - Contrast and noise enhancement
   - OCR-ready image generation

4. **OCREngine** (`src/recognition/ocr_engine.py`)
   - EasyOCR/Tesseract integration
   - Character recognition with confidence
   - Text normalization

5. **PlateValidator** (`src/validation/plate_validator.py`)
   - Format validation
   - Contextual character correction
   - Length and character set validation
   - Regex pattern matching

6. **PlateTracker** (`src/tracking/plate_tracker.py`)
   - Multi-frame observation aggregation
   - Confidence-weighted voting
   - Duplicate detection prevention
   - Temporal stabilization

7. **Database Layer** (`src/database/`)
   - `db_connection.py`: MySQL connection management
   - `plate_repository.py`: CRUD operations
   - Duplicate detection
   - Query interface

8. **CharacterSegmenter** (`src/segmentation/character_segmenter.py`)
   - Optional classical CV-based character extraction
   - Contour detection and filtering
   - Connected component analysis

9. **Visualization** (`src/visualization/display.py`)
   - Real-time display of detections
   - Bounding boxes and confidence
   - FPS overlay
   - Tracking ID display

## Technology Stack

### Core Libraries
- **Python 3.8+** – Language
- **OpenCV** – Image processing
- **NumPy** – Numerical operations
- **YOLO (Ultralytics)** – Object detection
- **EasyOCR** – Optical character recognition

### Database
- **MySQL** – Storage
- **mysql-connector-python** – Database interface

### Utilities
- **python-dotenv** – Environment configuration
- **PyYAML** – Configuration files
- **pytest** – Testing framework

## Project Structure

```
real-time-license-plate-recognition/
│
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── .env                             # Environment config (DO NOT COMMIT)
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
│
├── config/                          # Configuration module
│   ├── __init__.py
│   └── settings.py                 # Centralized settings (NO magic numbers)
│
├── models/                          # YOLO model storage
│   ├── license_plate_detector.pt   # Trained YOLO model (download required)
│   └── README.md                   # Model setup instructions
│
├── src/                             # Source code package
│   ├── __init__.py
│   │
│   ├── video/                       # Video stream handling
│   │   ├── __init__.py
│   │   └── video_stream.py         # WebCam and video file reader
│   │
│   ├── detection/                   # YOLO detection
│   │   ├── __init__.py
│   │   └── yolo_detector.py        # YOLO model wrapper
│   │
│   ├── preprocessing/               # Plate preprocessing
│   │   ├── __init__.py
│   │   └── plate_preprocessor.py   # Image enhancement for OCR
│   │
│   ├── recognition/                 # OCR engine
│   │   ├── __init__.py
│   │   └── ocr_engine.py           # Character recognition
│   │
│   ├── segmentation/                # Character segmentation (optional)
│   │   ├── __init__.py
│   │   └── character_segmenter.py  # Classical CV-based segmentation
│   │
│   ├── validation/                  # Plate validation
│   │   ├── __init__.py
│   │   └── plate_validator.py      # Format & regex validation
│   │
│   ├── tracking/                    # Temporal stabilization
│   │   ├── __init__.py
│   │   └── plate_tracker.py        # Multi-frame aggregation
│   │
│   ├── database/                    # Database operations
│   │   ├── __init__.py
│   │   ├── db_connection.py        # MySQL connection
│   │   └── plate_repository.py     # Data access layer
│   │
│   ├── visualization/               # Display & rendering
│   │   ├── __init__.py
│   │   └── display.py              # Real-time visualization
│   │
│   └── utils/                       # Utility functions
│       ├── __init__.py
│       └── helpers.py              # Generic helpers
│
├── data/                            # Data storage
│   ├── input/                       # Input videos/images
│   ├── output/                      # Output visualizations
│   ├── plates/                      # Extracted plate images
│   └── debug/                       # Debug intermediate images
│
├── tests/                           # Unit tests
│   ├── test_detector.py
│   ├── test_ocr.py
│   ├── test_validator.py
│   └── test_tracker.py
│
└── notebooks/                       # Jupyter notebooks for experimentation
    └── experiments.ipynb
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- MySQL Server (5.7+)
- Webcam or video file (for input)
- GPU (NVIDIA CUDA) - optional but recommended for real-time performance

### Step 1: Clone/Setup Project

```bash
cd d:\final_year
git clone <repository_url>
cd real-time-license-plate-recognition
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment Configuration

```bash
# Copy template to actual .env file
cp .env.example .env

# Edit .env with your settings
# Important: Set database credentials and model path
```

Edit `.env` and configure:
- `DB_HOST`, `DB_USER`, `DB_PASSWORD` for MySQL
- `YOLO_MODEL_PATH` to point to your trained model
- Other parameters as needed

### Step 5: Verify Installation

```bash
# Run Phase 1 verification
python main.py
```

Expected output:
```
======================================================================
Real-Time License Plate Detection and Recognition System
======================================================================
✓ All required directories created/verified
✓ Configuration validated
✓ System initialized successfully

Phase 1 Complete: Project Setup & Scaffolding
...
```

### Step 6: Setup MySQL Database

```sql
-- Create database
CREATE DATABASE license_plate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Switch to database
USE license_plate_db;

-- Create table
CREATE TABLE plate_detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plate_number VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    camera_id INT DEFAULT 0,
    image_path VARCHAR(255),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_plate (plate_number),
    INDEX idx_timestamp (detected_at)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 7: Download YOLO Model

Place a trained license plate detection YOLO model at:
```
models/license_plate_detector.pt
```

If you don't have a model:
- Train one on a license plate dataset (e.g., from Roboflow)
- Or download a pre-trained model and place it in `models/`

See [models/README.md](models/README.md) for detailed instructions.

## Environment Configuration

Key `.env` variables:

### Database
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=license_plate_db
```

### YOLO
```
YOLO_MODEL_PATH=./models/license_plate_detector.pt
YOLO_CONFIDENCE_THRESHOLD=0.5        # Min confidence for detection
YOLO_IOU_THRESHOLD=0.4               # IoU for NMS
YOLO_GPU_ENABLED=true                # Use GPU if available
```

### Video
```
CAMERA_ID=0                          # Webcam index
FRAME_WIDTH=1280
FRAME_HEIGHT=720
RESIZE_FRAME=true
```

### OCR
```
OCR_ENGINE=easyocr                   # easyocr or tesseract
OCR_LANGUAGE=en
OCR_CONFIDENCE_THRESHOLD=0.3
```

### Tracking
```
TRACKING_MIN_OBSERVATIONS=3          # Frames to confirm plate
TRACKING_MAX_AGE=30                  # Frames before forgetting
TRACKING_CONFIDENCE_THRESHOLD=0.7
```

### Debug
```
DEBUG_MODE=false                     # Enable debug output
DEBUG_SAVE_INTERMEDIATE=false        # Save preprocessing steps
VERBOSE_LOGGING=false
```

## Usage

### Running with Webcam

```bash
python main.py --source webcam
```

Press `q` to quit.

### Running with Video File

```bash
python main.py --source path/to/video.mp4
```

### Running with Debug Mode

```bash
# Enable all debug outputs and intermediate image saving
DEBUG_MODE=true python main.py --source webcam
```

Debug images saved to `data/debug/`

## Expected Output Example

```
Frame 142 | FPS: 28.5
Plate Detected: WB12AB1234
├─ Detection Confidence: 94%
├─ OCR Confidence: 96%
├─ Track ID: 7
└─ Status: CONFIRMED (Saved to DB)

Image: data/plates/plate_20240115_145632_a7f9e2k1.jpg
```

## Limitations

1. **YOLO Model Quality** – Recognition accuracy heavily depends on the trained model
2. **OCR Limitations** – Poor image quality may cause recognition errors
3. **Lighting Conditions** – Extreme lighting can degrade performance
4. **Plate Format** – Currently tuned for Indian registration format
5. **Real-Time Performance** – Depends on GPU availability and frame resolution
6. **Frame Rate** – Limited by YOLO inference time and available hardware
7. **Perspective Angles** – Highly skewed angles may not be recognized
8. **Partially Obscured Plates** – Dirt, occlusion, or damage reduces accuracy

## Future Improvements

1. **Multi-Camera Support** – Track vehicles across multiple cameras
2. **Vehicle Detection** – Detect vehicle class along with plates
3. **Entry/Exit Detection** – Identify direction of vehicle movement
4. **Web Dashboard** – Real-time visualization dashboard
5. **REST API** – Query plates and statistics via HTTP
6. **License Plate Database** – Searchable historical records
7. **Statistics & Analytics** – Daily/weekly/monthly reports
8. **Cloud Deployment** – Deploy on AWS/Azure/GCP
9. **Mobile App** – Mobile interface for police/traffic officers
10. **Parking Management** – Integration with parking systems

## Testing

Run unit tests:

```bash
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

Test coverage targets:
- `test_detector.py` – YOLO detector output validation
- `test_ocr.py` – OCR normalization and confidence
- `test_validator.py` – Plate format validation
- `test_tracker.py` – Multi-frame tracking logic

## Performance Benchmarks

Typical performance on NVIDIA GPU:
- **YOLO Inference** – 5-15 ms per frame
- **OCR** – 20-50 ms per plate
- **Total Pipeline** – 30-100 ms per frame
- **Target FPS** – 10-30 FPS depending on hardware

## Troubleshooting

### YOLO Model Not Found
**Error:** `FileNotFoundError: models/license_plate_detector.pt`

**Solution:** Download or train a YOLO model and place in `models/` directory

### No Detections
1. Check YOLO confidence threshold (try lowering from 0.5 to 0.3)
2. Verify model is appropriate for license plate detection
3. Check image quality and lighting
4. Enable DEBUG_MODE to inspect YOLO outputs

### OCR Accuracy Low
1. Verify preprocessing: check `data/debug/preprocessed_*.jpg`
2. Adjust contrast enhancement settings
3. Try different OCR engine (easyocr vs tesseract)
4. Increase OCR confidence threshold

### Database Connection Error
1. Verify MySQL is running: `mysql -u root -p`
2. Check `.env` credentials
3. Create database if not exists: `CREATE DATABASE license_plate_db;`

### Low FPS
1. Reduce frame resolution (`FRAME_WIDTH`, `FRAME_HEIGHT`)
2. Increase YOLO confidence threshold (skip low-confidence detections)
3. Enable GPU: `YOLO_GPU_ENABLED=true`
4. Reduce target FPS in settings

## Contributing

This project is designed for educational purposes and serves as a portfolio piece.

## License

[Your License Here]

## Contact

[ankan/ankanp227@gmail.com]

## References

- [Ultralytics YOLO Documentation](https://docs.ultralytics.com/)
- [EasyOCR GitHub](https://github.com/JaidedAI/EasyOCR)
- [OpenCV Documentation](https://docs.opencv.org/)
- [MySQL Python Connector](https://dev.mysql.com/doc/connector-python/en/)

---

**Last Updated:** January 2024  
**Version:** 1.0.0
