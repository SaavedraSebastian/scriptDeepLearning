import cv2
import os
import subprocess

def reverse_video_opencv_audio(input_path, output_path):

    
    temp_audio = "temp_audio.wav"
    audio_cmd = f'ffmpeg -i "{input_path}" -q:a 0 -map a "{temp_audio}" -y'
    subprocess.run(audio_cmd, shell=True, capture_output=True)
    
    cap = cv2.VideoCapture(input_path)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    
    cap.release()
    frames.reverse()
    
    temp_video = "temp_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    
    for frame in frames:
        out.write(frame)
    out.release()
    
    mix_cmd = f'ffmpeg -i "{temp_video}" -i "{temp_audio}" -c:v copy -c:a aac -y "{output_path}"'
    subprocess.run(mix_cmd, shell=True, capture_output=True)
    
    if os.path.exists(temp_audio):
        os.remove(temp_audio)
    if os.path.exists(temp_video):
        os.remove(temp_video)
    
    print(f"✓ Video con audio: {os.path.basename(output_path)}")

def process_folder():
    input_folder = "videos_data"
    output_folder = "videos"

    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if not file.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
            continue

        input_path = os.path.join(input_folder, file)
        name, ext = os.path.splitext(file)
        output_path = os.path.join(output_folder, f"{name}_rev.mp4")

        reverse_video_opencv_audio(input_path, output_path)

if __name__ == "__main__":
    print("=== REVERSOR CON OPENCV + AUDIO ===")
    process_folder()
    print("Proceso completado.")