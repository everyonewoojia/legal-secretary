<template>
  <div class="draft-page">
    <el-alert
      v-if="errorMsg"
      :title="errorMsg"
      type="error"
      show-icon
      closable
      @close="errorMsg = ''"
      style="border-radius:0"
    />

    <div class="main-body" :class="{ 'has-draft': hasDraft, 'preview-expanded': previewExpanded }">
      <aside class="sidebar-left">
        <div class="sidebar-section">
          <h3 class="sidebar-title">合同类型选择</h3>
          <div class="type-list">
            <div
              v-for="t in displayTypes"
              :key="t.code"
              :class="['type-card', { active: store.contractCode === t.code }]"
              @click="onTypeChange(t.code)"
            >
              <span class="type-icon">{{ typeIcons[t.code] || '📄' }}</span>
              <span class="type-label">{{ t.name }}</span>
            </div>
          </div>
        </div>

        <div class="sidebar-section progress-section">
          <div class="progress-text">已采集 <span class="progress-num">{{ filledCount }}</span> 条要素</div>
        </div>

        <div class="sidebar-section slots-section">
          <div v-if="!fieldKeys.length" class="slots-empty">等待采集要素...</div>
          <div v-else class="slots-bubbles">
            <div
              v-for="field in fieldKeys"
              :key="field"
              class="slot-bubble"
            >
              <span class="bubble-dot" />
              <span class="bubble-text">{{ field }}：{{ store.slots[field] }}</span>
            </div>
          </div>
        </div>
      </aside>

      <main class="chat-area">
        <div class="chat-header">
          <div class="chat-header-left">
            <span class="chat-type-label">{{ store.getContractLabel(store.contractCode) }}</span>
            <span class="status-dot" :class="hasDraft ? 'green' : 'blue'" />
            <span class="status-text">{{ hasDraft ? '可生成合同' : '信息采集中' }}</span>
          </div>
        </div>

        <div class="messages" ref="msgBox">
          <div v-for="(m, i) in store.messages" :key="i" :class="['msg-row', m.role]">
            <div v-if="m.role === 'agent' || m.role === 'assistant'" class="msg-avatar">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="16" r="16" fill="#E5E7EB" />
                <circle cx="11" cy="13" r="1.5" fill="#2563EB" />
                <circle cx="21" cy="13" r="1.5" fill="#2563EB" />
                <path d="M11 19c0 0 2 3.5 5 3.5s5-3.5 5-3.5" stroke="#2563EB" stroke-width="1.5" stroke-linecap="round" />
              </svg>
            </div>
            <div class="msg-content">
              <div class="bubble">
                <div class="msg-text">
                  {{ m.content }}
                  <span v-if="m.loading" class="typing-dots">
                    <span class="dot" /><span class="dot" /><span class="dot" />
                  </span>
                </div>
              </div>
              <div class="msg-time">{{ formatTime(m.time) }}</div>
            </div>
            <div v-if="m.role === 'user'" class="msg-avatar">
              <img v-if="userAvatar" :src="userAvatar" class="user-avatar-img" />
              <span v-else class="user-avatar-fallback">{{ userInitial }}</span>
            </div>
          </div>
          <div v-if="!store.messages.length" class="empty-chat">
            <div class="empty-icon">📄</div>
            <p class="empty-title">选择合同类型</p>
            <p class="empty-desc">请在左侧选择一个合同类型开始对话</p>
          </div>
        </div>

        <div class="input-area">
          <div class="quick-replies" v-if="store.typeId">
            <button
              v-for="r in quickReplies"
              :key="r"
              class="quick-chip"
              @click="quickFill(r)"
            >
              {{ r }}
            </button>
          </div>
          <div class="input-row">
            <el-input
              v-model="inputMsg"
              type="textarea"
              :rows="1"
              placeholder="请输入您的回答..."
              :disabled="!store.typeId"
              @keyup.enter.prevent="send"
              class="chat-input"
            />
            <el-button
              type="primary"
              :loading="sending"
              :disabled="!store.typeId || !inputMsg.trim()"
              @click="send"
              class="send-btn"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </el-button>
            <el-button
              v-if="!store.draftId"
              type="primary"
              :loading="store.generating"
              :disabled="!store.messages.length || sending || store.generating"
              @click="generate"
              class="gen-row-btn"
            >
              生成合同
            </el-button>
            <button
              v-if="store.draftId"
              class="regenerate-btn"
              @click="regenerate"
            >
              重新生成
            </button>
            <button
              v-if="store.currentDraft && !previewVisible"
              class="view-btn"
              @click="previewVisible = true"
            >
              查看合同
            </button>
            <button v-if="store.typeId" class="reset-btn" @click="resetChat">↺ 重新开始</button>
          </div>
        </div>
      </main>

      <aside class="sidebar-right" v-show="previewVisible">
        <div class="preview-header">
          <h3 class="preview-title">《{{ store.getContractLabel(store.contractCode) }}》</h3>
          <div class="preview-header-right">
            <span v-if="store.draftId" class="preview-version">V1.0</span>
            <button v-if="hasDraft" class="expand-btn" @click="toggleExpand" :title="previewExpanded ? '恢复比例' : '展开预览'">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline v-if="!previewExpanded" points="15 3 21 3 21 9" />
                <polyline v-if="!previewExpanded" points="9 21 3 21 3 15" />
                <line v-if="!previewExpanded" x1="21" y1="3" x2="14" y2="10" />
                <line v-if="!previewExpanded" x1="3" y1="21" x2="10" y2="14" />
                <polyline v-if="previewExpanded" points="15 21 21 21 21 15" />
                <polyline v-if="previewExpanded" points="9 3 3 3 3 9" />
                <line v-if="previewExpanded" x1="21" y1="21" x2="14" y2="14" />
                <line v-if="previewExpanded" x1="3" y1="3" x2="10" y2="10" />
              </svg>
            </button>
            <button class="preview-close-btn" @click="closePreview" title="关闭预览">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </div>
        <div class="preview-body">
          <div v-if="store.currentDraft" class="contract-text" v-html="renderedDraft" />
          <div v-else class="preview-empty">
            <div class="empty-icon">📄</div>
            <p class="empty-title">{{ store.generating ? '合同生成中...' : '暂无合同' }}</p>
            <p class="empty-desc">{{ store.generating ? '合同内容正在生成，请稍候' : '完成对话后，点击下方「生成合同」即可在此预览' }}</p>
            <el-button
              v-if="!store.generating"
              type="primary"
              :disabled="!store.typeId"
              @click="generate"
              class="generate-btn"
            >
              生成合同
            </el-button>
            <div v-else class="generate-loading">
              <span class="loading-dot"></span>
              <span class="loading-dot"></span>
              <span class="loading-dot"></span>
            </div>
          </div>
        </div>
        <div class="preview-actions" v-if="store.currentDraft">
          <el-button
            class="action-btn primary"
            :disabled="!store.draftId"
            @click="exportDoc"
          >
            下载
          </el-button>
          <el-button
            @click="restartDraft"
          >
            重新起草
          </el-button>
        </div>
      </aside>
    </div>

  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useContractStore } from '../stores/contract'
