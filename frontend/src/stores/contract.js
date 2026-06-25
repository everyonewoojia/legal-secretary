import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as contractApi from '../api/contract'
import { chatStream } from '../api'

export const useContractStore = defineStore('contract', () => {
  const contractType = ref('tech_service')
  const sessionId = ref(null)
  const messages = ref([])
  const slots = ref({})
  const draftId = ref(null)
  const currentDraft = ref('')
  const generating = ref(false)

  const contractTypeMap = {
    tech_service: '技术服务合同',
    procurement: '采购合同',
    employment: '劳动合同',
    cooperation: '合作协议',
    non_disclosure: '保密协议',
  }

  function getContractLabel(type) {
    return contractTypeMap[type] || type
  }

  async function startSession(type) {
    contractType.value = type
    const res = await contractApi.createSession(type)
    if (res.code === 0) {
      sessionId.value = res.data.session_id
      slots.value = res.data.slots || {}
      const content = res.data.next_question || '您好，请告诉我合同相关信息。'
      messages.value = [{ role: 'agent', content }]
      draftId.value = null
      currentDraft.value = ''
    }
    return res
  }

  function sendMessage(text) {
    return new Promise((resolve, reject) => {
      const userMsg = { role: 'user', content: text }
      const aiMsg = { role: 'agent', content: '', loading: true }
      messages.value.push(userMsg, aiMsg)

      const lastAi = messages.value[messages.value.length - 1]

      chatStream(
        sessionId.value,
        text,
        (chunk) => {
          if (chunk.startsWith('{')) {
            try {
              const parsed = JSON.parse(chunk)
              if (parsed.content) lastAi.content += parsed.content
              if (parsed.slots) {
                slots.value = { ...slots.value, ...parsed.slots }
              }
              return
            } catch {
            }
          }
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
        () => messages.value,
      )
    })
  }

  async function generateContract() {
    generating.value = true
    try {
      const res = await contractApi.generateContract(sessionId.value)
      if (res.code === 0) {
        draftId.value = res.data.draft_id
        currentDraft.value = res.data.contract_text
        messages.value.push({ role: 'agent', content: '✅ 合同已生成，请在右侧预览。' })
      }
      return res
    } finally {
      generating.value = false
    }
  }

  function updateSlots(newSlots) {
    slots.value = { ...slots.value, ...newSlots }
  }

  function clearSession() {
    sessionId.value = null
    messages.value = []
    slots.value = {}
    draftId.value = null
    currentDraft.value = ''
  }

  return {
    contractType,
    sessionId,
    messages,
    slots,
    draftId,
    currentDraft,
    generating,
    getContractLabel,
    startSession,
    sendMessage,
    generateContract,
    updateSlots,
    clearSession,
  }
})
