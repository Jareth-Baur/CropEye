import os
import cv2
import subprocess
from ultralytics import YOLO

model = YOLO("models/cropeye_yolov8s_maize_detection_v1.pt")


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


def process_frames(frames_folder, annotated_folder):

    os.makedirs(annotated_folder, exist_ok=True)

    detections = []

    frame_files = sorted(os.listdir(frames_folder))

    for index, frame_name in enumerate(frame_files):

        frame_path = os.path.join(frames_folder, frame_name)

        results = model(frame_path)

        for result in results:

            # SAVE YOLO-ANNOTATED FRAME
            annotated_frame = result.plot()

            output_path = os.path.join(
                annotated_folder,
                frame_name
            )

            cv2.imwrite(output_path, annotated_frame)

            if result.boxes is None:
                continue

            for box in result.boxes:

                confidence = float(box.conf[0])

                if confidence < 0.60:
                    continue

                cls = int(box.cls[0])

                x1, y1, x2, y2 = box.xyxy[0]

                timestamp_sec = round(index / 10, 2)
                
                detections.append({
                    "frame_name": frame_name,
                    "timestamp_sec": timestamp_sec,
                    "disease_name": model.names[cls],
                    "confidence": confidence,
                    "bbox_x": float(x1),
                    "bbox_y": float(y1),
                    "bbox_width": float(x2 - x1),
                    "bbox_height": float(y2 - y1)
                })

    print(f"Detections found: {len(detections)}")

    return detections