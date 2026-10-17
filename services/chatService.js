import api from './api'

export const chatService = {
  sendMessage: async (message, file = null) => {
    const formData = new FormData()
    formData.append('message', message)
    if (file) {
      formData.append('file', file)
    }

    const response = await api.post('/chat', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getMovieById: async (movieId) => {
    const response = await api.get(`/movie/${movieId}`)
    return response.data
  },

  getRecommendations: async (movieId) => {
    const response = await api.get(`/recommendations/${movieId}`)
    return response.data
  },
}

