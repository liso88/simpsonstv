import os
import subprocess

# Set the absolute path to your video folder here
FOLDER_PATH = "simpsonstv/videos/"

def get_video_files(folder_path, extensions=None):
    if extensions is None:
        extensions = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv']

    return [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[1].lower() in extensions
    ]

def play_videos_with_vlc(video_files):
    if not video_files:
        print("No video files found.")
        return

    # Add --loop flag to enable looping playback
    command = [ 'mpv', '--fullscreen', '--video-rotate=270', '--loop=inf',    f"--input-ipc-server=/run/user/{os.getuid()}/mpvsocket"] + video_files
    subprocess.run(command)

if __name__ == "__main__":
    if not os.path.isdir(FOLDER_PATH):
        print(f"Error: {FOLDER_PATH} is not a valid directory.")
    else:
        video_files = get_video_files(FOLDER_PATH)
        play_videos_with_vlc(video_files)
