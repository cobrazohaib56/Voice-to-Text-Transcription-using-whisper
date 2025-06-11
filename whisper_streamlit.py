import streamlit as st
import os
import wave
import pyaudio
import tempfile
from faster_whisper import WhisperModel
from datetime import datetime

# Disable symlink warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Apply modern UI styling
def apply_modern_styling():
    st.markdown("""
    <style>
        /* Base styles */
        .stApp {
            background-color: #f5f7fa;
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .stApp {
                background-color: #0e1117;
            }
            .card {
                background-color: #1a1c24 !important;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
            }
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        
        /* Main title */
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(90deg, #4776E6 0%, #8E54E9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        
        /* Card container */
        .card {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .card:hover {
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        /* Card title */
        .card-title {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f0f0f0;
            color: #333;
        }
        
        /* Buttons */
        .primary-btn {
            background: linear-gradient(90deg, #4776E6 0%, #8E54E9 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 1rem;
        }
        .primary-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(142, 84, 233, 0.2);
        }
        .secondary-btn {
            background-color: #f0f0f0;
            color: #333;
            border: none;
            padding: 10px 15px;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.2s ease;
            text-align: center;
        }
        .secondary-btn:hover {
            background-color: #e0e0e0;
        }
        .danger-btn {
            background-color: #ff5252;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.2s ease;
            text-align: center;
        }
        .danger-btn:hover {
            background-color: #ff3838;
        }
        .success-btn {
            background-color: #4caf50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.2s ease;
            text-align: center;
        }
        .success-btn:hover {
            background-color: #43a047;
        }
        
        /* Recording animation */
        .recording-pulse {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background: rgba(255, 82, 82, 0.05);
            border-radius: 10px;
            margin: 20px 0;
        }
        .pulse-dot {
            width: 20px;
            height: 20px;
            background-color: #ff5252;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% {
                transform: scale(0.8);
                opacity: 0.8;
            }
            50% {
                transform: scale(1.2);
                opacity: 1;
            }
            100% {
                transform: scale(0.8);
                opacity: 0.8;
            }
        }
        
        /* Transcript area */
        .transcript-container {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
        }
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #4776E6 0%, #8E54E9 100%);
        }
        
        /* Info box */
        .info-box {
            background-color: rgba(33, 150, 243, 0.1);
            border-left: 4px solid #2196f3;
            padding: 10px 15px;
            border-radius: 4px;
            margin: 10px 0;
        }
        
        /* Status badge */
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }
        .status-ready {
            background-color: #e3f2fd;
            color: #1565c0;
        }
        .status-recording {
            background-color: #ffebee;
            color: #c62828;
            animation: blink 1s infinite;
        }
        .status-processing {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        @keyframes blink {
            0% {opacity: 0.7;}
            50% {opacity: 1;}
            100% {opacity: 0.7;}
        }
        
        /* Utility classes */
        .center {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .mt-1 {
            margin-top: 0.5rem;
        }
        .mt-2 {
            margin-top: 1rem;
        }
        .mb-1 {
            margin-bottom: 0.5rem;
        }
        .mb-2 {
            margin-bottom: 1rem;
        }
        
        /* Settings panel */
        .settings-panel {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }
        .settings-item {
            flex: 1;
            min-width: 150px;
        }
        
        /* Text area customization */
        .stTextArea textarea {
            border-radius: 10px;
            border-color: #e0e0e0;
            padding: 15px;
            font-size: 16px;
            line-height: 1.5;
        }
    </style>
    """, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Voice Transcription App",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom styling
apply_modern_styling()

# Initialize session state variables
if 'transcription_history' not in st.session_state:
    st.session_state.transcription_history = ""

if 'recording_timestamp' not in st.session_state:
    st.session_state.recording_timestamp = None
    
if 'last_transcription' not in st.session_state:
    st.session_state.last_transcription = ""
    
if 'status' not in st.session_state:
    st.session_state.status = "Ready"
    
if 'whisper_model' not in st.session_state:
    # Load model on first run
    with st.spinner("Loading Whisper model..."):
        st.session_state.whisper_model = WhisperModel("medium.en", device="cpu", compute_type="int8")

# App header
st.markdown('<h1 class="main-title">Voice Transcription</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; margin-bottom: 40px;">Professional voice-to-text transcription powered by Whisper AI</p>', unsafe_allow_html=True)

# Main content container with 3 column layout
col1, col2, col3 = st.columns([1, 10, 1])

with col2:
    # Recording card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">Record Audio</h3>', unsafe_allow_html=True)
    
    # Settings panel
    st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
    
    # Duration selection
    st.markdown('<div class="settings-item">', unsafe_allow_html=True)
    duration = st.select_slider(
        "Recording Duration",
        options=[3, 5, 7, 10, 15, 20, 30],
        value=7,
        key="duration_slider",
        format_func=lambda x: f"{x} seconds"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Model selection
    st.markdown('<div class="settings-item">', unsafe_allow_html=True)
    model = st.selectbox(
        "Model Quality",
        options=["medium.en", "small.en", "base.en"],
        index=0,
        help="Higher quality models are more accurate but slower"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Status badge
    status_badge_style = "status-ready"
    if st.session_state.status == "Recording":
        status_badge_style = "status-recording"
    elif st.session_state.status == "Processing":
        status_badge_style = "status-processing"
    
    st.markdown(f'<div style="display: flex; align-items: center;">'
                f'<p style="margin: 0;">Status: {st.session_state.status}</p>'
                f'<span class="status-badge {status_badge_style}">{st.session_state.status}</span>'
                f'</div>', 
                unsafe_allow_html=True)
    
    # Record button
    if st.button("Start Recording", key="record_button"):
        # Update status
        st.session_state.status = "Recording"
        st.rerun()
    
    # Recording animation (shown only when recording)
    if st.session_state.status == "Recording":
        # Show recording indicator
        st.markdown('<div class="recording-pulse">'
                    '<div class="pulse-dot"></div>'
                    '<span>Recording in progress... Speak clearly into your microphone</span>'
                    '</div>', unsafe_allow_html=True)
        
        # Update timestamp
        st.session_state.recording_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        
        # Record audio
        frames = []
        chunk_size = 1024
        sample_rate = 16000
        total_chunks = int((sample_rate / chunk_size) * duration)
        
        # Create progress bar with custom styling
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        for i in range(total_chunks):
            data = stream.read(1024)
            frames.append(data)
            # Update progress
            progress = (i + 1) / total_chunks
            progress_bar.progress(progress)
            remaining = duration - int(duration * progress)
            progress_text.markdown(f"<div style='text-align: center;'>Recording: {remaining} seconds remaining</div>", unsafe_allow_html=True)
            
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
        
        # Update status
        st.session_state.status = "Processing"
        st.markdown('<div class="info-box">'
                    '<p style="margin: 0;">🔍 Processing audio with Whisper AI...</p>'
                    '</div>', unsafe_allow_html=True)
        
        # Transcribe the audio
        segments, _ = st.session_state.whisper_model.transcribe(temp_filename, beam_size=5)
        text = ""
        for segment in segments:
            text += segment.text
        
        # Add to transcription history
        if text.strip():
            st.session_state.last_transcription = text
            st.session_state.transcription_history += text + " "
            
        # Clean up
        os.remove(temp_filename)
        
        # Reset status
        st.session_state.status = "Ready"
        
        # Force a rerun to update the UI
        st.rerun()
    
    # Show info about last recording
    if st.session_state.recording_timestamp:
        st.caption(f"Last recording: {st.session_state.recording_timestamp}")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Transcription card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">Transcription Results</h3>', unsafe_allow_html=True)
    
    # Last transcription highlight
    if st.session_state.last_transcription:
        st.markdown('<div class="info-box">'
                    '<p style="margin: 0; font-weight: 600;">Latest transcription:</p>'
                    f'<p style="margin: 5px 0 0 0;">{st.session_state.last_transcription}</p>'
                    '</div>', unsafe_allow_html=True)
    
    # Complete transcription history
    st.markdown('<p class="mb-1"><strong>Full transcription history:</strong></p>', unsafe_allow_html=True)
    st.markdown('<div class="transcript-container">', unsafe_allow_html=True)
    transcript_text = st.text_area("", 
                                   value=st.session_state.transcription_history,
                                   height=200,
                                   label_visibility="collapsed")
    st.session_state.transcription_history = transcript_text  # Allow manual edits
    st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons with better layout
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📋 Copy Text", key="copy_btn", type="primary"):
            st.code(st.session_state.transcription_history)
            st.success("Text copied! Use Ctrl+C/Cmd+C to copy to clipboard")
    
    with action_col2:
        if st.button("🧹 Clear All", key="clear_btn", type="secondary"):
            st.session_state.transcription_history = ""
            st.session_state.last_transcription = ""
            st.rerun()
            
    with action_col3:
        if st.session_state.transcription_history:
            st.download_button(
                label="💾 Download",
                data=st.session_state.transcription_history,
                file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key="download_btn",
                type="primary"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<hr style="margin-top: 2rem; margin-bottom: 1rem; opacity: 0.3;">', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #777; font-size: 0.8rem;">Voice Transcription App • Powered by Whisper AI</p>', unsafe_allow_html=True)