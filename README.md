# Voice Transcription App

A powerful voice-to-text transcription application built with Streamlit and powered by OpenAI's Whisper AI. This application provides a modern, user-friendly interface for real-time voice transcription with high accuracy.

## Features

- 🎤 Real-time voice recording with customizable duration
- 🎯 High-accuracy transcription using Whisper AI
- 💾 Save and download transcriptions
- 📋 Copy transcription text to clipboard
- 🎨 Modern, responsive UI with dark mode support
- 📱 Mobile-friendly interface
- 🔄 Continuous transcription history
- ⚡ Fast processing with optimized Whisper model

## Prerequisites

- Python 3.8 or higher
- PyAudio
- Streamlit
- faster-whisper

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cobrazohaib56/Voice-to-Text-Transcription-using-whisper.git
cd Voice-to-Text-Transcription-using-whisper
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run whisper_streamlit.py
```

2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)

3. Use the interface to:
   - Select recording duration
   - Choose model quality
   - Start recording
   - View and manage transcriptions

## Configuration

The application offers several customization options:

- **Recording Duration**: Choose between 3 to 30 seconds
- **Model Quality**: Select from different Whisper models:
  - medium.en (default, balanced accuracy and speed)
  - small.en (faster, slightly less accurate)
  - base.en (fastest, basic accuracy)

## Features in Detail

### Recording
- Click "Start Recording" to begin voice capture
- Visual recording indicator with remaining time
- Automatic processing after recording

### Transcription Management
- View latest transcription in highlighted box
- Access full transcription history
- Copy text to clipboard
- Download transcriptions as text files
- Clear all transcriptions

### UI Features
- Modern gradient design
- Dark mode support
- Responsive layout
- Progress indicators
- Status badges

## Technical Details

The application uses:
- Streamlit for the web interface
- PyAudio for audio recording
- faster-whisper for transcription
- Custom CSS for modern styling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the Whisper model
- Streamlit team for the amazing framework
- faster-whisper for optimized Whisper implementation 