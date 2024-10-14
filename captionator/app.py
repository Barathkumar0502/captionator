import os
import whisper
import numpy as np
import librosa
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import time
import torch
import re
from PIL import Image, ImageDraw, ImageFont
import sys
import moviepy  # Add this import

def load_local_model(model_name, models_dir):
    os.environ["WHISPER_HOME"] = models_dir
    print(f"Loading Whisper model: {model_name} from {models_dir}")
    model = whisper.load_model(model_name)
    return model

def get_word_size(word):
    # Simple heuristic: capitalize words are considered stressed
    return 120 if word.isupper() else 90  # Tripled font sizes

def create_caption_clip(caption, video_width, video_height):
    font_size = 80
    font = ImageFont.truetype("arial.ttf", font_size)
    words = caption["text"].split()
    
    # Create a blank image
    img = Image.new('RGBA', (video_width, font_size + 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate total width of text
    total_width = sum(draw.textbbox((0, 0), word, font=font)[2] for word in words) + (len(words) - 1) * 10
    
    # Calculate starting x position to center the text
    x = (video_width - total_width) // 2
    y = 0
    
    for word in words:
        word_width = draw.textbbox((0, 0), word, font=font)[2]
        draw.text((x, y), word, font=font, fill=(255, 255, 255, 255))
        x += word_width + 10  # Add space between words
    
    # Convert PIL Image to numpy array
    img_array = np.array(img)
    
    # Create ImageClip from numpy array
    clip = ImageClip(img_array).set_duration(caption["end"] - caption["start"]).set_start(caption["start"])
    clip = clip.set_position(('center', 'bottom'))
    
    return clip

def transcribe_and_caption(file_path, model_name="large"):
    models_dir = r"D:\caption1\whisper_models"
    temp_dir = r"D:\caption1\temp"
    os.makedirs(temp_dir, exist_ok=True)
    audio_path = os.path.join(temp_dir, "temp_audio.wav")

    try:
        # Load video
        print(f"Loading video file: {file_path}")
        video = VideoFileClip(file_path)

        # Extract audio to a temporary WAV file
        print("Extracting audio...")
        video.audio.write_audiofile(audio_path, fps=16000, nbytes=2, codec='pcm_s16le')

        # Load audio using librosa
        audio, _ = librosa.load(audio_path, sr=16000)

        # Load model and transcribe
        model = load_local_model(model_name, models_dir)
        print(f"Transcribing audio...")
        result = model.transcribe(audio, fp16=False, language="en", task="transcribe", word_timestamps=True)

        return result, video
    except Exception as e:
        import traceback
        return f"An error occurred: {str(e)}\n{traceback.format_exc()}", None
    finally:
        # Clean up temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)

def format_captions(segments, max_chars_per_line=40):
    captions = []
    for segment in segments:
        words = segment.get("words", [])
        if not words:
            continue  # Skip segments with no words
        
        current_line = ""
        current_start = words[0]["start"]
        
        for word in words:
            if len(current_line) + len(word["word"]) > max_chars_per_line:
                captions.append({
                    "text": current_line.strip(),
                    "start": current_start,
                    "end": word["start"]
                })
                current_line = word["word"] + " "
                current_start = word["start"]
            else:
                current_line += word["word"] + " "
        
        if current_line:
            captions.append({
                "text": current_line.strip(),
                "start": current_start,
                "end": words[-1]["end"]
            })
    
    return captions

def debug_environment():
    print("Environment Debug Information:")
    print(f"Current working directory: {os.getcwd()}")
    print(f"PATH: {os.environ.get('PATH', 'Not set')}")
    print(f"Python version: {sys.version}")
    print(f"Moviepy version: {moviepy.__version__}")
    print(f"PIL version: {Image.__version__}")

# Usage
file_path = r"D:\NIRANJAN\SIH DEMO VIDEO.mp4"
print(f"Starting transcription and captioning of: {file_path}")

debug_environment()

result, video = transcribe_and_caption(file_path, model_name="large")

if isinstance(result, str):  # Error occurred
    print(result)
else:
    captions = format_captions(result["segments"])
    caption_clips = [create_caption_clip(caption, video.w, video.h) for caption in captions]
    
    final_video = CompositeVideoClip([video] + caption_clips)
    
    output_path = os.path.splitext(file_path)[0] + "_captioned.mp4"
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    print(f"Captioned video saved to: {output_path}")

# Clean up
if video:
    video.close()

# Print system information
import sys
import whisper
import moviepy

print("\nSystem Information:")
print(f"Python version: {sys.version}")
print(f"Whisper version: {whisper.__version__}")
print(f"MoviePy version: {moviepy.__version__}")
print(f"PyTorch version: {torch.__version__}")
