"""
Testes unitários para serviços.
"""
import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ai_service import AIService
from services.movie_service import MovieService


class TestServices:
    """Testes para funções de serviço."""
    
    def test_ai_service_initialization(self, app):
        """Testa inicialização do serviço de IA."""
        with app.app_context():
            ai_service = AIService()
            assert ai_service is not None
    
    def test_movie_service_initialization(self, app):
        """Testa inicialização do serviço de filmes."""
        with app.app_context():
            movie_service = MovieService()
            assert movie_service is not None

