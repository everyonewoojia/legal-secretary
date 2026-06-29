import http from './index'
import {
  mockCreateSession,
  mockGenerateContract,
  mockExportDraft,
} from './mock/contractMock'

export async function createSession(contractType) {
  try {
    const res = await http.post('/contract/session', { contract_type: contractType })
    if (res?.code === 0) return res
  } catch {
    // fallback
  }
  return mockCreateSession(contractType)
}

export async function generateContract(sessionId,payload) {
  try {
    const res = await http.post(`/contract/generate/${sessionId}`, payload)
    if (res?.code === 0) return res
  } catch {
    // fallback
  }
  return mockGenerateContract(sessionId)
}

export async function exportDraft(draftId, format = 'docx') {
  try {
    const res = await http.get(`/contract/${draftId}/download?format=${format}`)
    if (res?.code === 0) return res
  } catch {
    // fallback
  }
  return mockExportDraft(draftId)
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
