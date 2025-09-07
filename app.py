import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import numpy as np
import tempfile
import requests
import soundfile as sf

st.title("🎤 Live Telugu Speech → English Translation")

API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"
ASR_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


class AudioRecorder(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.frames.append(audio)
        return frame


ctx = webrtc_streamer(
    key="example",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=AudioRecorder,
)

if ctx.audio_processor and st.button("🛑 Stop & Process Recording"):
    if ctx.audio_processor.frames:
        audio_data = np.concatenate(ctx.audio_processor.frames, axis=0)
        tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        sf.write(tmp_wav, audio_data, 16000)

        st.audio(tmp_wav, format="audio/wav")

        # --------------------------
        # Transcribe Telugu
        # --------------------------
        with open(tmp_wav, "rb") as f:
            files = {"audio": f}
            data = {"model": "saarika"}  # Telugu ASR model
            resp = requests.post(ASR_ENDPOINT, headers=HEADERS, files=files, data=data)

        if resp.status_code == 200:
            telugu_text = resp.json().get("text", "")
            st.markdown(f"**📝 Telugu Transcription:** {telugu_text}")

            # --------------------------
            # Translate to English
            # --------------------------
            trans_data = {
                "model": "mayura",
                "text": telugu_text,
                "source": "te-IN",
                "target": "en-IN",
            }
            trans_resp = requests.post(TRANSLATE_ENDPOINT, headers=HEADERS, json=trans_data)

            if trans_resp.status_code == 200:
                english_text = trans_resp.json().get("translation", "")
                st.markdown(f"**🌍 English Translation:** {english_text}")
            else:
                st.error("❌ Translation failed")
        else:
            st.error("❌ Transcription failed")

        # Download button
        st.download_button(
            "💾 Download Recorded WAV",
            data=open(tmp_wav, "rb"),
            file_name="recorded_audio.wav",
            mime="audio/wav",
        )
