"""
Testes unitários para serviços.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from chatcine import services


class TestServices:
    """Testes para funções de serviço."""
    
    @patch('chatcine.services.genai')
    def test_generate_gemini_response_text(self, mock_genai, app):
        """Testa geração de resposta da IA com texto."""
        with app.app_context():
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = '{"type": "text", "content": "Olá!"}'
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            response = services.generate_gemini_response("Olá")
            
            assert response is not None
            assert "type" in response or "text" in response.lower()
    
    def test_clean_json_response(self, app):
        """Testa limpeza de resposta JSON."""
        with app.app_context():
            # Teste com JSON válido
            valid_json = '{"type": "text", "content": "Teste"}'
            result = services.clean_json_response(valid_json)
            assert result == valid_json
            
            # Teste com markdown code block
            json_with_markdown = '```json\n{"type": "text", "content": "Teste"}\n```'
            result = services.clean_json_response(json_with_markdown)
            assert result is not None
            assert "type" in result
            
            # Teste com texto inválido
            invalid = "Não é JSON"
            result = services.clean_json_response(invalid)
            assert result is None
    
    @patch('chatcine.services.requests.get')
    def test_get_movie_info(self, mock_get, app):
        """Testa busca de informações de filme."""
        with app.app_context():
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "results": [{
                    "id": 123,
                    "media_type": "movie",
                    "title": "Test Movie",
                    "release_date": "2023-01-01"
                }]
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            # Mock get_movie_info_by_id também
            with patch('chatcine.services.get_movie_info_by_id') as mock_by_id:
                mock_by_id.return_value = {
                    "id": 123,
                    "title": "Test Movie",
                    "year": "2023"
                }
                
                result = services.get_movie_info("Test Movie")
                assert result is not None
                assert result["title"] == "Test Movie"

