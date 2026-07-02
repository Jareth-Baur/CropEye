from ultralytics import YOLO
import cv2
import os

# =====================================================
# CONFIG
# =====================================================

MODEL_PATH = "models/cropeye_yolov8s_maize_detection_v4.pt"
IMAGE_PATH = "test.jpg"

# =====================================================
# LOAD MODEL
# =====================================================

model = YOLO(MODEL_PATH)

print("=" * 60)
print("MODEL CLASSES")
print("=" * 60)
print(model.names)

# =====================================================
# PREDICT
# =====================================================

results = model.predict(
    source=IMAGE_PATH,
    imgsz=640,
    conf=0.01,      # VERY LOW FOR DEBUGGING
    save=True,
    save_txt=True,
    save_conf=True,
    verbose=True
)

result = results[0]

print("\n" + "=" * 60)
print("DETECTION SUMMARY")
print("=" * 60)

if len(result.boxes) == 0:
    print("NO DETECTIONS FOUND")
    exit()

print(f"Total detections: {len(result.boxes)}")

# =====================================================
# PRINT ALL DETECTIONS
# =====================================================

confidences = []

for i, box in enumerate(result.boxes):

    class_id = int(box.cls[0])
    confidence = float(box.conf[0])

    confidences.append(confidence)

    label = model.names[class_id]

    x1, y1, x2, y2 = box.xyxy[0].tolist()

    print("\n--------------------------")
    print(f"Detection #{i+1}")
    print("--------------------------")
    print("Class:", label)
    print("Confidence:", round(confidence, 4))
    print(
        f"Box: "
        f"x1={x1:.1f}, "
        f"y1={y1:.1f}, "
        f"x2={x2:.1f}, "
        f"y2={y2:.1f}"
    )

# =====================================================
# CONFIDENCE ANALYSIS
# =====================================================

print("\n" + "=" * 60)
print("CONFIDENCE ANALYSIS")
print("=" * 60)

print("Highest confidence :", max(confidences))
print("Lowest confidence  :", min(confidences))
print("Average confidence :", sum(confidences) / len(confidences))

print(
    "Detections > 0.50 :",
    sum(c > 0.50 for c in confidences)
)

print(
    "Detections > 0.30 :",
    sum(c > 0.30 for c in confidences)
)

print(
    "Detections > 0.10 :",
    sum(c > 0.10 for c in confidences)
)

# =====================================================
# IMAGE SIZE
# =====================================================

img = cv2.imread(IMAGE_PATH)

if img is not None:
    h, w = img.shape[:2]

    print("\nImage size:")
    print(f"{w}x{h}")

print("\nPrediction image saved to:")
print("runs/detect/predict/")