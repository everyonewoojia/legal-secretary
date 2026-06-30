import http from './index'

export const contractApi = {
  getTypes: () => http.get('/contracts/types'),

  chat: (typeId, message, history = []) =>
    http.post(`/contracts/chat/${typeId}`, { message, history }),

  generate: (typeId, collectedFields, title = '') =>
    http.post(`/contracts/generate/${typeId}`, { collected_fields: collectedFields, title }),

  create: (typeId, title = '', content = '') =>
    http.post('/contracts/', { type_id: typeId, title, content }),

  list: (status) => http.get('/contracts/', { params: { status } }),

  get: (id) => http.get(`/contracts/${id}`),

  delete: (id) => http.delete(`/contracts/${id}`),

  download: (id, fmt = 'docx') =>
    http.get(`/contracts/${id}/download`, { params: { fmt } }),

  getVersions: (id) => http.get(`/contracts/${id}/versions`),

  getRisks: (id) => http.get(`/contracts/${id}/risks`),
}
