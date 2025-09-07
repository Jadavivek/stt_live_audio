import streamlit as st
import asyncio
import base64
import tempfile
import numpy as np
import ffmpeg
import requests
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

API_KEY = "sk_2e681bna_IQkRnfFTXLYEpyj39shqTNlX"
STT_WS_URL = "wss://api.sarvam.ai/speech-to-text-stream"  # Placeholder
TRANSLATE_WS_URL = "wss://api.sarvam.ai/speech-to-text-translate-stream"

st.title("🎙 Live Telugu → English Transcription")

class Proc(AudioProcessorBase):
    def __init__(self):
        self.buf = bytearray()

    def recv_audio(self, frame):
        self.buf.extend(frame.to_ndarray().flatten().tobytes())
        return frame

webrtc_ctx = webrtc_streamer(
    key="live-stream",
    mode=WebRtcMode.SENDONLY,
    media_stream_constraints={"audio": True, "video": False},
    audio_receiver_size=1024,
    async_processing=True,
    audio_processor_factory=Proc,
)

async def stream_audio_and_transcribe(bytes_audio):
    import websockets, json
    async with websockets.connect(STT_WS_URL, extra_headers={"Authorization": f"Bearer {API_KEY}"}) as ws:
        await ws.send(json.dumps({"language_code": "te-IN", "model": "saarika:v2"}))
        await ws.send(base64.b64encode(bytes_audio).decode())
        response = await ws.recv()
        return response

if webrtc_ctx.audio_receiver and st.button("Start Live Transcription"):
    audio_bytes = webrtc_ctx.audio_processor.buf
    # Convert PCM to WAV
    pcm_file = tempfile.NamedTemporaryFile(delete=False, suffix=".raw")
    pcm_file.write(audio_bytes)
    pcm_file.flush()

    wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    (
        ffmpeg
        .input(pcm_file.name, f="s16le", ar="48000", ac=1)
        .output(wav_path, ar=16000, ac=1)
        .overwrite_output()
        .run(quiet=True)
    )

    async def run():
        telugu_response = await stream_audio_and_transcribe(open(wav_path, "rb").read())
        st.write("**Telugu Transcription:**", telugu_response)

        async with websockets.connect(TRANSLATE_WS_URL, extra_headers={"Authorization": f"Bearer {API_KEY}"}) as ws:
            await ws.send(json.dumps({"model": "saaras:v2", "language_code": "te-IN"}))
            await ws.send(base64.b64encode(open(wav_path, "rb").read()).decode())
            translation = await ws.recv()
            st.write("**English Translation:**", translation)

    asyncio.run(run())
