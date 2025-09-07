import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import numpy as np
import soundfile as sf
import tempfile
import requests

st.title("🎤 Live Telugu Speech → English Translation")

API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"
ASR_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"

# --------------------------
# Audio Processor
# --------------------------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame):
        self.frames.append(frame.to_ndarray())
        return frame

# --------------------------
# Start WebRTC audio stream
# --------------------------
ctx = webrtc_streamer(
    key="live-audio",
    mode=WebRtcMode.SENDONLY,
    media_stream_constraints={"audio": True, "video": False},
    audio_receiver_size=1024,
    async_processing=True,
    audio_processor_factory=AudioProcessor
)

# --------------------------
# Transcribe & Translate
# --------------------------
if ctx.audio_receiver and st.button("📝 Transcribe & Translate"):
    # Merge audio frames
    audio_data = np.concatenate(ctx.audio_processor.frames, axis=0)
    
    # Save to temporary WAV
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    sf.write(tmp_wav, audio_data, 16000)  # 16 kHz mono

    st.audio(tmp_wav, format="audio/wav")

    # --------------------------
    # Transcribe Telugu
    # --------------------------
    with open(tmp_wav, "rb") as f:
        files = {"audio": f}
        data = {"model": "saarika"}  # Telugu model
        headers = {"Authorization": f"Bearer {API_KEY}"}
        resp = requests.post(ASR_ENDPOINT, headers=headers, files=files, data=data)

    if resp.status_code == 200:
        telugu_text = resp.json().get("text", "")
        st.write("📝 Telugu Transcription:", telugu_text)

        # --------------------------
        # Translate to English
        # --------------------------
        trans_data = {
            "model": "mayura",
            "text": telugu_text,
            "source": "te-IN",
            "target": "en-IN",
        }
        trans_resp = requests.post(TRANSLATE_ENDPOINT, headers=headers, json=trans_data)

        if trans_resp.status_code == 200:
            english_text = trans_resp.json().get("translation", "")
            st.write("🌍 English Translation:", english_text)
        else:
            st.error("❌ Translation failed")
    else:
        st.error("❌ Transcription failed")

    # --------------------------
    # Download option
    # --------------------------
    st.download_button("💾 Download WAV", data=open(tmp_wav, "rb"), file_name="recorded_audio.wav")
