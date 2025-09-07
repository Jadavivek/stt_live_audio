import streamlit as st
import numpy as np
import tempfile
import wave
import requests
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# ==========================
# CONFIG
# ==========================
API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"
ASR_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"

st.title("🎤 Telugu Speech → English Translation (Live Recorder)")

# ==========================
# AUDIO PROCESSOR
# ==========================
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame):
        arr = frame.to_ndarray()
        self.frames.append(arr)
        return frame

# ==========================
# WEBRTC AUDIO STREAMER
# ==========================
ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=256,
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=AudioProcessor,
    async_processing=True,
)

# ==========================
# STOP & TRANSCRIBE BUTTON
# ==========================
if ctx.audio_processor:
    if st.button("⏹ Stop & Transcribe"):
        if not ctx.audio_processor.frames:
            st.error("⚠️ No audio recorded! Please record some speech first.")
        else:
            # Combine frames
            audio_data = np.concatenate(ctx.audio_processor.frames, axis=0)

            # Save as WAV
            wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(16000)
                wf.writeframes(audio_data.astype(np.int16).tobytes())

            st.success("✅ Audio recorded successfully!")
            st.audio(wav_path, format="audio/wav")

            # ==========================
            # TRANSCRIBE (Telugu)
            # ==========================
            headers = {"Authorization": f"Bearer {API_KEY}"}
            with open(wav_path, "rb") as f:
                files = {"audio": f}
                data = {"model": "saarika"}  # Telugu STT model
                resp = requests.post(ASR_ENDPOINT, headers=headers, files=files, data=data)

            if resp.status_code == 200:
                telugu_text = resp.json().get("text", "")
                st.write("📝 **Telugu Transcription:**", telugu_text)

                # ==========================
                # TRANSLATE (English)
                # ==========================
                trans_data = {
                    "model": "mayura",
                    "text": telugu_text,
                    "source": "te-IN",
                    "target": "en-IN",
                }
                trans_resp = requests.post(TRANSLATE_ENDPOINT, headers=headers, json=trans_data)

                if trans_resp.status_code == 200:
                    english_text = trans_resp.json().get("translation", "")
                    st.write("🌍 **English Translation:**", english_text)
                else:
                    st.error("❌ Translation failed: " + trans_resp.text)
            else:
                st.error("❌ Transcription failed: " + resp.text)
