import axios from 'axios'

// A API roda no mesmo servidor Next.js (app/api/*), então usamos um caminho
// relativo. NEXT_PUBLIC_API_URL continua permitindo apontar para outro host.
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api'

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

