import os
import time
import requests
import subprocess
import shutil

from dotenv import load_dotenv
from httpx import Client, HTTPTransport
from supabase import ClientOptions, create_client

from process_video import extract_frames, process_frames
from annotate_video import annotate_frames

from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None


def create_supabase_client():
    # Disable HTTP/2 to avoid idle ConnectionTerminated errors during polling.
    transport = HTTPTransport(retries=3, http2=False)
    http_client = Client(transport=transport, timeout=120)
    options = ClientOptions(httpx_client=http_client)

    return create_client(SUPABASE_URL, SUPABASE_KEY, options=options)


def reset_supabase_client():
    global supabase

    supabase = create_supabase_client()


def is_connection_error(error):
    error_text = str(error)

    return any(
        marker in error_text
        for marker in (
            "ConnectionTerminated",
            "RemoteProtocolError",
            "Server disconnected",
            "Connection reset",
        )
    )


def execute_with_retry(operation, retries=3):
    global supabase

    last_error = None

    for attempt in range(retries):
        try:
            return operation()
        except Exception as error:
            last_error = error

            if is_connection_error(error) and attempt < retries - 1:
                print(
                    f"Supabase connection lost, reconnecting "
                    f"({attempt + 1}/{retries})..."
                )
                reset_supabase_client()
                time.sleep(2**attempt)
                continue

            raise

    raise last_error


reset_supabase_client()

TEMP_VIDEO = "temp/input.mp4"

FRAMES_FOLDER = "frames"

ANNOTATED_FOLDER = "annotated_frames"

OUTPUT_VIDEO = "outputs/output.mp4"


def generate_flight_name():

    now = datetime.now()

    return f"Maize Flight {now.strftime('%Y-%m-%d %H:%M')}"


def clear_folder(folder_path):

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    os.makedirs(folder_path, exist_ok=True)
    
def cleanup_temp_files():

    folders = [
        FRAMES_FOLDER,
        ANNOTATED_FOLDER,
        "outputs"
    ]

    for folder in folders:

        if os.path.exists(folder):
            shutil.rmtree(folder)

    if os.path.exists(TEMP_VIDEO):
        os.remove(TEMP_VIDEO)

    print("Temporary files cleaned")
def upload_detection_frame(frame_path, flight_id, frame_name):

    file_name = f"{flight_id}/{frame_name}"

    with open(frame_path, "rb") as file:

        supabase.storage.from_("detection-frames").upload(
            path=file_name,
            file=file,
            file_options={
                "upsert": "true"
            }
        )

    public_url = supabase.storage.from_(
        "detection-frames"
    ).get_public_url(file_name)

    return public_url

    public_url = supabase.storage.from_(
        "detection-frames"
    ).get_public_url(file_name)

    return public_url

def download_video(url, save_path):

    response = requests.get(url, stream=True)

    response.raise_for_status()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "wb") as file:

        for chunk in response.iter_content(chunk_size=8192):

            if chunk:
                file.write(chunk)

    print(f"Video downloaded successfully: {save_path}")

def upload_processed_video(file_path, flight_id):

    file_name = f"{flight_id}_{int(time.time())}.mp4"

    with open(file_path, "rb") as file:

        supabase.storage.from_("processed-videos").upload(
            file_name,
            file
        )

    public_url = supabase.storage.from_(
        "processed-videos"
    ).get_public_url(file_name)

    return public_url


def build_output_video():

    command = [
        "ffmpeg",
        "-y",
        "-framerate", "10",
        "-i", "annotated_frames/frame_%04d.png",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        OUTPUT_VIDEO
    ]

    subprocess.run(command)


while True:

    flight_id = None

    try:

        response = execute_with_retry(
            lambda: supabase.table("flights")
            .select("*")
            .eq("status", "pending")
            .limit(1)
            .execute()
        )

        flights = response.data

        if not flights:
            print("No pending flights...")
            time.sleep(5)
            continue

        flight = flights[0]

        flight_id = flight["id"]

        print(f"Processing flight: {flight_id}")

        clear_folder(FRAMES_FOLDER)

        clear_folder(ANNOTATED_FOLDER)

        clear_folder("outputs")

        execute_with_retry(
            lambda: supabase.table("flights")
            .update({"status": "processing"})
            .eq("id", flight_id)
            .execute()
        )

        video_url = flight["uploaded_video_url"]

        print("Downloading video...")

        download_video(video_url, TEMP_VIDEO)

        print("Extracting frames...")

        extract_frames(
            TEMP_VIDEO,
            FRAMES_FOLDER
        )

        print("Running detection + classification pipeline...")

        # DETECTION + CLASSIFICATION
        detections = process_frames(
            FRAMES_FOLDER
        )

        print(f"Filtered detections found: {len(detections)}")

        print("Annotating frames...")

        # MANUAL ANNOTATION
        annotate_frames(
            FRAMES_FOLDER,
            detections,
            ANNOTATED_FOLDER
        )
        
        print("Uploading detection frames...")

        print("Clearing old detections...")

        execute_with_retry(
            lambda: supabase.table("detections")
            .delete()
            .eq("flight_id", flight_id)
            .execute()
        )

        print("Saving new detections...")

        # BULK INSERT PREP
        
        uploaded_frames = {}

        for detection in detections:

            detection["flight_id"] = flight_id

            frame_name = detection["frame_name"]

            # UPLOAD FRAME ONLY ONCE
            if frame_name not in uploaded_frames:

                frame_path = os.path.join(
                    ANNOTATED_FOLDER,
                    frame_name
                )

                frame_url = upload_detection_frame(
                    frame_path,
                    flight_id,
                    frame_name
                )

                uploaded_frames[frame_name] = frame_url

            detection["frame_image_url"] = uploaded_frames[frame_name]
            
            
        # BULK INSERT
        if detections:

            execute_with_retry(
                lambda: supabase.table("detections")
                .insert(detections)
                .execute()
            )

        print("Building replay video...")

        build_output_video()

        if os.path.exists(OUTPUT_VIDEO):
            print("Replay video generated successfully")
        else:
            print("Replay video failed")

        print("Uploading replay video...")

        processed_video_url = upload_processed_video(
            OUTPUT_VIDEO,
            flight_id
        )

        print("Finalizing flight...")

        execute_with_retry(
            lambda: supabase.table("flights")
            .update({
                "status": "completed",
                "processed_video_url": processed_video_url,
                "total_detections": len(detections),
            })
            .eq("id", flight_id)
            .execute()
        )

        print("Processing completed!")

        cleanup_temp_files()

    except Exception as error:

        if flight_id:
            print(f"ERROR processing flight {flight_id}:", error)
            cleanup_temp_files()

            try:
                execute_with_retry(
                    lambda: supabase.table("flights")
                    .update({"status": "failed"})
                    .eq("id", flight_id)
                    .execute()
                )
            except Exception as inner_error:
                print("FAILED STATUS ERROR:", inner_error)
        elif is_connection_error(error):
            print("Supabase polling connection dropped, reconnecting...")
            reset_supabase_client()
        else:
            print("ERROR while polling for flights:", error)

    time.sleep(5)