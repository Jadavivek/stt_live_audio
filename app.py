import streamlit as st
import requests
import base64
import tempfile
import wave

st.title("🎤 Live Telugu Speech → English Translation")

API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"
ASR_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"

# --------------------------
# Mic Recorder UI
# --------------------------
st.markdown(
    """
    <script src="https://cdn.jsdelivr.net/npm/streamlit-mic-recorder@0.1.0/dist/streamlit-mic-recorder.min.js"></script>
    <mic-recorder id="recorder"></mic-recorder>
    """,
    unsafe_allow_html=True
)

# Button to trigger recording
if st.button("🎙️ Record & Upload"):
    # JS sends base64 WAV string
    wav_b64 = st.experimental_get_query_params().get("audio", [None])[0]
    if wav_b64:
        audio_bytes = base64.b64decode(wav_b64)
        st.audio(audio_bytes, format="audio/wav")

        # Save WAV temporarily
        wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        with open(wav_path, "wb") as f:
            f.write(audio_bytes)

        # --------------------------
        # Transcribe Telugu
        # --------------------------
        with open(wav_path, "rb") as f:
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
