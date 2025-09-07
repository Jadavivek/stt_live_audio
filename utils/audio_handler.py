import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import numpy as np
import io
import wave
import queue
import time

class AudioRecorder:
    """Handle audio recording in Streamlit"""
    
    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        
    def record(self):
        """Record audio using streamlit-audio-recorder"""
        # Using st.audio_input for simplicity (requires streamlit>=1.31.0)
        # For older versions, we'll use a file uploader as fallback
        
        try:
            # Try using audio_input (newer Streamlit versions)
            audio_value = st.audio_input("Click to record", key="audio_recorder")
            if audio_value:
                return audio_value.getvalue()
        except AttributeError:
            # Fallback for older Streamlit versions
            st.info("🎤 Upload an audio file or use your device's recorder")
            uploaded_file = st.file_uploader(
                "Choose an audio file", 
                type=['wav', 'mp3', 'm4a'],
                key="audio_uploader"
            )
            if uploaded_file:
                return uploaded_file.getvalue()
        
        return None

# Alternative implementation using streamlit-webrtc for real-time recording
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []
        
    def recv(self, frame):
        self.frames.append(frame.to_ndarray())
        return frame
    
    def get_audio_data(self):
        if not self.frames:
            return None
            
        audio_data = np.concatenate(self.frames, axis=0)
        
        # Convert to WAV format
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_data.tobytes())
        
        buffer.seek(0)
        return buffer.getvalue()