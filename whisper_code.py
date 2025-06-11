import os
import wave
import pyaudio
import numpy as np
import time
from faster_whisper import WhisperModel

# Disable symlink warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# ANSI color codes for colorful output
NEON_GREEN = "\033[92m"
RESET_COLOR = "\033[0m"

def record_audio(p, stream, file_path, record_seconds=10):
    """
    Record audio from the microphone for a fixed duration.
    
    Args:
        p: PyAudio instance
        stream: PyAudio stream
        file_path: Path to save the audio file
        record_seconds: Number of seconds to record
    """
    print(f"Recording for {record_seconds} seconds...")
    
    frames = []
    # Calculate total chunks to record based on frame rate and buffer size
    chunk_size = 1024
    sample_rate = 16000
    total_chunks = int((sample_rate / chunk_size) * record_seconds)
    
    # Record for the specified duration
    for _ in range(total_chunks):
        data = stream.read(chunk_size)
        frames.append(data)
    
    print("Recording finished. Transcribing...")
    
    # Save the recorded audio
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return True

def transcribe_chunk(model, chunk_file):
    """
    Transcribe an audio chunk using the Whisper model.
    
    Args:
        model: Whisper model instance
        chunk_file: Path to the audio file
    
    Returns:
        Transcribed text
    """
    segments, _ = model.transcribe(chunk_file, beam_size=5)
    text = ""
    for segment in segments:
        text += segment.text
    return text

def main():
    # Choose your model settings
    model_size = "medium.en"
    # Use CPU instead of CUDA
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    
    accumulated_transcription = ""  # Initialize an empty string to accumulate transcriptions
    
    try:
        while True:
            input("Press Enter to start recording (10 seconds)...")
            chunk_file = "temp_chunk.wav"
            if record_audio(p, stream, chunk_file, record_seconds=10):
                transcription = transcribe_chunk(model, chunk_file)
                print(NEON_GREEN + transcription + RESET_COLOR)
                
                # Append the new transcription to the accumulated transcription
                accumulated_transcription += transcription + " "
                
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
            
    except KeyboardInterrupt:
        print("Stopping...")
        # Write the accumulated transcription to the log file
        with open("log.txt", "w") as log_file:
            log_file.write(accumulated_transcription)
    
    finally:
        print("LOG:" + accumulated_transcription)
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()