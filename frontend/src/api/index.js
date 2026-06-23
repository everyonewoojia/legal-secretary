const BASE_URL = '/api/v1'

async function request(url, options = {}) {
  const token = localStorage.getItem('token')
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE_URL}${url}`, { ...options, headers })
  return res.json()
}

export const auth = {
  login: (phone, password) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ phone, password }) }),
  register: (data) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
}

export const contract = {
  createSession: (contractType) =>
    request('/contract/session', { method: 'POST', body: JSON.stringify({ contract_type: contractType }) }),
  generate: (sessionId) =>
    request('/contract/generate', { method: 'POST', body: JSON.stringify({ session_id: sessionId }) }),
  export: (draftId, format = 'docx') =>
    request(`/contract/${draftId}/export?format=${format}`),
  analyze: (draftId, modifiedText, contractType) =>
    request('/contract/negotiate/analyze', {
      method: 'POST',
      body: JSON.stringify({ draft_id: draftId, modified_text: modifiedText, contract_type: contractType }),
    }),
}

export const rag = {
  search: (query, contractType = '') =>
    request('/rag/search', { method: 'POST', body: JSON.stringify({ query, contract_type: contractType }) }),
}
