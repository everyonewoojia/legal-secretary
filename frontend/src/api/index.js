import axios from 'axios'

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

export const auth = {
  login: (phone, password) => http.post('/auth/login', { phone, password }),
  register: (data) => http.post('/auth/register', data),
}

export const contract = {
  createSession: (contractType) =>
    http.post('/contract/session', { contract_type: contractType }),

  generate: (sessionId) =>
    http.post('/contract/generate', { session_id: sessionId }),

  exportDraft: (draftId, format = 'docx') =>
    http.get(`/contract/${draftId}/export`, { params: { format } }),

  analyze: (draftId, modifiedText, contractType) =>
    http.post('/contract/negotiate/analyze', {
      draft_id: draftId,
      modified_text: modifiedText,
      contract_type: contractType,
    }),
}

export async function chatStream(sessionId, message, onChunk, onDone, onError) {
  const token = localStorage.getItem('token')
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  try {
    const res = await fetch('/api/v1/contract/chat/stream', {
      method: 'POST',
      headers,
      body: JSON.stringify({ session_id: sessionId, message }),
    })

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}))
      onError?.(errBody.message || `HTTP ${res.status}`)
      return
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || !trimmed.startsWith('data:')) continue
        const data = trimmed.slice(5).trim()
        if (data === '[DONE]') {
          onDone?.()
          return
        }
        onChunk?.(data)
      }
    }
    onDone?.()
  } catch (err) {
    onError?.(err.message || 'SSE 连接失败')
  }
}

export const rag = {
  search: (query, contractType = '') =>
    http.post('/rag/search', { query, contract_type: contractType }),
}
