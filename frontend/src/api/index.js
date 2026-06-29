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

export async function chatStream(sessionId, message, onChunk, onDone, onError, getMessages) {
  const token = localStorage.getItem('token')
  const history = typeof getMessages === 'function' ? getMessages() : []

  try {
    const resp = await fetch(`/api/v1/contracts/chat/${sessionId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message, history }),
    })

    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim()
          if (data === '[DONE]') {
            onDone()
            return
          }
          try {
            const parsed = JSON.parse(data)
            if (parsed.content) onChunk(parsed.content)
            if (parsed.slots && typeof onChunk === 'function') {
              onChunk(JSON.stringify({ slots: parsed.slots }))
            }
            if (parsed.done) onDone()
          } catch {
            onChunk(data)
          }
        }
      }
    }
    onDone()
  } catch {
    // Fallback to mock when backend is unavailable
    mockChatStream(sessionId, message, onChunk, onDone, onError, getMessages)
  }
}

export async function ragSearch(query, contractType = '') {
  try {
    const res = await rag.search(query, contractType)
    if (res?.code === 0 && res?.data?.chunks) {
      return res.data.chunks
    }
  } catch {
    // Silently fall back
  }
  return []
}
