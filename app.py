import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import numpy as np
import requests
import tempfile
import ffmpeg
from static_ffmpeg import add_paths

# Ensure ffmpeg works in Streamlit Cloud
add_paths()

# Sarvam API config
API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"   # 🔑 Replace with your API key
ASR_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_ENDPOINT = "https://api.sarvam.ai/translate"

st.title("🎤 Live Telugu → English Speech Transcription")

# --- Audio Processor ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.chunks = []

    def recv_audio(self, frame):
        # Collect audio frames
        data = frame.to_ndarray().flatten()
        self.chunks.append(data)
        return frame

# --- Start WebRTC mic stream ---
webrtc_ctx = webrtc_streamer(
    key="telugu-stt",
    mode=WebRtcMode.SENDONLY,
    media_stream_constraints={"audio": True, "video": False},
    audio_receiver_size=256,
    async_processing=True,
    audio_processor_factory=AudioProcessor,
)

# --- Convert raw PCM to WAV ---
def convert_to_wav(raw_audio, output_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".raw") as tmp_raw:
        tmp_raw.write(raw_audio)
        tmp_raw.flush()
        (
            ffmpeg
            .input(tmp_raw.name, f="s16le", ar="48000", ac="1")
            .output(output_file, ar=16000, ac=1)
            .overwrite_output()
            .run(quiet=True)
        )
    return output_file

# --- Main Logic ---
if webrtc_ctx.audio_receiver and st.button("🎙️ Transcribe"):
    # Join PCM chunks into bytes
    audio_data = np.concatenate(webrtc_ctx.audio_processor.chunks).astype(np.int16).tobytes()

    # Save as WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
        wav_path = tmp_wav.name
    convert_to_wav(audio_data, wav_path)

    # Step 1: Telugu Speech-to-Text
    headers = {"Authorization": f"Bearer {API_KEY}"}
    with open(wav_path, "rb") as f:
        resp1 = requests.post(ASR_ENDPOINT, headers=headers, files={"audio": f}, data={"model": "saarika"})
    telugu_text = resp1.json().get("text", "")
    st.write("📝 **Telugu Transcription:**", telugu_text)

    # Step 2: Translate Telugu → English
    resp2 = requests.post(
        TRANSLATE_ENDPOINT,
        headers=headers,
        json={"model": "mayura", "text": telugu_text, "source": "te-IN", "target": "en-IN"},
    )
    english_text = resp2.json().get("translation", "")
    st.write("🌍 **English Translation:**", english_text)
