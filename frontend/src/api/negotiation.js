import http from './index'

export const negotiationApi = {
  upload: (contractId, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return http.post(`/negotiation/upload/${contractId}`, fd)
  },

  getDiff: (contractId, versionA, versionB) =>
    http.get(`/negotiation/diff/${contractId}`, {
      params: { version_a: versionA, version_b: versionB },
    }),

  aiAnalyze: (contractId) => http.post(`/negotiation/ai-analyze/${contractId}`),

  getRisks: (contractId) => http.get(`/negotiation/risks/${contractId}`),

  counterArgument: (riskId, style = 'balanced') =>
    http.post('/negotiation/counter-argument', {
      risk_id: riskId,
      negotiation_style: style,
    }),
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
