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
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      window.location.href = '/login'
      return Promise.reject(new Error('登录已过期'))
    }
    const body = err.response?.data
    const msg = body?.message || body?.detail || err.message || '请求失败'
    return Promise.reject(new Error(msg))
  },
)

function getToken() {
  return localStorage.getItem('token') || ''
}

async function sseFetch(path, body, onChunk, onDone, onError, signal) {
  try {
    const token = getToken()
    const res = await fetch(`/api/v1${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body),
      signal,
    })

    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        window.location.href = '/login'
        onError?.('登录已过期')
        return
      }
      const errBody = await res.text()
      let msg = '请求失败'
      try {
        const parsed = JSON.parse(errBody)
        msg = parsed.message || msg
      } catch {}
      onError?.(msg)
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
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim()
          if (data === '[DONE]') {
            onDone?.()
            return
          }
          try {
            const parsed = JSON.parse(data)
            onChunk(parsed)
          } catch {
            onChunk(data)
          }
        } else if (line.trim()) {
          onChunk(line)
        }
      }
    }

    if (buffer.startsWith('data: ')) {
      const data = buffer.slice(6).trim()
      if (data === '[DONE]') {
        onDone?.()
        return
      }
      try {
        const parsed = JSON.parse(data)
        onChunk(parsed)
      } catch (e) {
        onChunk(data)
      }
    }

    onDone?.()
  } catch (err) {
    onError?.(err.message || '网络请求失败')
  }
}

export function chatStream(typeId, message, onChunk, onDone, onError, getMessages, slotKey) {
  const history = getMessages ? getMessages().filter((m) => m.role !== 'system').map((m) => ({ role: m.role, content: m.content })) : []
  const body = { message, history }
  if (slotKey) body.slotKey = slotKey

  let cancelled = false
  const controller = new AbortController()

  sseFetch(
    `/contracts/chat/${typeId}`,
    body,
    (chunk) => {
      if (cancelled) return
      onChunk(chunk)
    },
    () => {
      if (cancelled) return
      cancelled = true
      onDone?.()
    },
    (err) => {
      if (cancelled) return
      cancelled = true
      onError?.(err)
    },
    controller.signal,
  )

  return () => { cancelled = true; controller.abort() }
}

export function generateStream(typeId, collectedFields, title, onChunk, onDone, onError) {
  let contractId = null
  let cancelled = false
  const controller = new AbortController()
  const timer = setTimeout(() => { cancelled = true; controller.abort(); onError?.('生成超时') }, 120000)

  sseFetch(
    `/contracts/generate-stream/${typeId}`,
    { collected_fields: collectedFields, title: title || '' },
    (data) => {
      if (cancelled) return
      if (data.error) {
        cancelled = true
        clearTimeout(timer)
        onError?.(data.error)
        return
      }
      if (data.done && data.contract_id) {
        contractId = data.contract_id
        clearTimeout(timer)
        onDone?.(contractId)
        return
      }
      onChunk(data.content || '')
    },
    () => {
      if (cancelled) return
      cancelled = true
      clearTimeout(timer)
      if (!contractId) onDone?.(null)
    },
    (err) => {
      if (cancelled) return
      cancelled = true
      clearTimeout(timer)
      onError?.(err)
    },
    controller.signal,
  )

  return () => { cancelled = true; clearTimeout(timer); controller.abort() }
}

export default http
