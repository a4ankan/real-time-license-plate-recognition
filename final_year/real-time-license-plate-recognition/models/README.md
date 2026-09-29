# YOLO Model Setup

This directory contains the trained YOLO model for license plate detection.

## Model Requirements

The system requires a YOLO object detection model trained on license plate detection task.

### Expected Model File

```
models/license_plate_detector.pt
```

## Getting the Model

### Option 1: Train Your Own Model

Use Ultralytics YOLOv8 with a license plate dataset:

```bash
from ultralytics import YOLO

# Load a pretrained model
model = YOLO('yolov8m.pt')

# Train on your license plate dataset
results = model.train(
    data='path/to/dataset.yaml',
    epochs=100,
    imgsz=640,
    device=0  # GPU device ID
)

# Save the best model
model.save('license_plate_detector.pt')
```

### Option 2: Download Pre-trained Model

Download a pre-trained license plate detection model from:
- [Roboflow](https://roboflow.com) – Download YOLOv8 format
- [Ultralytics Models Hub](https://hub.ultralytics.com/)

### Option 3: Custom Training Script

Create a training script:

```bash
yolo detect train data=license_plates.yaml model=yolov8m.pt epochs=100 imgsz=640
```

## Dataset Format

If training your own model, use COCO or YOLOv8 format:

```
dataset/
├── images/
│   ├── train/
│   │   ├── img1.jpg
│   │   ├── img2.jpg
│   │   └── ...
│   ├── val/
│   └── test/
├── labels/
│   ├── train/
│   │   ├── img1.txt
│   │   ├── img2.txt
│   │   └── ...
│   ├── val/
│   └── test/
└── data.yaml
```

### data.yaml Example

```yaml
path: /path/to/dataset
train: images/train
val: images/val
test: images/test

nc: 1  # number of classes
names: ['license_plate']  # class names
```

### Label Format (YOLO txt)

Each image has a corresponding `.txt` file with normalized coordinates:

```
<class_id> <x_center> <y_center> <width> <height>
```

Example:
```
0 0.5 0.5 0.3 0.2
```

## Model Configuration

Update `.env` with your model path:

```
YOLO_MODEL_PATH=./models/license_plate_detector.pt
YOLO_CONFIDENCE_THRESHOLD=0.5
YOLO_IOU_THRESHOLD=0.4
YOLO_INPUT_SIZE=640
```

## Performance Tuning

### Inference Speed

- **Larger models** (yolov8l, yolov8x) – More accurate but slower
- **Smaller models** (yolov8n, yolov8s) – Faster but less accurate
- **Recommended:** yolov8m (medium) for balanced performance

### Quality vs Speed

```
yolov8n.pt  ← Fastest
yolov8s.pt
yolov8m.pt  ← Recommended
yolov8l.pt
yolov8x.pt  ← Most accurate
```

## Testing the Model

```python
from ultralytics import YOLO
from config import Config

model = YOLO(Config.YOLO_MODEL_PATH)

# Test on image
results = model.predict('test_image.jpg', conf=Config.YOLO_CONFIDENCE_THRESHOLD)

# Display results
for result in results:
    print(result.boxes)
```

## Common Issues

### Model File Not Found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'models/license_plate_detector.pt'`

**Solution:**
1. Download or train a model
2. Place it exactly at `models/license_plate_detector.pt`
3. Verify path in `.env` file

### Low Accuracy

1. **Verify dataset** – Is your training data representative?
2. **Check augmentation** – Enable data augmentation during training
3. **Increase epochs** – Train for more iterations
4. **Adjust thresholds** – Lower `YOLO_CONFIDENCE_THRESHOLD` in `.env`

### Slow Inference

1. **Use GPU** – Set `YOLO_GPU_ENABLED=true`
2. **Smaller model** – Use yolov8n or yolov8s instead of yolov8x
3. **Smaller input size** – Reduce `YOLO_INPUT_SIZE` (trade-off with accuracy)
4. **Frame resizing** – Set `RESIZE_FRAME=true` in `.env`

## Resources

- [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com/)
- [Roboflow Datasets](https://roboflow.com/datasets)
- [YOLOv8 Training Guide](https://docs.ultralytics.com/modes/train/)
- [License Plate Detection Datasets](https://www.kaggle.com/datasets?search=license+plate)
