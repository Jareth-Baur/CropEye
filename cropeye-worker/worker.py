import os
import time
import requests
import subprocess
import shutil

from dotenv import load_dotenv
from supabase import create_client

from process_video import extract_frames, process_frames

from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


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
    


def download_video(url, save_path):

    response = requests.get(url)

    with open(save_path, "wb") as file:
        file.write(response.content)

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

    try:

        response = (
            supabase.table("flights")
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

        (
            supabase.table("flights")
            .update({"status": "processing"})
            .eq("id", flight_id)
            .execute()
        )

        video_url = flight["uploaded_video_url"]

        download_video(video_url, TEMP_VIDEO)

        extract_frames(TEMP_VIDEO, FRAMES_FOLDER)

        detections = process_frames(
            FRAMES_FOLDER,
            ANNOTATED_FOLDER
        )
        
        supabase.table("detections") \
            .delete() \
            .eq("flight_id", flight_id) \
            .execute()
            
        for detection in detections:

            detection["flight_id"] = flight_id

            (
                supabase.table("detections")
                .insert(detection)
                .execute()
            )

        build_output_video()
        if os.path.exists(OUTPUT_VIDEO):
            print("Replay video generated successfully")
        else:
            print("Replay video failed")

        processed_video_url = upload_processed_video(
            OUTPUT_VIDEO,
            flight_id
        )
        
        print("Processing completed!")

        (
            supabase.table("flights")
           .update({
            "status": "completed",
            "processed_video_url": processed_video_url,
            "total_detections": len(detections)
        })
            .eq("id", flight_id)
            .execute()
        )

    except Exception as error:
        print("ERROR:", error)

    time.sleep(5)
    