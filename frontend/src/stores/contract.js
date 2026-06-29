import { defineStore } from 'pinia'
import { ref } from 'vue'
import { contractApi } from '../api/contract'
import { chatStream, generateStream } from '../api'

const SLOT_KEYWORDS = {
  '甲方': ['甲方', '委托方', '买方', '采购方'],
  '乙方': ['乙方', '受托方', '服务方', '卖方', '销售方'],
  '合同金额': ['金额', '总价', '合同额', '报价', '总金额'],
  '交付物': ['交付物', '交付内容', '开发内容', '服务内容', '交付'],
  '付款方式': ['付款', '支付', '一次性', '分期', '分阶段', '分次'],
  '交付期限': ['期限', '时间', '天', '工作日', '周', '月', '交付时间'],
  '违约金比例': ['违约金', '违约', '比例', '%', '百分之'],
}

const SLOT_KEYS = Object.keys(SLOT_KEYWORDS)
const SLOT_QUESTIONS = {
  '甲方': '请问甲方',
  '乙方': '请问乙方',
  '合同金额': '合同总金额',
  '交付物': '交付物',
  '付款方式': '付款方式',
  '交付期限': '期限',
  '违约金比例': '违约金',
}

function detectSlot(text, messages) {
  if (SLOT_KEYS.some(k => text.startsWith(`${k}：`) || text.startsWith(`${k}:`))) {
    return null
  }
  for (const [slot, keywords] of Object.entries(SLOT_KEYWORDS)) {
    if (keywords.some(kw => text.includes(kw))) {
      return slot
    }
  }
  if (messages && messages.length) {
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i]
      if (m.role === 'agent' || m.role === 'assistant') {
        for (const [slot, qText] of Object.entries(SLOT_QUESTIONS)) {
          if (m.content.includes(qText)) {
            return slot
          }
        }
        break
      }
    }
  }
  return null
}

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
      const slotKey = detectSlot(text, messages.value)
      const enrichedText = slotKey ? `${slotKey}：${text}` : text

      const userMsg = { role: 'user', content: enrichedText }
      const aiMsg = { role: 'agent', content: '', loading: true }
      messages.value.push(userMsg, aiMsg)

      const lastAi = messages.value[messages.value.length - 1]

      chatStream(
        typeId.value,
        enrichedText,
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
        slotKey,
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
    detectSlot,
  }
})
