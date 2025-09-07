import streamlit as st
import requests
import tempfile
import numpy as np
import soundfile as sf
from streamlit_audio_recorder import st_audiorecorder  # pip install streamlit-audio-recorder

# --------------------------
# App Title
# --------------------------
st.title("🎤 Live Telugu Speech → English Translation")

# --------------------------
# Sarvam API configuration
# --------------------------
API_KEY = "YOUR_SARVAM_API_KEY"
ASR_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# --------------------------
# Audio Recorder UI
# --------------------------
st.markdown("Click 'Start Recording' to record your speech.")
audio_bytes = st_audiorecorder(key="recorder")

if audio_bytes:
    # Show live audio playback
    st.audio(audio_bytes, format="audio/wav")

    # Save temporary WAV
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    with open(tmp_wav, "wb") as f:
        f.write(audio_bytes)

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

    # --------------------------
    # Download recorded audio
    # --------------------------
    st.download_button(
        label="💾 Download Recorded WAV",
        data=open(tmp_wav, "rb"),
        file_name="recorded_audio.wav",
        mime="audio/wav",
    )
else:
    st.info("🎙️ Press 'Start Recording' and speak to transcribe and translate.")
