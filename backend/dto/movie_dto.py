"""
DTOs para operações com filmes.
"""
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class MovieDTO:
    """DTO para informações de filme."""
    id: int
    title: str
    year: str
    poster_url: Optional[str] = None
    genres: Optional[str] = None
    rating: Optional[str] = None
    overview: Optional[str] = None
    imdb_id: Optional[str] = None
    media_type: str = "movie"
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'poster_url': self.poster_url,
            'genres': self.genres,
            'rating': self.rating,
            'overview': self.overview,
            'imdb_id': self.imdb_id,
            'media_type': self.media_type
        }


@dataclass
class RecommendationDTO:
    """DTO para recomendação de filme."""
    id: int
    title: str
    year: str
    poster_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'poster_url': self.poster_url
        }


@dataclass
class RecommendationsDTO:
    """DTO para lista de recomendações."""
    recommendations: List[RecommendationDTO]
    
    def to_list(self) -> List[dict]:
        """Converte para lista de dicionários."""
        return [rec.to_dict() for rec in self.recommendations]

