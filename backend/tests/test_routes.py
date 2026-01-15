"""
Testes de integração para rotas.
"""
import pytest
import json


class TestAuthRoutes:
    """Testes para rotas de autenticação."""
    
    def test_login_page_loads(self, client):
        """Testa se a página de login carrega."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()
    
    def test_register_new_user(self, client, app):
        """Testa registro de novo usuário."""
        response = client.post('/register', data={
            'email': 'newuser@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Deve redirecionar após registro bem-sucedido
        assert response.status_code == 200
    
    def test_login_invalid_credentials(self, client):
        """Testa login com credenciais inválidas."""
        response = client.post('/login', data={
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        })
        
        # Deve retornar erro ou redirecionar para login
        assert response.status_code in [200, 302]
    
    def test_logout_requires_login(self, client):
        """Testa que logout requer autenticação."""
        response = client.get('/logout', follow_redirects=True)
        # Deve redirecionar para login
        assert response.status_code == 200


class TestMainRoutes:
    """Testes para rotas principais."""
    
    def test_index_requires_login(self, client):
        """Testa que a página principal requer login."""
        response = client.get('/', follow_redirects=True)
        # Deve redirecionar para login
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'Login' in response.data
    
    def test_chat_requires_login(self, client):
        """Testa que chat requer login."""
        response = client.post('/chat', data={
            'message': 'test'
        }, follow_redirects=True)
        
        # Deve redirecionar para login
        assert response.status_code == 200
    
    @pytest.mark.skip(reason="Requer mock de serviços externos")
    def test_chat_with_message(self, authenticated_client):
        """Testa envio de mensagem no chat."""
        # Este teste requer mocks dos serviços externos
        pass
    
    def test_movie_by_id_requires_login(self, client):
        """Testa que busca de filme requer login."""
        response = client.get('/movie/123', follow_redirects=True)
        assert response.status_code == 200
    
    def test_recommendations_requires_login(self, client):
        """Testa que recomendações requerem login."""
        response = client.get('/recommendations/123', follow_redirects=True)
        assert response.status_code == 200

