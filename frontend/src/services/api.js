import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptores desabilitados temporariamente para testes
// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem('auth-storage')
//   if (token) {
//     try {
//       const { state } = JSON.parse(token)
//       if (state?.token) {
//         config.headers.Authorization = `Bearer ${state.token}`
//       }
//     } catch (error) {
//       console.error('Error parsing token:', error)
//     }
//   }
//   return config
// })

// api.interceptors.response.use(
//   (response) => response,
//   (error) => {
//     if (error.response?.status === 401) {
//       localStorage.removeItem('auth-storage')
//       window.location.href = '/login'
//     }
//     return Promise.reject(error)
//   }
// )

export default api

