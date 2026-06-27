import {
  mockCreateSession,
  mockGenerateContract,
  mockExportDraft,
} from './mock/contractMock'

export async function createSession(contractType) {
  return mockCreateSession(contractType)
}

export async function generateContract(sessionId) {
  return mockGenerateContract(sessionId)
}

export async function exportDraft(draftId, format = 'docx') {
  return mockExportDraft(draftId)
}
