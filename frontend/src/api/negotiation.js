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
