import requests
import json
import base64
import os
from typing import Optional

class SarvamAIClient:
    """Client for Sarvam AI API interactions"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.sarvam.ai"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def transcribe_audio(self, audio_path: str, language: str = "te") -> Optional[str]:
        """
        Transcribe audio file to text using Sarvam AI
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: 'te' for Telugu)
            
        Returns:
            Transcribed text or None if error
        """
        try:
            # Read and encode audio file
            with open(audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Prepare request
            url = f"{self.base_url}/speech-to-text"
            payload = {
                "audio": audio_base64,
                "language": language,
                "model": "sarvam-1"  # Use appropriate model name
            }
            
            # Make request
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def translate_text(self, text: str, source_lang: str = "te", target_lang: str = "en") -> Optional[str]:
        """
        Translate text from source language to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text or None if error
        """
        try:
            # Prepare request
            url = f"{self.base_url}/translate"
            payload = {
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "model": "sarvam-translation-1"  # Use appropriate model name
            }
            
            # Make request
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("translated_text", "")
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")

# Alternative implementation using mock API for testing
class MockSarvamClient:
    """Mock client for testing without API key"""
    
    def transcribe_audio(self, audio_path: str, language: str = "te") -> str:
        """Mock transcription for testing"""
        return "నమస్తే, మీరు ఎలా ఉన్నారు? ఈ రోజు చాలా బాగుంది."
    
    def translate_text(self, text: str, source_lang: str = "te", target_lang: str = "en") -> str:
        """Mock translation for testing"""
        translations = {
            "నమస్తే, మీరు ఎలా ఉన్నారు? ఈ రోజు చాలా బాగుంది.": "Hello, how are you? Today is very nice."
        }
        return translations.get(text, "Hello, this is a test translation.")