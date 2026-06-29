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

export async function fetchContractTypes() {
  try {
    const res = await http.get('/contract/type')
    if (res?.code === 0) return res.data || []
  } catch {
    // fallback
  }
  return [
    { id: 1, name: '技术服务合同', code: 'tech_service' },
    { id: 2, name: '采购合同', code: 'procurement' },
    { id: 3, name: '劳动合同', code: 'employment' },
    { id: 4, name: '合作协议', code: 'cooperation' },
    { id: 5, name: '保密协议', code: 'non_disclosure' },
  ]
}

export async function searchLawContext(query, contractType = '') {
  try {
    const res = await http.post('/rag/search', { query, contract_type: contractType, top_k: 5 })
    // 兼容后端是否带统一统一包装 data 层
    const targetData = res?.chunks ? res : res?.data;
    
    if (targetData?.chunks && Array.isArray(targetData.chunks)) {
      return targetData.chunks.map(c => `【依据文件：${c.source}】\n${c.content}`).join('\n\n')
    }
  } catch (error) {
    console.error("RAG 对齐解析失败:", error)
  }
  return '' // 失败时 fallback 变为空字符串
}
