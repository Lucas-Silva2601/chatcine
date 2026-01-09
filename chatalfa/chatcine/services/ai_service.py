"""
Serviço para integração com APIs de IA (Groq).
"""
import os
import json
from typing import Optional, List, Dict, Any
from groq import Groq
from PIL import Image
import base64
from io import BytesIO

from ..core.constants import SYSTEM_PROMPT
from ..core.exceptions import ExternalAPIError


class AIService:
    """Serviço para comunicação com APIs de IA."""
    
    def __init__(self):
        """Inicializa o serviço de IA."""
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                # Se houver erro na inicialização, permite continuar sem cliente
                print(f"⚠️  Aviso: Erro ao inicializar Groq: {e}")
                self.client = None
        else:
            self.client = None
    
    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado."""
        return bool(self.api_key and self.client)
    
    def _encode_image(self, image_file) -> str:
        """Codifica imagem em base64."""
        image = Image.open(image_file.stream)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def generate_response(
        self,
        user_message: str,
        image_file: Optional[Any] = None,
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Gera resposta da IA usando Groq.
        
        Args:
            user_message: Mensagem do usuário
            image_file: Arquivo de imagem opcional
            chat_history: Histórico de conversa
            
        Returns:
            Resposta da IA como string JSON
        """
        if not self.is_configured():
            raise ExternalAPIError("GROQ_API_KEY não configurada.")
        
        # Prepara mensagens para o chat
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Adiciona histórico de conversa
        if chat_history:
            for message in chat_history[-6:]:
                if message["role"] == "user":
                    messages.append({"role": "user", "content": message['content']})
                elif message["role"] == "assistant":
                    content = message.get('content', '')
                    if isinstance(content, dict):
                        content = json.dumps(content)
                    messages.append({"role": "assistant", "content": str(content)})
        
        # Adiciona mensagem atual
        # Nota: Groq ainda não tem suporte completo para visão, então apenas texto por enquanto
        if image_file:
            # Para imagens, informa ao usuário que precisa descrever
            messages.append({
                "role": "user", 
                "content": f"{user_message}\n\n[O usuário enviou uma imagem. Descreva o que você vê ou identifique o filme baseado na descrição fornecida.]"
            })
        else:
            messages.append({"role": "user", "content": user_message})
        
        # Usa o modelo mais recente e poderoso do Groq
        model = "llama-3.3-70b-versatile"
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise ExternalAPIError(f"Erro na API do Groq: {str(e)}")
    
    def clean_json_response(self, text: str) -> Optional[str]:
        """
        Limpa e extrai JSON de uma string.
        
        Args:
            text: String que pode conter JSON
            
        Returns:
            String JSON válida ou None
        """
        # Remove markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].strip()
        if "```" in text:
            text = text.split("```")[0].strip()
        
        # Extrai JSON
        try:
            match_start = text.find('{')
            if match_start == -1:
                return None
            
            open_braces = 0
            last_brace_index = -1
            for i in range(match_start, len(text)):
                if text[i] == '{':
                    open_braces += 1
                elif text[i] == '}':
                    open_braces -= 1
                    if open_braces == 0:
                        last_brace_index = i
                        break
            
            if last_brace_index != -1:
                potential_json = text[match_start:last_brace_index+1]
                json.loads(potential_json)  # Valida
                return potential_json
        except (json.JSONDecodeError, IndexError):
            return None
        
        return None
