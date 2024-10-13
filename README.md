# Captionator

Captionator is a Python-based tool that automatically transcribes and captions video files using OpenAI's Whisper model. It adds stylized captions to videos, emphasizing certain words for better viewer engagement.

## Features

- Automatic video transcription using Whisper
- Dynamic caption generation with word emphasis
- Customizable caption styling (font size, color, position)
- Supports various video formats
- Easy-to-use command-line interface

## Prerequisites

- Python 3.7+
- FFmpeg
- ImageMagick

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Barathkumar0502/captionator.git
   cd captionator
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Ensure FFmpeg and ImageMagick are installed and accessible in your system PATH.

## Usage

Run the script with the following command:

```
python captionator/app.py
```

The script will prompt you for the input video file path. Alternatively, you can modify the `file_path` variable in the script to set a default input file.

## Configuration

- Adjust the `models_dir` variable to set the directory for Whisper models.
- Modify the `change_settings()` function call to set the correct path for ImageMagick on your system.

## Output

The captioned video will be saved in the same directory as the input video, with "_captioned" appended to the filename.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here, e.g., MIT License]

## Acknowledgements

- OpenAI's Whisper for transcription
- MoviePy for video editing
- Librosa for audio processing
