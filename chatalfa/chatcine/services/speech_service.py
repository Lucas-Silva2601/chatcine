"""
Serviço para transcrição de áudio.
"""
import os
from google.cloud import speech
from typing import Optional

from ..core.exceptions import ExternalAPIError


class SpeechService:
    """Serviço para transcrição de áudio."""
    
    def __init__(self):
        """Inicializa o serviço de transcrição."""
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado."""
        return bool(self.credentials_path and os.path.exists(self.credentials_path))
    
    def transcribe_audio(self, audio_file) -> Optional[str]:
        """
        Transcreve um arquivo de áudio.
        
        Args:
            audio_file: Arquivo de áudio (FileStorage)
            
        Returns:
            Texto transcrito ou None em caso de erro
        """
        if not self.is_configured():
            raise ExternalAPIError("Credenciais do Google Cloud Speech não configuradas.")
        
        try:
            client = speech.SpeechClient()
            content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                language_code="pt-BR",
                enable_automatic_punctuation=True
            )
            
            response = client.recognize(config=config, audio=audio)
            
            if response.results:
                return response.results[0].alternatives[0].transcript
            return None
        except Exception as e:
            raise ExternalAPIError(f"Erro ao processar áudio: {str(e)}")

