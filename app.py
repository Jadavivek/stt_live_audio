import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import numpy as np
import av
import tempfile
import requests
import wave

API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"
STT_URL = "https://api.sarvam.ai/speech-to-text"
TRANSLATE_URL = "https://api.sarvam.ai/translate"

st.title("🎙️ Telugu STT + English Translation (Live Recording)")

# Step 1: Record audio from mic
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio_frame(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray()
        self.frames.append(pcm)
        return frame

ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

if ctx.audio_processor:
    if st.button("Stop & Transcribe"):
        # Save to wav
        audio_data = np.concatenate(ctx.audio_processor.frames, axis=0)
        wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(16000)
            wf.writeframes(audio_data.astype(np.int16).tobytes())

        st.audio(wav_path, format="audio/wav")

        # Step 2: Telugu transcription
        with open(wav_path, "rb") as f:
            audio_bytes = f.read()

        st.info("🔄 Transcribing...")
        stt_headers = {"Authorization": f"Bearer {API_KEY}"}
        stt_files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        stt_data = {"model": "saarika:v2", "language_code": "te-IN"}
        stt_resp = requests.post(STT_URL, headers=stt_headers, files=stt_files, data=stt_data)

        if stt_resp.status_code == 200:
            telugu_text = stt_resp.json().get("text", "")
            st.success("📝 Telugu Transcription:")
            st.write(telugu_text)

            # Step 3: Translate Telugu → English
            st.info("🔄 Translating...")
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
                st.success("🌍 English Translation:")
                st.write(english_text)
            else:
                st.error(f"Translation failed: {translate_resp.text}")
        else:
            st.error(f"Transcription failed: {stt_resp.text}")
