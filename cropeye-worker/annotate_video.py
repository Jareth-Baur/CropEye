import cv2
import os


def annotate_frames(frames_folder, detections, output_folder):

    os.makedirs(output_folder, exist_ok=True)

    grouped = {}

    for detection in detections:
        frame_name = detection["frame_name"]

        if frame_name not in grouped:
            grouped[frame_name] = []

        grouped[frame_name].append(detection)

    for frame_name in os.listdir(frames_folder):

        frame_path = os.path.join(frames_folder, frame_name)

        frame = cv2.imread(frame_path)

        frame_detections = grouped.get(frame_name, [])

        for det in frame_detections:
            #print(det)
            x = int(det["bbox_x"])
            y = int(det["bbox_y"])
            w = int(det["bbox_width"])
            h = int(det["bbox_height"])

            label = f'{det["disease_name"]} {det["confidence"]:.2f}'

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        output_path = os.path.join(output_folder, frame_name)

        cv2.imwrite(output_path, frame)