import streamlit as st
import requests
import io
from pydub import AudioSegment
from st_audiorec import st_audiorec  # pip install streamlit-audiorec pydub

# ---------------------------
# API CONFIG
# ---------------------------
API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"  # Replace with your Sarvam AI key
ASR_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"

st.set_page_config(page_title="Telugu → English Transcriber", layout="centered")
st.title("🎤 Telugu Speech → English Translation (Sarvam AI)")

# ---------------------------
# AUDIO RECORDING
# ---------------------------
wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    st.audio(wav_audio_data, format="audio/wav")
    st.success("✅ Audio recorded!")

    if st.button("Transcribe & Translate"):
        try:
            # Convert raw bytes into a WAV file
            audio_bytes = io.BytesIO(wav_audio_data)
            audio = AudioSegment.from_file(audio_bytes, format="wav")

            buf = io.BytesIO()
            audio.export(buf, format="wav")
            buf.seek(0)

            headers = {"Authorization": f"Bearer {API_KEY}"}

            # Step 1: Telugu ASR
            resp1 = requests.post(
                ASR_ENDPOINT,
                headers=headers,
                files={"audio": ("audio.wav", buf, "audio/wav")},
                data={"model": "saarika"},  # Telugu model
            )
            resp1.raise_for_status()
            telugu_text = resp1.json().get("text", "")
            st.write("**📝 Telugu Transcription:**", telugu_text)

            # Step 2: Translation Telugu → English
            resp2 = requests.post(
                TRANSLATE_ENDPOINT,
                headers=headers,
                json={
                    "model": "mayura",
                    "text": telugu_text,
                    "source": "te-IN",
                    "target": "en-IN",
                },
            )
            resp2.raise_for_status()
            translated = resp2.json().get("translation", "")
            st.write("**🌍 English Translation:**", translated)

        except Exception as e:
            st.error(f"❌ Error: {e}")
