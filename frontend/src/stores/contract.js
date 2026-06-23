import { defineStore } from 'pinia'
import { ref } from 'vue'
import { contract as contractApi, chatStream } from '../api'

export const useContractStore = defineStore('contract', () => {
  const contractType = ref('tech_service')
  const sessionId = ref(null)
  const messages = ref([])
  const draftId = ref(null)
  const contractText = ref('')
  const generating = ref(false)

  async function startSession(type) {
    contractType.value = type
    const res = await contractApi.createSession(type)
    if (res.code === 0) {
      sessionId.value = res.data.session_id
      messages.value = [{ role: 'ai', content: res.data.next_question }]
      draftId.value = null
      contractText.value = ''
    }
    return res
  }

  function sendMessage(text) {
    return new Promise((resolve, reject) => {
      const userMsg = { role: 'user', content: text }
      const aiMsg = { role: 'ai', content: '', loading: true }
      messages.value.push(userMsg, aiMsg)

      const lastAi = messages.value[messages.value.length - 1]

      chatStream(
        sessionId.value,
        text,
        (chunk) => {
          lastAi.content += chunk
        },
        () => {
          lastAi.loading = false
          resolve()
        },
        (err) => {
          lastAi.content = err || '对话失败，请重试'
          lastAi.loading = false
          reject(new Error(err))
        },
      )
    })
  }

  async function generateContract() {
    generating.value = true
    try {
      const res = await contractApi.generate(sessionId.value)
      if (res.code === 0) {
        draftId.value = res.data.draft_id
        contractText.value = res.data.contract_text
        messages.value.push({ role: 'ai', content: '✅ 合同已生成，请在右侧预览。' })
      }
      return res
    } finally {
      generating.value = false
    }
  }

  function clearSession() {
    sessionId.value = null
    messages.value = []
    draftId.value = null
    contractText.value = ''
  }

  return {
    contractType, sessionId, messages, draftId, contractText, generating,
    startSession, sendMessage, generateContract, clearSession,
  }
})