import { useUserStore } from '../stores/user'
import { contractApi } from '../api/contract'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'

const router = useRouter()
const store = useContractStore()
const userStore = useUserStore()

const previewExpanded = ref(false)

const typeIcons = {
  tech_service: '📄',
  procurement: '📝',
  employment: '🤝',
  cooperation: '🔒',
  non_disclosure: '📋',
}

const filledCount = computed(() => Object.keys(store.slots).length)
const fieldKeys = computed(() => Object.keys(store.slots))

const hasDraft = computed(() => !!store.currentDraft)

const userAvatar = computed(() => userStore.userInfo?.avatar || '')
const userInitial = computed(() => (userStore.userInfo?.username || '我').charAt(0))

const quickReplies = ['甲方：', '乙方：', '合同金额：', '交付物：', '付款方式：', '交付期限：', '违约金比例：']

function preprocessContract(text) {
  const lines = text.split('\n')
  const result = []
  let inSignature = false
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trimmed = line.trim()
    if (!trimmed) { result.push(''); continue }
    // Title (first non-empty line)
    if (i === 0 && !trimmed.startsWith('#')) {
      result.push('# ' + trimmed)
      continue
    }
    // Section headers
    if (/^第[一二三四五六七八九十]+[条节]/.test(trimmed) && !trimmed.startsWith('#')) {
      result.push('## ' + trimmed)
      continue
    }
    // Sub-clause titles: 1.1, 1.2, 2.1...
    if (/^\d+\.\d+\s/.test(trimmed)) {
      result.push(`<p class="sub-clause">${trimmed}</p>`)
      continue
    }
    // Contract/protocol number
    if (/^(合同|协议)编号[：:]/.test(trimmed)) {
      result.push(`<p class="contract-number">${trimmed}</p>`)
      continue
    }
    // Signature block: lines with 盖章/签字/日期 near the end
    if (/（盖章）/.test(trimmed) || /（签字）/.test(trimmed) || /（签名）/.test(trimmed)) {
      inSignature = true
      result.push(`<div class="signature-line">${trimmed}</div>`)
      continue
    }
    if (inSignature && /^日期[：:]/.test(trimmed)) {
      result.push(`<div class="signature-line date-line">${trimmed}</div>`)
      continue
    }
    // Regular content
    result.push(line)
  }
  return result.join('\n')
}

