import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { negotiationApi } from '../api/negotiation'
import { contractApi } from '../api/contract'

export const useNegotiationStore = defineStore('negotiation', () => {
  const contractId = ref(null)
  const caseId = ref(null)
  const diffList = ref([])
  const selectedRiskId = ref(null)
  const fileList = ref([])
  const modifiedText = ref('')
  const loading = ref(false)
  const version = ref('V1')
  const loadingAdvice = ref(false)

  const selectedRisk = computed(() => {
    if (!selectedRiskId.value) return null
    return diffList.value.find((item) => item.id === selectedRiskId.value) || null
  })

  function selectRisk(id) {
    selectedRiskId.value = id
  }

  async function loadCounterArgument(riskId) {
    if (loadingAdvice.value) return
    const item = diffList.value.find((i) => i.id === riskId)
    if (!item || item.advice) return
    loadingAdvice.value = true
    try {
      const res = await negotiationApi.counterArgument(riskId)
      if (res.code === 0 && res.data) {
        if (item) {
          const parts = []
          if (res.data.plan_a) parts.push('【强硬方案】' + res.data.plan_a)
          if (res.data.plan_b) parts.push('【折中方案】' + res.data.plan_b)
          item.advice = parts.join('\n\n')
        }
      }
    } catch (e) {
      console.warn('loadCounterArgument failed:', e)
    } finally {
      loadingAdvice.value = false
    }
  }

  function mapRiskItem(item) {
    return {
      id: item.id,
      clause_title: item.clause_location || item.clause_title || '',
      risk_level: item.risk_level || 'low',
      risk_desc: item.description || item.risk_desc || '',
      legal_basis: item.legal_basis || '',
      acceptable_bottom_line: item.acceptable_bottom_line || '',
      advice: item.advice || item.suggestion || '',
    }
  }

  async function submitAnalysis() {
    loading.value = true
    diffList.value = []
    selectedRiskId.value = null
    try {
      let cid = contractId.value

      if (!cid) {
        const content = '（原始合同文本，待对比分析）'
        const createRes = await contractApi.create(1, '谈判辅助合同', content)
        if (createRes.code !== 0) return createRes
        cid = createRes.data.id
        contractId.value = cid
      }

      if (fileList.value.length > 0) {
        for (const f of fileList.value) {
          await negotiationApi.upload(cid, f.raw)
        }
      } else if (modifiedText.value) {
        const blob = new Blob([modifiedText.value], { type: 'text/plain' })
        const file = new File([blob], 'modified_text.txt', { type: 'text/plain' })
        await negotiationApi.upload(cid, file)
      }

      await negotiationApi.getDiff(cid)

      const analyzeRes = await negotiationApi.aiAnalyze(cid)
      if (analyzeRes.code !== 0) return analyzeRes

      const risksRes = await negotiationApi.getRisks(cid)
      if (risksRes.code === 0) {
        const items = (risksRes.data || []).map(mapRiskItem)
        diffList.value = items
        version.value = 'V2'
        if (items.length > 0) {
          selectedRiskId.value = items[0].id
          loadCounterArgument(items[0].id)
        }
      }

      caseId.value = cid
      return { code: 0, data: { diff_list: diffList.value, case_id: cid, version: version.value } }
    } catch (e) {
      return { code: 1, message: e.message || '分析失败' }
    } finally {
      loading.value = false
    }
  }

  function resetAnalysis() {
    contractId.value = null
    caseId.value = null
    diffList.value = []
    selectedRiskId.value = null
    fileList.value = []
    modifiedText.value = ''
    version.value = 'V1'
  }

  return {
    contractId,
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
    loadCounterArgument,
  }
})
