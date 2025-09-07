import streamlit as st
import numpy as np
import tempfile
import requests
import wave
from audiorecorder import audiorecorder  # simple recorder widget

# ==========================
# CONFIG
# ==========================
API_KEY = "YOUR_SARVAM_API_KEY"
ASR_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"

st.title("🎤 Telugu Speech → English Translation (Record Audio)")

# ==========================
# RECORD AUDIO
# ==========================
audio = audiorecorder("🎙️ Start Recording", "⏹ Stop Recording")

if len(audio) > 0:
    st.audio(audio.tobytes(), format="audio/wav")

    # Save to temp WAV file
    wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(16000)
        wf.writeframes(audio.tobytes())

    # ==========================
    # TRANSCRIBE (Telugu)
    # ==========================
    if st.button("📝 Transcribe & Translate"):
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
