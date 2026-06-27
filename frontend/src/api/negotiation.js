import { mockAnalyzeNegotiation, mockExportReport } from './mock/negotiationMock'

export async function analyzeNegotiation(data) {
  return mockAnalyzeNegotiation(data)
}

export async function exportReport(caseId) {
  return mockExportReport(caseId)
}
