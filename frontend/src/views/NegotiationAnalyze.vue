<template>
  <div class="negotiate-page">
    <el-header class="header" height="56px">
      <div class="header-left">
        <span class="brand">法务小秘</span>
        <el-tag type="warning" size="small">谈判辅助</el-tag>
      </div>
      <div class="header-nav">
        <el-button text @click="router.push('/')">首页</el-button>
        <el-button text @click="router.push('/draft')">合同起草</el-button>
        <el-button text @click="router.push('/admin')">后台管理</el-button>
      </div>
    </el-header>

    <el-alert
      v-if="errorMsg"
      :title="errorMsg"
      type="error"
      show-icon
      closable
      @close="errorMsg = ''"
      style="border-radius:0"
    />

    <div class="main-body">
      <div class="left-panel">
        <div class="panel-header">
          <h2 class="page-title">法务小秘 谈判辅助</h2>
        </div>

        <div class="input-section">
          <el-upload
            ref="uploadRef"
            v-model:file-list="store.fileList"
            :limit="3"
            :auto-upload="false"
            accept=".doc,.docx,.txt"
            :on-exceed="handleExceed"
            :before-upload="beforeUpload"
          >
            <el-button size="default">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:4px;vertical-align:-2px">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              上传合同文件
            </el-button>
            <template #tip>
              <div class="upload-tip">支持 .doc .docx .txt 格式</div>
            </template>
          </el-upload>

          <div class="divider-text"><span>或</span></div>

          <el-input
            v-model="store.modifiedText"
            type="textarea"
            :rows="6"
            placeholder="粘贴对方修改后的合同文本，或输入修改内容…"
          />

          <el-button
            type="primary"
            size="large"
            :loading="store.loading"
            :disabled="!hasInput"
            @click="startAnalysis"
            class="analyze-btn"
          >
            {{ store.loading ? '分析中…' : '开始分析' }}
          </el-button>

          <p v-if="!hasInput && showValidationHint" class="hint-error">
            请上传文件或粘贴修改文本后进行分析
          </p>
        </div>

        <div v-if="store.diffList.length" class="diff-section">
          <h3 class="section-title">
            修改差异列表
            <el-tag size="small" type="info" style="margin-left:8px">
              {{ store.diffList.length }} 项
            </el-tag>
          </h3>
          <div class="diff-list">
            <div
              v-for="item in store.diffList"
              :key="item.id"
              :class="['diff-item', { active: store.selectedRiskId === item.id }]"
              @click="onSelectRisk(item.id)"
            >
              <div class="diff-item-header">
                <span class="diff-clause">{{ item.clause_title }}</span>
                <el-tag
                  :type="riskTagType(item.risk_level)"
                  size="small"
                  effect="dark"
                >
                  {{ riskLabel(item.risk_level) }}
                </el-tag>
              </div>
              <p class="diff-preview">{{ item.risk_desc }}</p>
            </div>
          </div>
        </div>

        <el-empty v-else-if="store.loading" description="正在分析中…" />
      </div>

      <div class="right-panel" v-if="store.diffList.length">
        <div class="right-header">
          <h3 class="version-title">原合同版本：{{ store.version }}</h3>
        </div>

        <div v-if="store.selectedRisk" class="risk-detail">
          <div class="detail-section">
            <div class="detail-label">风险等级</div>
            <el-tag
              :type="riskTagType(store.selectedRisk.risk_level)"
              size="default"
              effect="dark"
            >
              {{ riskLabel(store.selectedRisk.risk_level) }}
            </el-tag>
          </div>

          <div class="detail-section">
            <div class="detail-label">修改条款</div>
            <div class="detail-value">{{ store.selectedRisk.clause_title }}</div>
          </div>

          <div class="detail-section">
            <div class="detail-label">风险原因</div>
            <div class="detail-value">{{ store.selectedRisk.risk_desc }}</div>
          </div>

          <div class="detail-section" v-if="store.selectedRisk.legal_basis">
            <div class="detail-label">依据</div>
            <div class="detail-value">{{ store.selectedRisk.legal_basis }}</div>
          </div>

          <div class="detail-section" v-if="store.selectedRisk.acceptable_bottom_line">
            <div class="detail-label">可接受底线</div>
            <div class="detail-value highlight">{{ store.selectedRisk.acceptable_bottom_line }}</div>
          </div>

          <div class="detail-section" v-if="store.selectedRisk.advice">
            <div class="detail-label">建议话术</div>
            <div class="detail-value advice-text">{{ store.selectedRisk.advice }}</div>
          </div>
        </div>

        <div class="right-actions">
          <el-button
            type="primary"
            :disabled="!store.selectedRisk?.advice"
            @click="copyAdvice"
          >
            复制话术
          </el-button>
          <el-button
            :disabled="!store.caseId"
            @click="exportReport"
          >
            导出报告
          </el-button>
        </div>

        <div class="disclaimer">
          免责声明：本分析结果仅供参考，不构成法律意见。建议在实际谈判中咨询专业律师。
        </div>
      </div>

      <div v-else class="right-panel right-empty">
        <el-empty description="分析结果将在此展示" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNegotiationStore } from '../stores/negotiation'
