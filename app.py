from flask import Flask, request, render_template
import os
import cv2
from moviepy.editor import VideoFileClip  # Correct import

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        # Retrieve uploaded video and form data
        video = request.files.get('video')  # Use `get` for better safety
        start_time = request.form.get('start_time', type=int)
        end_time = request.form.get('end_time', type=int)

        if not video:
            return "No video uploaded! Please select a file."

        # Save uploaded video
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        video.save(filepath)

        # Ensure valid time range
        clip = VideoFileClip(filepath)
        if start_time < 0 or end_time > clip.duration or start_time >= end_time:
            return f"Invalid time range! Start: {start_time}, End: {end_time}, Video Duration: {clip.duration:.2f}s"

        # Create GIF
        gif_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.gif')
        create_gif(filepath, start_time, end_time, gif_path)

        return f"GIF created: <a href='/static/output.gif'>View GIF</a>"
    except Exception as e:
        # Debugging error message
        return f"Error occurred: {str(e)}"

def create_gif(video_path, start_time, end_time, output_path, fps=10):
    try:
        # Validate video file exists
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Create GIF
        clip = VideoFileClip(video_path).subclip(start_time, end_time)
        clip.write_gif(output_path, fps=fps)
    except Exception as e:
        raise RuntimeError(f"Failed to create GIF: {str(e)}")

def extract_frames(video_path, output_folder, frame_rate=30):
    cap = cv2.VideoCapture(video_path)
    count = 0
    os.makedirs(output_folder, exist_ok=True)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % frame_rate == 0:  # Save one frame every 'frame_rate' frames
            frame_path = os.path.join(output_folder, f"frame{count}.jpg")
            cv2.imwrite(frame_path, frame)
        count += 1
    cap.release()
    return output_folder

def detect_scenes(video_path):
    cap = cv2.VideoCapture(video_path)
    prev_frame = None
    scenes = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, frame)
            if diff.mean() > 50:  # Threshold for scene change
                scenes.append(frame_count)
        prev_frame = frame
        frame_count += 1

    cap.release()
    return scenes

if __name__ == '__main__':
    app.run(debug=True)
