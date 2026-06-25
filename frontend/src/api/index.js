import axios from 'axios'
import { mockChatStream } from './mock/contractMock'

const http = axios.create({ baseURL: '/api/v1' })

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err.response?.data?.message || err.message || '请求失败'
    return Promise.reject(new Error(msg))
  },
)

export default http

export const auth = {
  login: (phone, password) => http.post('/auth/login', { phone, password }),
  register: (data) => http.post('/auth/register', data),
}

export const rag = {
  search: (query, contractType = '') =>
    http.post('/rag/search', { query, contract_type: contractType }),
}

export function chatStream(sessionId, message, onChunk, onDone, onError, getMessages) {
  return mockChatStream(sessionId, message, onChunk, onDone, onError, getMessages)
}
