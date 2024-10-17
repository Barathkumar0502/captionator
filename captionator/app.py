from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
import uuid
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, concatenate_videoclips
from moviepy.video.fx.all import resize, speedx, colorx
import speech_recognition as sr

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mp3', 'wav', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'success': True, 'filename': filename})
    return jsonify({'error': 'File type not allowed'})

@app.route('/process_video', methods=['POST'])
def process_video():
    data = request.json
    timeline = data['timeline']
    output_filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    clips = []
    for item in timeline:
        if item['type'] == 'video':
            clip = VideoFileClip(os.path.join(app.config['UPLOAD_FOLDER'], item['filename']))
            if 'start' in item and 'end' in item:
                clip = clip.subclip(item['start'], item['end'])
            if 'speed' in item:
                clip = clip.fx(speedx, item['speed'])
            if 'color' in item:
                clip = clip.fx(colorx, item['color'])
        elif item['type'] == 'audio':
            clip = AudioFileClip(os.path.join(app.config['UPLOAD_FOLDER'], item['filename']))
            if 'start' in item and 'end' in item:
                clip = clip.subclip(item['start'], item['end'])
        elif item['type'] == 'text':
            clip = TextClip(item['text'], fontsize=item['fontsize'], color=item['color'])
            clip = clip.set_position(item['position']).set_duration(item['duration'])
        
        clips.append(clip)

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path)

    return jsonify({'output_url': f'/output/{output_filename}'})

@app.route('/generate_captions', methods=['POST'])
def generate_captions():
    filename = request.json['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    video = VideoFileClip(file_path)
    audio = video.audio
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_audio.wav")
    audio.write_audiofile(audio_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio_data)
        captions = [{"start": 0, "end": video.duration, "text": text}]
    except sr.UnknownValueError:
        captions = [{"start": 0, "end": video.duration, "text": "Could not understand audio"}]
    except sr.RequestError:
        captions = [{"start": 0, "end": video.duration, "text": "Could not request results; check your internet connection"}]

    os.remove(audio_path)
    return jsonify({'captions': captions})

@app.route('/apply_effect', methods=['POST'])
def apply_effect():
    data = request.json
    filename = data['filename']
    effect = data['effect']
    params = data.get('params', {})

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    clip = VideoFileClip(file_path)

    if effect == 'resize':
        clip = clip.fx(resize, width=params.get('width'), height=params.get('height'))
    elif effect == 'speed':
        clip = clip.fx(speedx, factor=params.get('factor', 1.0))
    elif effect == 'color':
        clip = clip.fx(colorx, factor=params.get('factor', 1.0))
    
    output_filename = f"effect_{uuid.uuid4()}.mp4"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    clip.write_videofile(output_path)

    return jsonify({'output_url': f'/output/{output_filename}'})

@app.route('/output/<filename>')
def get_output(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(debug=True)
