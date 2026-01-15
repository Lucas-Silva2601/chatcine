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
      console.error('Error fetching recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="movie-card">
      <div className="movie-header">
        {movie.poster_path && (
          <img
            src={`https://image.tmdb.org/t/p/w300${movie.poster_path}`}
            alt={movie.title}
            className="movie-poster"
          />
        )}
        <div className="movie-info">
          <h3>{movie.title}</h3>
          {movie.release_date && (
            <p className="movie-year">
              {new Date(movie.release_date).getFullYear()}
            </p>
          )}
          {movie.vote_average && (
            <div className="movie-rating">
              ⭐ {movie.vote_average.toFixed(1)}/10
            </div>
          )}
        </div>
      </div>

      {movie.overview && (
        <div className="movie-overview">
          <p>{movie.overview}</p>
        </div>
      )}

      {movie.genres && movie.genres.length > 0 && (
        <div className="movie-genres">
          {movie.genres.map((genre) => (
            <span key={genre.id} className="genre-tag">
              {genre.name}
            </span>
          ))}
        </div>
      )}

      <button
        onClick={handleGetRecommendations}
        className="btn-recommendations"
        disabled={loading}
      >
        {loading ? 'Carregando...' : showRecommendations ? 'Ocultar Recomendações' : 'Ver Recomendações'}
      </button>

      {showRecommendations && recommendations.length > 0 && (
        <div className="recommendations-list">
          <h4>Recomendações:</h4>
          <div className="recommendations-grid">
            {recommendations.map((rec, index) => (
              <div key={index} className="recommendation-item">
                {rec.poster_path && (
                  <img
                    src={`https://image.tmdb.org/t/p/w200${rec.poster_path}`}
                    alt={rec.title}
                  />
                )}
                <div className="recommendation-info">
                  <h5>{rec.title}</h5>
                  {rec.vote_average && (
                    <span className="rec-rating">
                      ⭐ {rec.vote_average.toFixed(1)}
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

