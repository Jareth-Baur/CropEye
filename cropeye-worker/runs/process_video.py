import os
import cv2
import subprocess
from ultralytics import YOLO

# MODELS
detection_model = YOLO("models/cropeye_yolov8s_maize_detection_v3.pt")

classification_model = YOLO("models/maizeleaf_classification_yoloV8s_v2.pt")

names = detection_model.names.copy()

# Add Unknown as the next class index
names[len(names)] = "Unknown"

def extract_frames(video_path, output_folder):

    os.makedirs(output_folder, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", "fps=10,scale=1280:720",
        f"{output_folder}/frame_%04d.png"
    ]

    result = subprocess.run(command)

    if result.returncode != 0:
        raise Exception("FFmpeg frame extraction failed")

    print("Frames extracted successfully")

print(names)

print(classification_model.names)

def process_frames(frames_folder):

    detections = []
    
    last_detection_times = {}

    frame_files = sorted(os.listdir(frames_folder))

    for index, frame_name in enumerate(frame_files):
        # PROCESS ONLY EVERY 10TH FRAME
        if index % 10 != 0:
            continue

        frame_path = os.path.join(frames_folder, frame_name)

        frame = cv2.imread(frame_path)

        detection_results = detection_model(frame)

        for result in detection_results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                detection_confidence = float(box.conf[0])

                # DETECTION CONFIDENCE FILTER
                #if detection_confidence < 0.10:
                 #   continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # CROP DETECTED REGION
                crop = frame[y1:y2, x1:x2]

                if crop.size == 0:
                    continue

                # CLASSIFICATION
                classification_results = classification_model(crop)

                for cls_result in classification_results:

                    probs = cls_result.probs

                    if probs is None:
                        continue

                    class_id = int(probs.top1)

                    class_confidence = float(probs.top1conf)

                    # CLASSIFICATION CONFIDENCE FILTER
                    #if class_confidence < 0.01:
                    #    continue

                    timestamp_sec = round(index / 10, 2)
                    
                    disease_name = classification_model.names[class_id]
                    
                    # SKIP DUPLICATE DISEASES WITHIN 2 SECONDS
                    if disease_name in last_detection_times:

                        if timestamp_sec - last_detection_times[disease_name] < 2:
                            continue

                    last_detection_times[disease_name] = timestamp_sec

                    detections.append({
                        "frame_name": frame_name,
                        "timestamp_sec": timestamp_sec,
                        "disease_name": disease_name,
                        "confidence": class_confidence,
                        "bbox_x": float(x1),
                        "bbox_y": float(y1),
                        "bbox_width": float(x2 - x1),
                        "bbox_height": float(y2 - y1)
                    })

    print(f"Detections found: {len(detections)}")

    return detections