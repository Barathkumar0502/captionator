import os
import whisper
import librosa
import numpy as np
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import time
import torch
import re
from moviepy.config import change_settings

# Set the path to ImageMagick binary
change_settings({"IMAGEMAGICK_BINARY": r"D:\caption1\image\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def load_local_model(model_name, models_dir):
    os.environ["WHISPER_HOME"] = models_dir
    print(f"Loading Whisper model: {model_name} from {models_dir}")
    model = whisper.load_model(model_name)
    return model

def get_word_size(word):
    # Simple heuristic: capitalize words are considered stressed
    return 120 if word.isupper() else 90  # Tripled font sizes

def create_caption_clip(text, duration, start_time, video_width):
    words = text.split()
    word_clips = []
    x_position = 0  # Starting x position

    for word in words:
        font_size = get_word_size(word)
        word_clip = TextClip(word, fontsize=font_size, font='Arial', color='white')
        word_clip = word_clip.set_position((x_position, 0))
        word_clips.append(word_clip)
        x_position += word_clip.w + 10  # Add space between words

    caption_clip = CompositeVideoClip(word_clips, size=(video_width, max(clip.h for clip in word_clips)))
    caption_clip = caption_clip.set_position(('center', 'bottom')).set_duration(duration).set_start(start_time)
    return caption_clip

def transcribe_and_caption(file_path, model_name="large"):
    temp_dir = r"D:\caption1\temp"
    models_dir = r"D:\caption1\whisper_models"
    os.makedirs(temp_dir, exist_ok=True)
    audio_path = os.path.join(temp_dir, "temp_audio.wav")

    try:
        # Extract audio
        print(f"Extracting audio from video file: {file_path}")
        video = VideoFileClip(file_path)
        video.audio.write_audiofile(audio_path)

        # Load audio file
        print("Loading audio file...")
        audio, sr = librosa.load(audio_path, sr=16000)
        audio = audio.astype(np.float32)

        # Load model and transcribe
        model = load_local_model(model_name, models_dir)
        print(f"Transcribing audio...")
        result = model.transcribe(audio, fp16=False, language="en", task="transcribe")

        # Create caption clips
        caption_clips = []
        for segment in result['segments']:
            text = segment['text'].strip()
            # Simple stress detection: capitalize words ending with punctuation or ALL CAPS
            text = re.sub(r'\b(\w+[.!?])\b', lambda m: m.group(1).upper(), text)
            text = re.sub(r'\b([A-Z]{2,})\b', lambda m: m.group(1), text)
            
            caption_clip = create_caption_clip(text, segment['end'] - segment['start'], segment['start'], video.w)
            caption_clips.append(caption_clip)

        # Add captions to video
        final_video = CompositeVideoClip([video] + caption_clips)
        
        # Move captions higher
        for clip in caption_clips:
            clip.set_position(('center', lambda t: video.h - clip.h - 100))  # 100 pixels from bottom
        
        # Write output video
        output_path = os.path.splitext(file_path)[0] + "_captioned.mp4"
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        print(f"Captioned video saved to: {output_path}")
        return output_path

    except Exception as e:
        import traceback
        return f"An error occurred: {str(e)}\n{traceback.format_exc()}"
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"Temporary audio file removed: {audio_path}")

# Usage
file_path = r"D:\NIRANJAN\SIH DEMO VIDEO.mp4"
print(f"Starting transcription and captioning of: {file_path}")
output_path = transcribe_and_caption(file_path, model_name="large")
print("Process completed. Output video path:")
print(output_path)

# Print system information
import sys
import whisper
import moviepy

print("\nSystem Information:")
print(f"Python version: {sys.version}")
print(f"Whisper version: {whisper.__version__}")
print(f"MoviePy version: {moviepy.__version__}")
print(f"PyTorch version: {torch.__version__}")
