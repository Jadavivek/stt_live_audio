import streamlit as st
import requests
import base64
import tempfile
import ffmpeg

API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"  # put your key in .streamlit/secrets.toml

STT_URL = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_URL = "https://api.sarvam.ai/translate"

st.title("🎤 Audio → Telugu Transcription → English Translation")

uploaded_file = st.file_uploader("Upload or record an audio file", type=["wav", "mp3", "m4a"])

def convert_to_wav(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, ar=16000, ac=1, format="wav")
        .overwrite_output()
        .run(quiet=True)
    )
    return output_file

if uploaded_file is not None:
    # Save temp input file
    with tempfile.NamedTemporaryFile(delete=False, suffix="."+uploaded_file.name.split(".")[-1]) as tmp_in:
        tmp_in.write(uploaded_file.read())
        tmp_in.flush()

        # Convert to wav
        wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        convert_to_wav(tmp_in.name, wav_path)

        st.audio(wav_path, format="audio/wav")

        # Step 1: Transcribe Telugu
        with open(wav_path, "rb") as f:
            audio_bytes = f.read()

        st.info("Transcribing to Telugu...")
        stt_headers = {"Authorization": f"Bearer {API_KEY}"}
        stt_files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        stt_data = {"model": "saarika:v2", "language_code": "te-IN"}
        stt_resp = requests.post(STT_URL, headers=stt_headers, files=stt_files, data=stt_data)

        if stt_resp.status_code == 200:
            telugu_text = stt_resp.json().get("text", "")
            st.success("Telugu Transcription:")
            st.write(telugu_text)

            # Step 2: Translate Telugu → English
            st.info("Translating to English...")
            translate_headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            translate_payload = {
                "model": "saaras:v2",
                "input": telugu_text,
                "source_language_code": "te-IN",
                "target_language_code": "en-IN"
            }
            translate_resp = requests.post(TRANSLATE_URL, headers=translate_headers, json=translate_payload)

            if translate_resp.status_code == 200:
                english_text = translate_resp.json()["output"][0]["target_text"]
                st.success("English Translation:")
                st.write(english_text)
            else:
                st.error(f"Translation failed: {translate_resp.text}")
        else:
            st.error(f"Transcription failed: {stt_resp.text}")
