import streamlit as st
import os
import wave
import pyaudio
import tempfile
from faster_whisper import WhisperModel

# Disable symlink warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

st.set_page_config(
    page_title="Voice-to-Text Transcription",
    page_icon="🎤",
    layout="wide"
)

# App title and description
st.title("🎤 Voice-to-Text Transcription")
st.markdown("""
This app uses Whisper to transcribe your voice. Press the button to start recording for a fixed duration.
""")

# Initialize session state variables if they don't exist
if 'transcription_history' not in st.session_state:
    st.session_state.transcription_history = ""

if 'whisper_model' not in st.session_state:
    # Load model on first run
    with st.spinner("Loading Whisper model..."):
        st.session_state.whisper_model = WhisperModel("medium.en", device="cpu", compute_type="int8")
    # st.success("Model loaded successfully!")

def record_audio(duration=5):
    """Record audio for a fixed duration and return the file path"""
    st.markdown("🔴 **Recording...**")
    progress_bar = st.progress(0)
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    
    # Record audio
    frames = []
    chunk_size = 1024
    sample_rate = 16000
    total_chunks = int((sample_rate / chunk_size) * duration)
    
    for i in range(total_chunks):
        data = stream.read(1024)
        frames.append(data)
        # Update progress bar
        progress_bar.progress((i + 1) / total_chunks)
    
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        temp_filename = temp_audio.name
        
    # Save the recorded audio
    wf = wave.open(temp_filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    # Close stream and terminate PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return temp_filename

def transcribe_audio(audio_file):
    """Transcribe audio file using Whisper"""
    with st.spinner("Transcribing audio..."):
        segments, _ = st.session_state.whisper_model.transcribe(audio_file, beam_size=5)
        text = ""
        for segment in segments:
            text += segment.text
    return text

# UI Components
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Recording duration slider
    # duration = st.slider("Recording Duration (seconds)", min_value=3, max_value=30, value=5)

    duration = 7
    
    # Record button
    if st.button("🎙️ Start Recording", key="record_button"):
        audio_file = record_audio(duration)
        
        # Transcribe the audio
        transcription = transcribe_audio(audio_file)
        
        # Add to transcription history
        if transcription.strip():
            st.session_state.transcription_history += transcription + " "
            
        # Clean up
        os.remove(audio_file)
        
        # Force a rerun to update the UI
        st.rerun()

# Transcription display area
st.subheader("Transcription")
st.text_area("", value=st.session_state.transcription_history, height=200, key="transcript_display")

# Action buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Copy to Clipboard"):
        st.code(st.session_state.transcription_history)
        st.success("Copied to clipboard! (Select the text above and copy)")

with col2:
    if st.button("Clear"):
        st.session_state.transcription_history = ""
        st.rerun()