const renderedDraft = computed(() => {
  if (!store.currentDraft) return ''
  return marked(preprocessContract(store.currentDraft))
})

const displayTypes = computed(() => {
  if (store.contractTypes.length) {
    return store.contractTypes.map(t => ({ code: t.code, name: t.name }))
  }
  return [
    { code: 'tech_service', name: '技术服务合同' },
    { code: 'procurement', name: '采购合同' },
    { code: 'employment', name: '劳动合同' },
    { code: 'cooperation', name: '合作协议' },
    { code: 'non_disclosure', name: '保密协议' },
  ]
})

const previewVisible = ref(false)

const inputMsg = ref('')
const sending = ref(false)
const errorMsg = ref('')
const msgBox = ref(null)

function toggleExpand() {
  previewExpanded.value = !previewExpanded.value
}

function formatTime(time) {
  if (!time) return ''
  const d = new Date(time)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function onTypeChange(type) {
  errorMsg.value = ''
  previewVisible.value = false
  previewExpanded.value = false
  if (msgBox.value) msgBox.value.scrollTop = 0 // 归零
  try {
    await store.startSession(type)
  } catch (e) {
    errorMsg.value = '创建会话失败：' + (e.message || '未知错误')
    ElMessage.error(errorMsg.value)
  }
}

async function send() {
  const text = inputMsg.value.trim()
  if (!text || !store.typeId) return
  inputMsg.value = ''
  sending.value = true
  errorMsg.value = ''
  try {
    await store.sendMessage(text)
  } catch (e) {
    errorMsg.value = '对话请求失败，请重试'
    ElMessage.error(errorMsg.value)
  } finally {
    sending.value = false
  }
}

function quickFill(text) {
  inputMsg.value = text
}

async function generate() {
  if (store.generating) return
  errorMsg.value = ''
  previewVisible.value = true
  try {
    const res = await store.generateContract()
    if (res.code !== 0) {
      ElMessage.warning(res.message || '信息不完整，请继续补充')
    }
  } catch (e) {
    errorMsg.value = '合同生成失败：' + (e.message || '未知错误')
    ElMessage.error(errorMsg.value)
  }
}

async function regenerate() {
  store.currentDraft = ''
  store.draftId = null
  await generate()
}

function restartDraft() {
  store.clearSession()
  if (store.typeList.length > 0) {
    store.startSession(store.typeList[0].code)
  }
}

async function exportDoc() {
  if (!store.draftId) return
  try {
    const res = await contractApi.download(store.draftId)
    if (res.code === 0 && res.data?.download_url) {
      window.open(res.data.download_url, '_blank')
    } else if (res.code === 0 && res.data?.content) {
      const blob = new Blob([res.data.content], { type: 'text/plain;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${res.data.title || '合同'}.${res.data.format || 'docx'}`
      a.click()
      URL.revokeObjectURL(url)
    } else {
      ElMessage.warning('导出失败')
    }
  } catch {
    ElMessage.error('导出请求失败')
  }
}

function closePreview() {
  previewVisible.value = false
  previewExpanded.value = false
}

function resetChat() {
  store.clearSession()
  inputMsg.value = ''
  errorMsg.value = ''
  previewVisible.value = false
}

watch(
  () => store.messages,
  async () => {
    await nextTick()
    if (msgBox.value) {
      msgBox.value.scrollTo({
        top: msgBox.value.scrollHeight,
        behavior: 'smooth'
      })
    }
  },
  { deep: true }
)

if (!store.messages.length) {
  store.startSession(store.contractCode)
}
</script>

<style scoped>
.draft-page {
  height: 100vh;          /* 限制整页高度为视口高度 */
  display: flex;
  flex-direction: column;
  background: #F8FAFC;
  overflow: hidden;       /* 阻止外层出现全局滚动条 */
}

.draft-page :deep(.el-alert) {
  flex-shrink: 0;
}

/* ===== Main Layout ===== */
.main-body {
  flex: 1;
  display: flex;
  gap: 0;
  height: calc(100vh - 40px); /* 减去 el-alert 或 header 的高度，确保主体不超高 */
  overflow: hidden;           /* 核心：父级锁死，只让子内部滚动 */
  transition: all 0.3s ease;
}

/* Default (dialogue phase): sidebar 240px | chat 1.2fr | preview 0.8fr */
.sidebar-left {
  width: 240px;
  min-width: 240px;
  background: #fff;
  border-right: 1px solid #E5E7EB;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  transition: width 0.3s ease, min-width 0.3s ease;
}

.chat-area {
  flex: 1.2;
  display: flex;
  flex-direction: column;
  height: 100%;           /* 满格撑开 */
  min-width: 0;
  overflow: hidden;       /* 切断外溢，逼迫 .messages 产生滚动条 */
  transition: flex 0.3s ease;
}

.sidebar-right {
  flex: 0.8;
  min-width: 300px;
  height: 100%;           /* 满格撑开 */
  background: #fff;
  border-left: 1px solid #E5E7EB;
  display: flex;
  flex-direction: column;
  overflow: hidden;       /* 切断外溢 */
  transition: flex 0.3s ease;
}

/* Has draft: sidebar 200px | chat 1fr | preview 1.2fr */
.has-draft .sidebar-left {
  width: 200px;
  min-width: 200px;
}

.has-draft .chat-area {
  flex: 1;
}

.has-draft .sidebar-right {
  flex: 1.2;
}

/* Preview expanded: chat 0.5fr | preview 1.5fr */
.preview-expanded .chat-area {
  flex: 0.5;
}

.preview-expanded .sidebar-right {
  flex: 1.5;
}

/* ===== Left Sidebar ===== */
.sidebar-section {
  padding: 16px;
  border-bottom: 1px solid #F1F5F9;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 12px;
}

.type-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.type-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.type-card:hover {
  border-color: #2563EB;
}

.type-card.active {
  border-color: #2563EB;
  background: #EFF6FF;
}

.type-icon {
  font-size: 18px;
  line-height: 1;
}

.type-label {
  font-size: 13px;
  color: #1E293B;
  font-weight: 500;
}

.progress-section {
  padding: 10px 16px;
}

.progress-text {
  font-size: 16px;
  color: #64748B;
  font-weight: 500;
}

.progress-num {
  color: #2563EB;
  font-weight: 700;
  font-size: 18px;
}

.slots-section {
  flex: 1;
  overflow-y: auto;
  padding-top: 0;
}

.slots-empty {
  font-size: 16px;
  color: #94A3B8;
  text-align: center;
  padding: 32px 0;
}

.slots-bubbles {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.slot-bubble {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-radius: 8px;
  animation: bubbleSlideIn 0.3s ease;
}

.bubble-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2563EB;
  flex-shrink: 0;
}

.bubble-text {
  font-size: 16px;
  font-weight: 500;
  color: #1E293B;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
}

@keyframes bubbleSlideIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.slot-name {
  color: #1E293B;
  font-weight: 500;
  white-space: nowrap;
}

.slot-value {
  color: #64748B;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== Chat Area ===== */
.chat-header {
  height: 40px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  background: #fff;
  border-bottom: 1px solid #E5E7EB;
  flex-shrink: 0;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.chat-type-label {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
}

.status-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  margin-left: 4px;
}

.status-dot.blue { background: #2563EB; }
.status-dot.green { background: #10B981; }

.status-text {
  font-size: 11px;
  color: #64748B;
}

/* Messages */
.messages {
  flex: 1;                /* 自动吃掉输入框上方的所有剩余空间 */
  overflow-y: auto;       /* 仅在这里产生垂直滚动条 */
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #F8FAFC;
}

.msg-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  animation: msgIn 0.3s ease;
}

.msg-row.agent { justify-content: flex-start; }
.msg-row.user { justify-content: flex-end; }

.msg-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.msg-avatar svg {
  display: block;
}

.user-avatar-img {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar-fallback {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #E5E7EB;
  color: #64748B;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.msg-row.user .msg-avatar {
  order: 1;
}

.msg-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.msg-row.user .msg-content {
  align-items: flex-end;
}

.bubble {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
  color: #1E293B;
}

.msg-row.agent .bubble {
  background: #EFF6FF;
  border-top-left-radius: 4px;
}

.msg-row.user .bubble {
  background: #F1F5F9;
  border-top-right-radius: 4px;
}

.msg-text { display: inline; }

.msg-time {
  font-size: 10px;
  color: #94A3B8;
  padding: 0 4px;
}

/* Typing dots */
.typing-dots {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-left: 4px;
}

.typing-dots .dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #2563EB;
  animation: dotPulse 1.2s ease-in-out infinite;
}

.typing-dots .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dots .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.empty-icon { font-size: 48px; opacity: 0.4; }
.empty-title { font-size: 16px; font-weight: 600; color: #1E293B; margin: 0; }
.empty-desc { font-size: 14px; color: #94A3B8; margin: 0; }

/* Input Area */
.input-area {
  padding: 8px 24px 24px;
  background: #fff;
  border-top: 1px solid #E5E7EB;
  flex-shrink: 0;         /* 绝对不允许被压缩，死死固定在底部 */
}

.quick-replies {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.quick-chip {
  padding: 3px 10px;
  border: 1px solid #E5E7EB;
  border-radius: 14px;
  background: #fff;
  font-size: 11px;
  color: #64748B;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-chip:hover {
  border-color: #2563EB;
  color: #2563EB;
  background: #EFF6FF;
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.chat-input { flex: 0.8; }

.chat-input :deep(.el-textarea__inner) {
  border-radius: 8px;
  border: 1px solid #E5E7EB;
  resize: none;
  padding: 12px 14px;
  min-height: 52px;
  font-size: 16px;
  line-height: 1.5;
  transition: border-color 0.2s;
}

.chat-input :deep(.el-textarea__inner:focus) {
  border-color: #2563EB;
  box-shadow: 0 0 0 1px #2563EB;
}

.send-btn {
  width: 60px;
  height: 52px;
  border-radius: 8px;
  background: #2563EB;
  border-color: #2563EB;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 16px;
  font-weight: 600;
}

.send-btn:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

.gen-row-btn {
  height: 52px;
  border-radius: 8px;
  background: #2563EB;
  border-color: #2563EB;
  font-size: 14px;
  font-weight: 600;
  padding: 0 16px;
  flex-shrink: 0;
}

.gen-row-btn:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
}


.regenerate-btn,
.reset-btn {
  border: 1px solid #E5E7EB;
  background: #fff;
  font-size: 14px;
  color: #94A3B8;
  cursor: pointer;
  padding: 0 16px;
  height: 52px;
  border-radius: 8px;
  min-width: 118px;
  flex-shrink: 0;
  transition: all 0.2s;
  white-space: nowrap;
}

.regenerate-btn {
  color: #2563EB;
  border-color: #2563EB;
}

.regenerate-btn:hover {
  background: #EFF6FF;
}

.view-btn {
  border: 1px solid #2563EB;
  background: #2563EB;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  padding: 0 16px;
  height: 52px;
  border-radius: 8px;
  min-width: 118px;
  flex-shrink: 0;
  transition: all 0.2s;
  white-space: nowrap;
}

.view-btn:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

.reset-btn:hover {
  color: #2563EB;
  border-color: #2563EB;
  background: #EFF6FF;
}

/* ===== Right Sidebar Preview ===== */
.preview-header {
  padding: 10px 16px;
  border-bottom: 1px solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.preview-title {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

.preview-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-version {
  font-size: 11px;
  color: #94A3B8;
  background: #F1F5F9;
  padding: 2px 8px;
  border-radius: 4px;
}

.expand-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94A3B8;
  transition: all 0.2s;
}

.expand-btn:hover {
  border-color: #2563EB;
  color: #2563EB;
  background: #EFF6FF;
}

.preview-close-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94A3B8;
  transition: all 0.2s;
}

.preview-close-btn:hover {
  border-color: #EF4444;
  color: #EF4444;
  background: #FEF2F2;
}

.preview-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #F8FAFC;
}

.preview-body::-webkit-scrollbar {
  width: 5px;
}

.preview-body::-webkit-scrollbar-track {
  background: transparent;
}

.preview-body::-webkit-scrollbar-thumb {
  background: #D1D5DB;
  border-radius: 3px;
}

.contract-text {
  background: #FFFFFF;
  padding: 32px 40px;
  max-width: 800px;
  margin: 0 auto;
  font-family: 'Times New Roman', 'Noto Serif SC', 'SimSun', serif;
  font-size: 14px;
  line-height: 1.8;
  color: #1E293B;
  word-break: break-word;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
  border-radius: 4px;
}

/* Title */
.contract-text h1 {
  text-align: center;
  font-size: 14px;
  font-weight: 400;
  line-height: 1.8;
  margin: 0 0 12px;
  color: #1E293B;
}

/* Section headers: 第一条/第二条 */
.contract-text h2 {
  font-size: 14px;
  font-weight: 400;
  line-height: 1.8;
  margin: 12px 0 4px;
  color: #1E293B;
}

/* Body paragraphs */
.contract-text p {
  font-size: 14px;
  line-height: 1.8;
  margin: 4px 0;
  text-indent: 2em;
  color: #1E293B;
}

/* Contract number (no indent, right-aligned, only bold element) */
.contract-text :deep(.contract-number) {
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: #94A3B8;
  margin-bottom: 16px;
  text-indent: 0;
}

/* Sub-clause titles: 1.1, 1.2 (no indent) */
.contract-text :deep(.sub-clause) {
  font-size: 14px;
  font-weight: 400;
  line-height: 1.8;
  margin: 4px 0;
  text-indent: 0;
  color: #1E293B;
}

/* Signature section (right-aligned, no indent) */
.contract-text :deep(.signature-line) {
  text-align: right;
  font-size: 14px;
  line-height: 2;
  margin-top: 4px;
  text-indent: 0;
}

.contract-text :deep(.signature-line:first-of-type) {
  margin-top: 24px;
}

/* Strong labels - no bold */
.contract-text strong {
  font-weight: 400;
  color: #1E293B;
}

.contract-text ul,
.contract-text ol {
  padding-left: 24px;
  margin: 4px 0;
}

.contract-text li {
  font-size: 14px;
  line-height: 1.8;
  margin: 3px 0;
}

.contract-text hr {
  border: none;
  border-top: 1px solid #E5E7EB;
  margin: 16px 0;
}

.preview-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
}

.preview-empty .empty-icon { font-size: 48px; opacity: 0.4; }
.preview-empty .empty-title { font-size: 16px; font-weight: 600; color: #1E293B; margin: 0; }
.preview-empty .empty-desc {
  font-size: 14px;
  color: #94A3B8;
  margin: 0;
  text-align: center;
  max-width: 280px;
}

.generate-btn { margin-top: 8px; }

.generate-loading {
  display: flex;
  gap: 6px;
  margin-top: 16px;
}
.loading-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #2563EB;
  animation: dotPulse 1.4s infinite ease-in-out both;
}
.loading-dot:nth-child(1) { animation-delay: -0.32s; }
.loading-dot:nth-child(2) { animation-delay: -0.16s; }
.loading-dot:nth-child(3) { animation-delay: 0s; }
@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.preview-actions {
  padding: 12px 16px;
  border-top: 1px solid #E5E7EB;
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  flex: 1;
  height: 36px;
  border-radius: 8px;
  font-size: 13px;
}

.action-btn.primary {
  background: #2563EB;
  border-color: #2563EB;
  color: #fff;
}

.action-btn.primary:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

.action-btn.secondary {
  background: #fff;
  border-color: #2563EB;
  color: #2563EB;
}

.action-btn.secondary:hover {
  background: #EFF6FF;
}

/* ===== Responsive ===== */
@media (max-width: 900px) {
  .sidebar-left {
    width: 180px;
    min-width: 180px;
  }

  .has-draft .sidebar-left {
    width: 160px;
    min-width: 160px;
  }

  .sidebar-right {
    min-width: 260px;
  }
}

@media (max-width: 640px) {
  .sidebar-left,
  .sidebar-right {
    display: none;
  }
}
</style>