import { contractApi } from '../api/contract'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useNegotiationStore()
const errorMsg = ref('')
const showValidationHint = ref(false)
const uploadRef = ref(null)
const MAX_FILES = 3

const hasInput = computed(() => {
  return store.fileList.length > 0 || store.modifiedText.trim().length > 0
})

function handleExceed() {
  ElMessage.warning(`最多上传 ${MAX_FILES} 个文件`)
}

function beforeUpload() {
  return false
}

function riskTagType(level) {
  if (level === 'high') return 'danger'
  if (level === 'medium') return 'warning'
  return 'primary'
}

function riskLabel(level) {
  if (level === 'high') return '高风险'
  if (level === 'medium') return '中风险'
  if (level === 'low') return '低风险'
  return level
}

async function startAnalysis() {
  errorMsg.value = ''
  showValidationHint.value = false

  if (!hasInput.value) {
    showValidationHint.value = true
    return
  }

  try {
    const res = await store.submitAnalysis()
    if (res.code !== 0) {
      errorMsg.value = res.message || '分析失败，请重试'
      ElMessage.error(errorMsg.value)
    }
  } catch (e) {
    errorMsg.value = '分析请求失败：' + (e.message || '未知错误')
    ElMessage.error(errorMsg.value)
  }
}

async function copyAdvice() {
  if (!store.selectedRisk?.advice) return
  try {
    await navigator.clipboard.writeText(store.selectedRisk.advice)
    ElMessage.success('建议话术已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

async function onSelectRisk(id) {
  store.selectRisk(id)
  if (id) store.loadCounterArgument(id)
}

async function exportReport() {
  const items = store.diffList
  if (!items.length) {
    ElMessage.warning('没有可导出的分析结果')
    return
  }
  const lines = ['谈判分析报告', '==============', '']
  items.forEach((item, i) => {
    lines.push(`--- 风险项 ${i + 1} ---`)
    if (item.clause_title) lines.push(`条款: ${item.clause_title}`)
    lines.push(`风险等级: ${item.risk_level}`)
    if (item.risk_desc) lines.push(`描述: ${item.risk_desc}`)
    if (item.legal_basis) lines.push(`法律依据: ${item.legal_basis}`)
    if (item.advice) lines.push(`建议话术: ${item.advice}`)
    lines.push('')
  })
  const content = lines.join('\n')
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `谈判分析报告_${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('报告已下载')
}
</script>

<style scoped>
.negotiate-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  height: 56px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
}

.header-nav {
  display: flex;
  gap: 4px;
}

.main-body {
  flex: 1;
  display: flex;
  gap: 0;
  overflow: hidden;
}

.left-panel {
  flex: 55;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 20px;
}

.panel-header {
  margin-bottom: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin: 0;
}

.input-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.divider-text {
  display: flex;
  align-items: center;
  margin: 16px 0;
  color: #909399;
  font-size: 12px;
}

.divider-text::before,
.divider-text::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #dcdfe6;
}

.divider-text span {
  padding: 0 12px;
}

.analyze-btn {
  width: 100%;
  margin-top: 16px;
}

.hint-error {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 8px;
}

.diff-section {
  flex: 1;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px;
  display: flex;
  align-items: center;
}

.diff-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.diff-item {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.diff-item:hover {
  border-color: #409eff;
  box-shadow: 0 1px 4px rgba(64, 158, 255, 0.12);
}

.diff-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.diff-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.diff-clause {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.diff-preview {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.right-panel {
  flex: 45;
  min-width: 340px;
  background: #fff;
  border-left: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.right-empty {
  align-items: center;
  justify-content: center;
}

.right-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.version-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.risk-detail {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-label {
  font-size: 12px;
  font-weight: 500;
  color: #909399;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-value.highlight {
  background: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 6px;
  padding: 10px 12px;
  color: #e6a23c;
  font-weight: 500;
}

.detail-value.advice-text {
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
  border-radius: 6px;
  padding: 10px 12px;
  color: #67c23a;
  font-weight: 500;
}

.right-actions {
  padding: 12px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.disclaimer {
  padding: 10px 20px;
  font-size: 11px;
  color: #c0c4cc;
  line-height: 1.5;
  border-top: 1px solid #f0f2f5;
  flex-shrink: 0;
}
</style>
