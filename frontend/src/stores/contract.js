import { defineStore } from 'pinia'
import { ref } from 'vue'
import { contractApi } from '../api/contract'
import { chatStream, generateStream } from '../api'

const SLOT_KEYWORDS = {
  '甲方': ['甲方', '委托方', '买方', '采购方'],
  '乙方': ['乙方', '受托方', '服务方', '卖方', '销售方', '姓名', '名字'],
  '合同金额': ['金额', '总价', '合同额', '报价', '总金额'],
  '交付物': ['交付物', '交付内容', '开发内容', '服务内容', '交付'],
  '付款方式': ['付款', '支付', '一次性', '分期', '分阶段', '分次'],
  '交付期限': ['期限', '时间', '工作日', '交付时间', '交付期限'],
  '违约金比例': ['违约金', '违约', '比例', '%', '百分之'],
  '用人单位': ['用人单位', '雇主', '公司全称', '单位名称'],
  '法定代表人': ['法定代表人', '法人代表'],
  '劳动者': ['劳动者', '员工', '雇员'],
  '身份证号': ['身份证', '身份证号', '身份证号码'],
  '联系电话': ['联系电话', '手机号', '电话'],
  '合同期限': ['合同期限', '期限类型', '固定期限', '无固定期限'],
  '试用期': ['试用期'],
  '岗位': ['岗位', '职位', '职务'],
  '工作地点': ['工作地点', '工作地', '上班地点'],
  '工时制度': ['工时', '工时制度', '工作时间制度'],
  '基本工资': ['基本工资', '底薪'],
  '发薪日': ['发薪', '发薪日', '发放日'],
  '社保': ['社保', '五险', '社会保险'],
  '竞业限制': ['竞业', '竞业限制'],
  '劳动仲裁': ['劳动仲裁', '仲裁委员会'],
}


function saveContractState(code, messages, slots, draftId, currentDraft) {
  try {
    const data = {
      messages: messages.map((m) => ({ ...m, loading: false })),
      slots: { ...slots },
      draftId,
      currentDraft,
    }
    localStorage.setItem('contract_' + code, JSON.stringify(data))
  } catch (e) {
    console.warn('saveContractState failed:', e)
  }
}

function loadContractState(code) {
  try {
    const raw = localStorage.getItem('contract_' + code)
    return raw ? JSON.parse(raw) : null
  } catch (e) {
    console.warn('loadContractState failed:', e)
    return null
  }
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
      const persisted = loadContractState(code)
      if (persisted) {
        messages.value = persisted.messages
        slots.value = persisted.slots
        draftId.value = persisted.draftId
        currentDraft.value = persisted.currentDraft
      } else {
        messages.value = [{ role: 'agent', content: '您好！我是法务小秘的合同助手。请告诉我合同的基本信息，例如甲方/乙方的名称，以及您希望起草的合同涉及的主要内容。' }]
        slots.value = {}
        draftId.value = null
        currentDraft.value = ''
      }
    }
  }

  function sendMessage(text) {
    return new Promise((resolve, reject) => {
      const currentCode = contractCode.value

      const userMsg = { role: 'user', content: text }
      const aiMsg = { role: 'agent', content: '', loading: true }
      messages.value.push(userMsg, aiMsg)

      const lastAi = messages.value[messages.value.length - 1]

      let slotUpdated = false
      function extractAllSlots(userText) {
        const matches = []
        for (const [slot, keywords] of Object.entries(SLOT_KEYWORDS)) {
          for (const kw of keywords) {
            if (kw.length < 2) continue
            let idx = userText.indexOf(kw)
            while (idx !== -1) {
              matches.push({ slot, start: idx, end: idx + kw.length, len: kw.length })
              idx = userText.indexOf(kw, idx + 1)
            }
          }
        }
        if (!matches.length) return
        matches.sort((a, b) => a.start - b.start || b.len - a.len)
        const kept = []
        for (const m of matches) {
          const overlap = kept.some(k => m.start < k.end && m.end > k.start)
          if (!overlap) kept.push(m)
        }
        kept.sort((a, b) => a.start - b.start)
        for (let i = 0; i < kept.length; i++) {
          const m = kept[i]
          const nextStart = i + 1 < kept.length ? kept[i + 1].start : userText.length
          let val = userText.substring(m.end, nextStart).trim()
          val = val.replace(/^[是：:，,]+/, '').replace(/[，,、和及]+$/, '').trim()
          if (val) slots.value = { ...slots.value, [m.slot]: val }
        }
      }
      chatStream(
        typeId.value,
        text,
        (chunk) => {
          if (typeof chunk === 'object' && chunk.content !== undefined) {
            if (!slotUpdated && chunk.content.trim()) {
              extractAllSlots(text)
              slotUpdated = true
            }
            lastAi.content += chunk.content
            if (chunk.slots) {
              slots.value = { ...slots.value, ...chunk.slots }
            }
          } else if (typeof chunk === 'string') {
            if (!slotUpdated && chunk.trim()) {
              extractAllSlots(text)
              slotUpdated = true
            }
            lastAi.content += chunk
          }
        },
        () => {
          lastAi.loading = false
          saveContractState(currentCode, messages.value, slots.value, draftId.value, currentDraft.value)
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
    if (generating.value) return { code: -1, message: '正在生成中' }
    currentDraft.value = ''
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
            saveContractState(contractCode.value, messages.value, slots.value, draftId.value, currentDraft.value)
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
    saveContractState(contractCode.value, messages.value, slots.value, draftId.value, currentDraft.value)
  }

  function clearSession() {
    typeId.value = null
    contractCode.value = 'tech_service'
    messages.value = []
    slots.value = {}
    draftId.value = null
    currentDraft.value = ''
    sessions.value = {}
    try { localStorage.removeItem('contract_tech_service') } catch {}
    try { localStorage.removeItem('contract_procurement') } catch {}
    try { localStorage.removeItem('contract_employment') } catch {}
    try { localStorage.removeItem('contract_cooperation') } catch {}
    try { localStorage.removeItem('contract_non_disclosure') } catch {}
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
