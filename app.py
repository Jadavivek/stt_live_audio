import streamlit as st
import requests
import io
from pydub import AudioSegment
from pydub.utils import which
from st_audiorec import st_audiorec  # pip install streamlit-audiorec pydub

# ---------------------------
# Configure FFmpeg for pydub
# ---------------------------
AudioSegment.converter = which("ffmpeg")  # Ensure ffmpeg is in PATH

# ---------------------------
# API CONFIG
# ---------------------------
API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"  # Replace with your Sarvam API key
ASR_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"

# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(page_title="Telugu → English Transcriber", layout="centered")
st.title("🎤 Telugu Speech → English Translation (Sarvam AI)")
st.write("Record your voice, transcribe to Telugu, and translate to English!")

# ---------------------------
# Audio Recorder UI
# ---------------------------
wav_audio_data = st_audiorec()  # Browser recording

if wav_audio_data is not None:
    st.audio(wav_audio_data, format="audio/wav")
    st.success("✅ Audio recorded!")

    if st.button("Transcribe & Translate"):
        try:
            # Convert raw bytes to WAV via pydub
            audio_bytes = io.BytesIO(wav_audio_data)
            audio = AudioSegment.from_file(audio_bytes, format="wav")
            buf = io.BytesIO()
            audio.export(buf, format="wav")
            buf.seek(0)

            headers = {"Authorization": f"Bearer {API_KEY}"}

            # Step 1: Transcribe Telugu audio
            resp1 = requests.post(
                ASR_ENDPOINT,
                headers=headers,
                files={"audio": ("audio.wav", buf, "audio/wav")},
                data={"model": "saarika"},  # Telugu ASR model
            )
            resp1.raise_for_status()
            telugu_text = resp1.json().get("text", "")
            st.write("**📝 Telugu Transcription:**", telugu_text)

            # Step 2: Translate Telugu → English
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

        except requests.exceptions.HTTPError as errh:
            st.error(f"❌ HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            st.error(f"❌ Connection Error: {errc}")
        except requests.exceptions.Timeout as errt:
            st.error(f"❌ Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            st.error(f"❌ Error: {err}")
