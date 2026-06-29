import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as negotiationApi from '../api/negotiation'
import { searchLawContext } from '../api/contract'

export const useNegotiationStore = defineStore('negotiation', () => {
  const caseId = ref(null)
  const diffList = ref([])
  const selectedRiskId = ref(null)
  const fileList = ref([])
  const modifiedText = ref('')
  const loading = ref(false)
  const version = ref('V1')
  const lawContext = ref('')

  const selectedRisk = computed(() => {
    if (!selectedRiskId.value) return null
    return diffList.value.find((item) => item.id === selectedRiskId.value) || null
  })

  function selectRisk(id) {
    selectedRiskId.value = id
  }

  async function submitAnalysis() {
    loading.value = true
    try {
      const formData = new FormData()

      if (fileList.value.length > 0) {
        fileList.value.forEach((f) => formData.append('file', f.raw))
      }
      if (modifiedText.value.trim()) {
        formData.append('modified_text', modifiedText.value.trim())
      }

      // 异步获取法律知识上下文（作为分析参考）
      const ragQuery = modifiedText.value.trim().slice(0, 100) || '合同风险分析'
      searchLawContext(ragQuery).then(contextStr => {
        lawContext.value = contextStr // 直接接收拼接好的字符串
      })

      const res = await negotiationApi.analyzeNegotiation(formData)
      if (res.code === 0) {
        caseId.value = res.data.case_id || 1
        diffList.value = res.data.risks || res.data.changes || res.data.diff_list || []
        version.value = res.data.version || 'V2'
        if (diffList.value.length > 0) {
          selectedRiskId.value = diffList.value[0].id
        }
      }
      return res
    } finally {
      loading.value = false
    }
  }

  function resetAnalysis() {
    caseId.value = null
    diffList.value = []
    selectedRiskId.value = null
    fileList.value = []
    modifiedText.value = ''
    version.value = 'V1'
  }

  return {
    caseId,
    diffList,
    selectedRiskId,
    fileList,
    modifiedText,
    loading,
    version,
    selectedRisk,
    selectRisk,
    submitAnalysis,
    resetAnalysis,
  }
})
