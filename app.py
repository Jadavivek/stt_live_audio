import streamlit as st
import os
from utils.audio_handler import AudioRecorder
from utils.sarvam_client import SarvamAIClient
import tempfile
import base64

# Page config
st.set_page_config(
    page_title="Telugu Speech to English Translation",
    page_icon="🎤",
    layout="centered"
)

# Initialize session state
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'transcription' not in st.session_state:
    st.session_state.transcription = ""
if 'translation' not in st.session_state:
    st.session_state.translation = ""

# Title and description
st.title("🎤 Telugu Speech to English Translation")
st.markdown("""
This app allows you to:
1. Record audio in Telugu
2. Transcribe it to Telugu text
3. Translate it to English

**Note:** Make sure to set your Sarvam AI API key in the sidebar.
""")

# Sidebar for API configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input(
        "Sarvam AI API Key",
        type="password",
        help="Get your API key from Sarvam AI platform"
    )
    
    if api_key:
        os.environ['SARVAM_API_KEY'] = api_key
        st.success("API Key configured!")
    else:
        st.warning("Please enter your Sarvam AI API key")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎙️ Record Audio")
    
    # Audio recorder component
    audio_recorder = AudioRecorder()
    audio_data = audio_recorder.record()
    
    if audio_data:
        st.session_state.audio_data = audio_data
        st.success("Audio recorded successfully!")
        
        # Play recorded audio
        st.audio(audio_data, format='audio/wav')

with col2:
    st.subheader("📝 Process Audio")
    
    if st.button("🔄 Transcribe & Translate", type="primary", disabled=not api_key):
        if st.session_state.audio_data:
            try:
                with st.spinner("Processing audio..."):
                    # Initialize Sarvam client
                    client = SarvamAIClient(api_key)
                    
                    # Save audio to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                        tmp_file.write(st.session_state.audio_data)
                        audio_path = tmp_file.name
                    
                    # Transcribe audio
                    with st.spinner("Transcribing Telugu audio..."):
                        transcription = client.transcribe_audio(audio_path, language="te")
                        st.session_state.transcription = transcription
                    
                    # Translate to English
                    if transcription:
                        with st.spinner("Translating to English..."):
                            translation = client.translate_text(
                                transcription, 
                                source_lang="te", 
                                target_lang="en"
                            )
                            st.session_state.translation = translation
                    
                    # Clean up temporary file
                    os.unlink(audio_path)
                    
            except Exception as e:
                st.error(f"Error processing audio: {str(e)}")
        else:
            st.warning("Please record audio first!")

# Display results
st.markdown("---")

col3, col4 = st.columns([1, 1])

with col3:
    st.subheader("🔤 Telugu Transcription")
    if st.session_state.transcription:
        st.text_area(
            "Telugu Text",
            value=st.session_state.transcription,
            height=150,
            disabled=True
        )
    else:
        st.info("Transcription will appear here")

with col4:
    st.subheader("🌐 English Translation")
    if st.session_state.translation:
        st.text_area(
            "English Text",
            value=st.session_state.translation,
            height=150,
            disabled=True
        )
    else:
        st.info("Translation will appear here")

# Clear button
if st.button("🗑️ Clear All"):
    st.session_state.audio_data = None
    st.session_state.transcription = ""
    st.session_state.translation = ""
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ using Streamlit and Sarvam AI</p>
</div>
""", unsafe_allow_html=True)