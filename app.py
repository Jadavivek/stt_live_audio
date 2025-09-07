import streamlit as st
import requests
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import tempfile
import soundfile as sf

st.title("🎤 Live Telugu Speech → English Translation")

API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"
ASR_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"

# --------------------------
# Audio Processor Class
# --------------------------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame):
        self.frames.append(frame.to_ndarray())
        return frame

# --------------------------
# Start WebRTC audio streaming
# --------------------------
webrtc_ctx = webrtc_streamer(
    key="live-transcribe",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=AudioProcessor,
    async_processing=True,
)

# --------------------------
# Transcribe & Translate Button
# --------------------------
if webrtc_ctx.audio_receiver and st.button("🎙️ Transcribe & Translate"):
    audio_processor = webrtc_ctx.audio_processor
    if audio_processor and audio_processor.frames:
        audio_data = np.concatenate(audio_processor.frames, axis=0)

        # Save temp WAV
        wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        sf.write(wav_path, audio_data, 16000, format='wav')

        # --------------------------
        # Transcribe Telugu
        # --------------------------
        with open(wav_path, "rb") as f:
            files = {"audio": f}
            data = {"model": "saarika"}  # Telugu ASR model
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
    else:
        st.warning("⚠️ No audio recorded yet")
