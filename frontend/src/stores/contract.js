import { defineStore } from 'pinia'
import { ref } from 'vue'
import { contractApi } from '../api/contract'
import { chatStream, generateStream } from '../api'

export const useContractStore = defineStore('contract', () => {
  const contractTypes = ref([])
  const typeId = ref(null)
  const contractCode = ref('tech_service')
  const messages = ref([])
  const slots = ref({})
  const draftId = ref(null)
  const currentDraft = ref('')
  const generating = ref(false)
  const typesLoaded = ref(false)
  const sessions = ref({})

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

  async function fetchTypes() {
    if (typesLoaded.value) return
    try {
      const res = await contractApi.getTypes()
      if (res.code === 0 && res.data?.length) {
        contractTypes.value = res.data
        typesLoaded.value = true
      }
    } catch {
      contractTypes.value = Object.entries(contractTypeMap).map(([code, name], i) => ({
        id: i + 1,
        code,
        name,
        description: '',
        sort_order: i + 1,
      }))
      typesLoaded.value = true
    }
  }

  function getTypeId(code) {
    const t = contractTypes.value.find((c) => c.code === code)
    return t ? t.id : 1
  }

  function getTypeCode(id) {
    const t = contractTypes.value.find((c) => c.id === id)
    return t ? t.code : 'tech_service'
  }

  async function startSession(code) {
    await fetchTypes()
    const prev = contractCode.value
    if (prev && prev !== code && messages.value.length) {
      sessions.value[prev] = {
        messages: messages.value.map((m) => ({ ...m })),
        slots: { ...slots.value },
        draftId: draftId.value,
        currentDraft: currentDraft.value,
      }
    }
    contractCode.value = code
    typeId.value = getTypeId(code)
    const saved = sessions.value[code]
    if (saved) {
      messages.value = saved.messages
      slots.value = saved.slots
      draftId.value = saved.draftId
      currentDraft.value = saved.currentDraft
    } else {
      messages.value = [{ role: 'agent', content: '您好！我是法务小秘的合同助手。请告诉我合同的基本信息，例如甲方/乙方的名称，以及您希望起草的合同涉及的主要内容。' }]
      slots.value = {}
      draftId.value = null
      currentDraft.value = ''
    }
  }

  function sendMessage(text) {
    return new Promise((resolve, reject) => {
      const userMsg = { role: 'user', content: text }
      const aiMsg = { role: 'agent', content: '', loading: true }
      messages.value.push(userMsg, aiMsg)

      const lastAi = messages.value[messages.value.length - 1]

      chatStream(
        typeId.value,
        text,
        (chunk) => {
          if (typeof chunk === 'object' && chunk.content !== undefined) {
            lastAi.content += chunk.content
            if (chunk.slots) {
              slots.value = { ...slots.value, ...chunk.slots }
            }
          } else if (typeof chunk === 'string') {
            lastAi.content += chunk
          }
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
      const title = contractTypeMap[contractCode.value] || '合同'
      return await new Promise((resolve, reject) => {
        generateStream(
          typeId.value,
          slots.value,
          title,
          (chunk) => {
            currentDraft.value += chunk
          },
          (id) => {
            draftId.value = id
            messages.value.push({ role: 'agent', content: '✅ 合同已生成，请在右侧预览。' })
            generating.value = false
            resolve({ code: 0, data: { draft_id: id, contract_text: currentDraft.value } })
          },
          (err) => {
            generating.value = false
            reject(new Error(err || '合同生成失败'))
          },
        )
      })
    } finally {
      if (generating.value) generating.value = false
    }
  }

  function updateSlots(newSlots) {
    slots.value = { ...slots.value, ...newSlots }
  }

  function clearSession() {
    typeId.value = null
    contractCode.value = 'tech_service'
    messages.value = []
    slots.value = {}
    draftId.value = null
    currentDraft.value = ''
    sessions.value = {}
  }

  return {
    contractTypes,
    typeId,
    contractCode,
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
    fetchTypes,
  }
})
