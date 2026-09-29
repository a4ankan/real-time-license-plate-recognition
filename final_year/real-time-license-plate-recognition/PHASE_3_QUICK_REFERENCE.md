# Phase 3: YOLO Detection - Quick Reference

## Installation (REQUIRED BEFORE TESTING)

```bash
# Install ultralytics (required dependency)
pip install ultralytics

# Verify installation
python -c "from ultralytics import YOLO; print('OK')"
```

## Get Model (REQUIRED BEFORE TESTING)

### Option 1: Download Pre-trained (Recommended)
```bash
# YOLOv8 will auto-download on first use
python -c "from ultralytics import YOLO; model = YOLO('yolov8s.pt')"
# Place in ./models/license_plate_detector.pt
```

### Option 2: Train Custom Model
```bash
# Requires license plate dataset (e.g., from Roboflow)
# Follow ultralytics documentation
```

### Option 3: Transfer Learning
```bash
# Fine-tune YOLOv8 on your plate data
python -m ultralytics.yolo detect train data=license_plates.yaml model=yolov8s.pt epochs=50
```

## Quick API

```python
from src.detection import YOLODetector

# Initialize
detector = YOLODetector()  # Loads from Config.YOLO_MODEL_PATH

# Detect plates
detections = detector.detect(frame)  # List[Detection]

# Access detection properties
for det in detections:
    print(det.bbox)           # (x1, y1, x2, y2)
    print(det.confidence)     # 0.0-1.0
    print(det.width)          # Plate width
    print(det.height)         # Plate height
    print(det.center)         # (cx, cy)
```

## Testing Commands

```bash
# Test with webcam (requires camera)
python main.py --source webcam

# Test with video file
python main.py --source path/to/video.mp4

# Test with debug output
python main.py --source webcam --debug --verbose

# Run unit tests
pytest tests/test_yolo_detector.py -v

# Check test coverage
pytest tests/test_yolo_detector.py --cov=src/detection
```

## Expected Output

**First Run (with webcam):**
```
======================================================================
PHASE 3: YOLO LICENSE PLATE DETECTION
======================================================================

Initializing YOLO detector...
[OK] Detector loaded: YOLODetector(...)

Opening video stream...
[OK] Video stream opened

Detecting license plates (press 'q' to quit)...
------------------------------------------------------
Frame 30 | FPS: 28.5 | Detections: 2
Frame 60 | FPS: 29.1 | Detections: 1
...

Total frames processed: 300
Total detections: 45
Average detections/frame: 0.15
======================================================================
PHASE 3 COMPLETE
```

## Common Errors & Solutions

### ❌ FileNotFoundError: YOLO model not found
**Solution:** Place model at `./models/license_plate_detector.pt`

### ❌ ImportError: No module named 'ultralytics'
**Solution:** `pip install ultralytics`

### ❌ No camera detected
**Solution:** Check camera ID in .env or try `--source 1`, `--source 2`, etc.

### ❌ Very slow inference (< 5 FPS)
**Solution:** 
- Use smaller model (n or s)
- Disable real-time display
- Enable GPU if available
- Reduce frame resolution

## Configuration

**.env settings:**
```env
YOLO_MODEL_PATH=./models/license_plate_detector.pt
YOLO_CONFIDENCE_THRESHOLD=0.5
YOLO_IOU_THRESHOLD=0.4
YOLO_INPUT_SIZE=640
YOLO_GPU_ENABLED=false
CAMERA_ID=0
```

## Files in Phase 3

- `src/detection/yolo_detector.py` - Detection engine (380 lines)
- `tests/test_yolo_detector.py` - Unit tests (16 cases)
- `main.py` - phase3_test_yolo_detector() function
- `PHASE_3_COMPLETE.md` - Full documentation

## Performance Tips

| Aspect | Tip |
|--------|-----|
| Speed | Use GPU, smaller model, batch processing |
| Accuracy | Increase confidence threshold, better trained model |
| Memory | Reduce input size, process fewer frames |
| Real-time | Disable visualization, skip frames |

## Next: Phase 4

Phase 4 implements plate preprocessing:
- Extract plate regions
- Perspective correction
- Image enhancement
- Prepare for OCR

Status: Ready to proceed after Phase 3 approval ✅
