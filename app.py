import streamlit as st
import tempfile
import subprocess
import requests
import os
import time

SARVAM_API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"

def convert_to_wav(input_file, output_file):
    command = [
        "ffmpeg", "-y", "-i", input_file,
        "-ar", "16000", "-ac", "1", output_file
    ]
    subprocess.run(command, check=True)
    return output_file

def transcribe_and_translate(audio_path):
    url = "https://api.sarvam.ai/speech-to-text"  # check actual endpoint
    headers = {"Authorization": f"Bearer {SARVAM_API_KEY}"}
    with open(audio_path, "rb") as f:
        files = {"file": f}
        data = {"source_language": "te", "target_language": "en"}
        response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        res = response.json()
        return res.get("text", "No Telugu text"), res.get("translated_text", "No English translation")
    else:
        return None, f"Error: {response.text}"

st.title("🎙️ Live Telugu → English Transcription")

# Step 1: Record short audio clips
audio_chunk = st.audio_input("🎤 Speak Telugu", key="mic")  # works in Streamlit 1.29+

if audio_chunk is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_in:
        tmp_in.write(audio_chunk.getbuffer())
        tmp_in.flush()

        # Convert to WAV
        tmp_wav = tmp_in.name.replace(".webm", ".wav")
        convert_to_wav(tmp_in.name, tmp_wav)

        # Step 2: Transcribe + Translate
        telugu_text, english_text = transcribe_and_translate(tmp_wav)

        if telugu_text:
            st.info(f"📝 Telugu: {telugu_text}")
            st.success(f"🌍 English: {english_text}")
