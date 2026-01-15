"""
Serviço para integração com API TMDB.
"""
import os
import requests
from typing import Optional, List

from dto.movie_dto import MovieDTO, RecommendationDTO, RecommendationsDTO
from core.exceptions import ExternalAPIError, NotFoundError


class MovieService:
    """Serviço para buscar informações de filmes."""
    
    def __init__(self):
        """Inicializa o serviço de filmes."""
        self.api_key = os.getenv("TMDB_API_KEY")
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
    
    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado."""
        return bool(self.api_key)
    
    def search_movie(self, movie_name: str) -> Optional[MovieDTO]:
        """
        Busca informações de um filme pelo nome.
        
        Args:
            movie_name: Nome do filme
            
        Returns:
            MovieDTO ou None se não encontrado
        """
        if not self.is_configured():
            raise ExternalAPIError("TMDB_API_KEY não configurada.")
        
        try:
            search_url = f"{self.base_url}/search/multi"
            params = {
                'api_key': self.api_key,
                'query': movie_name,
                'language': 'pt-BR'
            }
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                print("⚠️ Nenhum resultado encontrado na busca")
                return None
            
            first_result = data["results"][0]
            media_type = first_result.get("media_type")
            
            print(f"🔍 Resultado encontrado: {first_result.get('title') or first_result.get('name')} (ID: {first_result.get('id')}, Tipo: {media_type})")
            print(f"🖼️ Poster path no resultado da busca: {first_result.get('poster_path')}")
            
            if media_type not in ["movie", "tv"]:
                print(f"⚠️ Tipo de mídia não suportado: {media_type}")
                return None
            
            return self.get_movie_by_id(first_result["id"], media_type)
        except requests.exceptions.RequestException as e:
            raise ExternalAPIError(f"Erro ao buscar no TMDB: {str(e)}")
    
    def get_movie_by_id(self, movie_id: int, media_type: str = "movie") -> Optional[MovieDTO]:
        """
        Busca detalhes de um filme pelo ID.
        
        Args:
            movie_id: ID do filme no TMDB
            media_type: Tipo de mídia ('movie' ou 'tv')
            
        Returns:
            MovieDTO ou None se não encontrado
        """
        if not self.is_configured():
            raise ExternalAPIError("TMDB_API_KEY não configurada.")
        
        try:
            details_url = f"{self.base_url}/{media_type}/{movie_id}"
            params = {
                'api_key': self.api_key,
                'language': 'pt-BR',
                'append_to_response': 'external_ids'
            }
            response = requests.get(details_url, params=params, timeout=10)
            response.raise_for_status()
            item = response.json()
            
            print(f"📥 Resposta completa da API TMDB (primeiros campos): {list(item.keys())[:10]}")
            
            title = item.get("title") if media_type == "movie" else item.get("name", "Desconhecido")
            release_date = item.get("release_date") if media_type == "movie" else item.get("first_air_date", "")
            year = release_date[:4] if release_date else "N/A"
            
            poster_path = item.get("poster_path")
            print(f"🖼️ Poster path retornado pela API: {poster_path} (tipo: {type(poster_path)})")
            
            poster_url = None
            if poster_path:
                # O TMDB retorna poster_path com barra inicial (ex: "/abc123.jpg")
                # e image_base_url já termina com "/t/p/w500", então concatenamos diretamente
                poster_url = f"{self.image_base_url}{poster_path}"
                print(f"✅ Poster URL construída: {poster_url}")  # Debug
            else:
                print(f"❌ Poster path não encontrado para: {title}")  # Debug
                print(f"📋 Campos disponíveis no item: {list(item.keys())}")
            
            movie_dto = MovieDTO(
                id=item.get("id"),
                title=title,
                year=year,
                poster_url=poster_url,
                genres=", ".join([g["name"] for g in item.get("genres", [])]) or "Não disponível",
                rating=f"{item.get('vote_average', 0):.1f}/10",
                overview=item.get("overview") or "Sinopse não disponível.",
                imdb_id=item.get("external_ids", {}).get("imdb_id"),
                media_type=media_type
            )
            movie_dict = movie_dto.to_dict()
            print(f"📦 MovieDTO criado: {movie_dict}")  # Debug
            print(f"🔍 Poster URL no dict: {movie_dict.get('poster_url')}")  # Debug
            return movie_dto
        except requests.exceptions.RequestException as e:
            raise ExternalAPIError(f"Erro ao buscar detalhes no TMDB: {str(e)}")
    
    def get_recommendations(self, movie_id: int, media_type: str = "movie") -> RecommendationsDTO:
        """
        Busca recomendações baseadas em um filme.
        
        Args:
            movie_id: ID do filme
            media_type: Tipo de mídia
            
        Returns:
            RecommendationsDTO com lista de recomendações
        """
        if not self.is_configured():
            raise ExternalAPIError("TMDB_API_KEY não configurada.")
        
        try:
            url = f"{self.base_url}/{media_type}/{movie_id}/recommendations"
            params = {
                'api_key': self.api_key,
                'language': 'pt-BR',
                'page': 1
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            recommendations = []
            for rec in data.get("results", [])[:5]:
                poster_path = rec.get("poster_path")
                rec_media_type = rec.get("media_type", media_type)
                
                poster_url = None
                if poster_path:
                    # O TMDB retorna poster_path com barra inicial (ex: "/abc123.jpg")
                    # e image_base_url já termina com "/t/p/w500", então concatenamos diretamente
                    poster_url = f"{self.image_base_url}{poster_path}"
                
                recommendations.append(RecommendationDTO(
                    id=rec.get("id"),
                    title=rec.get("title") if rec_media_type == "movie" else rec.get("name", "Desconhecido"),
                    year=(rec.get("release_date") or rec.get("first_air_date", ""))[:4],
                    poster_url=poster_url
                ))
            
            return RecommendationsDTO(recommendations=recommendations)
        except requests.exceptions.RequestException as e:
            raise ExternalAPIError(f"Erro ao buscar recomendações no TMDB: {str(e)}")

