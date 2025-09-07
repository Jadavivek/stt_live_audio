import streamlit as st
import subprocess
import os
import tempfile
import requests

SARVAM_API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"  # Store in Streamlit secrets

def convert_to_wav(input_file, output_file):
    """Convert any audio file to 16kHz mono WAV using ffmpeg."""
    command = [
        "ffmpeg",
        "-y",  # overwrite output
        "-i", input_file,
        "-ar", "16000",  # sample rate
        "-ac", "1",      # mono
        output_file
    ]
    subprocess.run(command, check=True)
    return output_file

def transcribe_and_translate(audio_path):
    """Send audio to Sarvam AI for Telugu → English transcription."""
    url = "https://api.sarvam.ai/speech-to-text"  # adjust if different endpoint
    headers = {"Authorization": f"Bearer {SARVAM_API_KEY}"}

    with open(audio_path, "rb") as f:
        files = {"file": f}
        data = {"source_language": "te", "target_language": "en"}
        response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        return response.json().get("text", "No text found")
    else:
        return f"Error: {response.text}"

st.title("🎙️ Telugu → English Speech Transcription")

uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a"])

if uploaded_file:
    st.audio(uploaded_file)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_in:
            tmp_in.write(uploaded_file.read())
            tmp_in.flush()

            # Convert to WAV
            convert_to_wav(tmp_in.name, tmp_wav.name)

        # Transcribe
        st.write("Transcribing with Sarvam AI...")
        result = transcribe_and_translate(tmp_wav.name)
        st.success("✅ Transcription complete:")
        st.write(result)
