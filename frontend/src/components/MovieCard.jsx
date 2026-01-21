import { useState } from 'react'
import { chatService } from '../services/chatService'
import '../styles/MovieCard.css'

function MovieCard({ movie }) {
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)

  const handleGetRecommendations = async () => {
    if (recommendations.length > 0) {
      setShowRecommendations(!showRecommendations)
      return
    }

    setLoading(true)
    try {
      const response = await chatService.getRecommendations(movie.id)
      setRecommendations(response.content || [])
      setShowRecommendations(true)
    } catch (error) {
      console.error('Erro ao buscar recomendações:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleWatchNow = () => {
    // Abre o IMDB ou outra plataforma de streaming
    if (movie.imdb_id) {
      window.open(`https://www.imdb.com/title/${movie.imdb_id}`, '_blank')
    } else {
      // Fallback para busca no Google
      const searchQuery = encodeURIComponent(`${movie.title} ${movie.year} assistir online`)
      window.open(`https://www.google.com/search?q=${searchQuery}`, '_blank')
    }
  }

  return (
    <div className="movie-card">
      <div className="movie-header">
        {movie.poster_url && (
          <img
            src={movie.poster_url}
            alt={movie.title}
            className="movie-poster"
          />
        )}
        <div className="movie-info">
          <h3>{movie.title}</h3>
          {movie.year && (
            <p className="movie-year">
              {movie.year}
            </p>
          )}
          {movie.rating && (
            <div className="movie-rating">
              ⭐ {movie.rating}
            </div>
          )}
        </div>
      </div>

      {movie.overview && (
        <div className="movie-overview">
          <p>{movie.overview}</p>
        </div>
      )}

      {movie.genres && (
        <div className="movie-genres">
          {movie.genres.split(', ').map((genre, index) => (
            <span key={index} className="genre-tag">
              {genre}
            </span>
          ))}
        </div>
      )}

      <div className="movie-actions">
        <button
          onClick={handleWatchNow}
          className="btn-watch-now"
        >
          🎬 Assistir Agora
        </button>
        <button
          onClick={handleGetRecommendations}
          className="btn-recommendations"
          disabled={loading}
        >
          {loading ? '⏳ Carregando...' : showRecommendations ? '🔼 Ocultar' : '🎯 Outras Recomendações'}
        </button>
      </div>

      {showRecommendations && recommendations.length > 0 && (
        <div className="recommendations-list">
          <h4>Você também pode gostar:</h4>
          <div className="recommendations-grid">
            {recommendations.map((rec, index) => (
              <div key={index} className="recommendation-item">
                {rec.poster_url && (
                  <img
                    src={rec.poster_url}
                    alt={rec.title}
                  />
                )}
                <div className="recommendation-info">
                  <h5>{rec.title}</h5>
                  {rec.year && (
                    <span className="rec-year">
                      {rec.year}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default MovieCard

