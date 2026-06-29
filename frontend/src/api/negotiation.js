import http from './index'
import { mockAnalyzeNegotiation, mockExportReport } from './mock/negotiationMock'

export async function analyzeNegotiation(data) {
  try {
    const res = await http.post('/negotiation/analyze', data)
    if (res?.code === 0) return res
  } catch {
    // fallback to mock
  }
  return mockAnalyzeNegotiation(data)
}

export async function exportReport(caseId) {
  try {
    const res = await http.get(`/negotiation/report/${caseId}`)
    if (res?.code === 0) return res
  } catch {
    // fallback to mock
  }
  return mockExportReport(caseId)
}

export async function fetchRiskContext(query) {
  try {
    const res = await http.post('/rag/search', { query, top_k: 3 })
    const target = res?.chunks ? res : res?.data;
    if (target?.chunks && Array.isArray(target.chunks)) {
      return target.chunks.map(c => `[${c.source}] ${c.content}`).join('\n\n')
    }
  } catch {
    // fallback
  }
  return ''
}
