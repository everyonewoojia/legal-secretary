<template>
  <div class="draft-page">
    <AppHeader tag="合同起草" tag-type="success">
      <el-button text @click="router.push('/')">首页</el-button>
      <el-button text @click="router.push('/negotiate')">谈判辅助</el-button>
      <el-button text @click="router.push('/admin')">后台管理</el-button>
    </AppHeader>

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
      <aside class="sidebar-left">
        <div class="sidebar-section">
          <h3 class="sidebar-title">合同类型选择</h3>
          <div class="type-buttons">
            <button
              v-for="t in displayTypes"
              :key="t.code"
              :class="['type-btn', { active: store.contractCode === t.code }]"
              @click="onTypeChange(t.code)"
            >
              {{ t.name }}
            </button>
          </div>
        </div>

        <div class="sidebar-section" v-if="Object.keys(store.slots).length">
          <h3 class="sidebar-title">已采集要素</h3>
          <div class="slots-list">
            <div v-for="(val, key) in store.slots" :key="key" class="slot-item">
              <span class="slot-key">{{ key }}</span>
              <span class="slot-val">{{ val }}</span>
            </div>
          </div>
        </div>
      </aside>

      <main class="chat-area">
        <div class="chat-header">
          <span class="chat-type-label">{{ store.getContractLabel(store.contractCode) }}</span>
        </div>

        <div class="messages" ref="msgBox">
          <div
            v-for="(m, i) in store.messages"
            :key="i"
            :class="['msg-row', m.role]"
          >
            <div class="msg-content">
              <div class="bubble" v-if="m.content || m.loading">
                <div class="msg-text">{{ m.content }}<span v-if="m.loading" class="cursor-blink">▌</span></div>
              </div>
            </div>
          </div>
          <div v-if="!store.messages.length" class="empty-chat">
            <el-empty description="选择一个合同类型开始对话" />
          </div>
        </div>

        <div class="input-area">
          <div class="quick-actions" v-if="store.typeId">
            <span class="hint-label">提示：</span>
            <el-button size="small" @click="quickFill('甲方：')">甲方</el-button>
            <el-button size="small" @click="quickFill('乙方：')">乙方</el-button>
            <el-button size="small" @click="quickFill('合同金额：')">金额</el-button>
            <el-button size="small" @click="quickFill('交付物：')">交付物</el-button>
            <el-button size="small" @click="quickFill('付款方式：')">付款方式</el-button>
            <el-button size="small" @click="quickFill('交付期限：')">交付期限</el-button>
            <el-button size="small" @click="quickFill('违约金比例：')">违约金比例</el-button>
          </div>
          <div class="input-row">
            <el-input
              v-model="inputMsg"
              type="textarea"
              :rows="2"
              placeholder="请输入您的回答…（例如：深圳某某科技公司、一次性、50万）"
              :disabled="!store.typeId"
              @keyup.enter.prevent="send"
            />
            <div class="input-actions">
              <el-button
                type="primary"
                :loading="sending"
                :disabled="!store.typeId || !inputMsg.trim()"
                @click="send"
              >
                发送
              </el-button>
            </div>
          </div>
        </div>
      </main>

      <aside class="sidebar-right" v-show="showPreview">
        <div class="preview-header">
          <h3 class="preview-title">《{{ store.getContractLabel(store.contractCode) }}》</h3>
        </div>
        <div class="preview-body">
          <div v-if="store.currentDraft" class="contract-text" v-html="renderedDraft" />
          <el-empty v-else description="点击下方按钮生成合同" />
        </div>
        <div class="preview-actions">
          <el-button
            type="primary"
            :loading="store.generating"
            :disabled="!store.typeId"
            @click="generate"
          >
            生成合同
          </el-button>
          <el-button
            :disabled="!store.draftId"
            @click="regenerate"
          >
            重新生成
          </el-button>
          <el-button
            :disabled="!store.draftId"
            @click="exportDoc"
          >
            下载
          </el-button>
        </div>
      </aside>
    </div>

    <div v-if="!store.draftId" class="gen-float-btn">
      <el-button
        type="primary"
        size="large"
        :loading="store.generating"
        :disabled="!store.typeId || !store.messages.length || sending"
        @click="generate"
        round
      >
        生成合同
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useContractStore } from '../stores/contract'
import { contractApi } from '../api/contract'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import AppHeader from '../components/AppHeader.vue'

const router = useRouter()
const store = useContractStore()

const renderedDraft = computed(() => {
  if (!store.currentDraft) return ''
  return marked(store.currentDraft)
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

const inputMsg = ref('')
const sending = ref(false)
const errorMsg = ref('')
const msgBox = ref(null)

const showPreview = computed(() => !!store.draftId || store.generating)

async function onTypeChange(type) {
  errorMsg.value = ''
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

function quickFill(template) {
  const current = inputMsg.value.trim()
  if (current.includes(template.replace('：', ''))) {
    return
  }
  if (current) {
    inputMsg.value = current + '，' + template
  } else {
    inputMsg.value = template
  }
}

async function generate() {
  errorMsg.value = ''
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

watch(
  () => store.messages.length,
  async () => {
    await nextTick()
    if (msgBox.value) {
      msgBox.value.scrollTop = msgBox.value.scrollHeight
    }
  },
)

if (!store.messages.length) {
  store.startSession(store.contractCode)
}
</script>

<style scoped>
.draft-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}


.main-body {
  flex: 1;
  display: flex;
  gap: 0;
  overflow: hidden;
}

.sidebar-left {
  width: 220px;
  min-width: 220px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-section {
  padding: 16px;
  border-bottom: 1px solid #f0f2f5;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.type-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.type-btn {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  text-align: left;
  transition: all 0.2s;
}

.type-btn:hover {
  border-color: #409eff;
  color: #409eff;
}

.type-btn.active {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
  font-weight: 500;
}

.slots-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.slot-item {
  display: flex;
  flex-direction: column;
  padding: 6px 8px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
}

.slot-key {
  font-weight: 500;
  color: #606266;
  margin-bottom: 2px;
}

.slot-val {
  color: #303133;
  word-break: break-all;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  height: 48px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.chat-type-label {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.msg-row {
  display: flex;
}

.msg-row.agent {
  justify-content: flex-start;
}

.msg-row.user {
  justify-content: flex-end;
}

.msg-content {
  max-width: 75%;
}

.bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.msg-row.agent .bubble {
  background: #fff;
  border: 1px solid #e4e7ed;
  color: #303133;
}

.msg-row.user .bubble {
  background: #409eff;
  color: #fff;
}

.msg-text {
  display: inline;
}

.cursor-blink {
  animation: blink 0.8s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.empty-chat {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-area {
  padding: 12px 20px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.quick-actions {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
  align-items: center;
}
.quick-actions .hint-label {
  font-size: 12px;
  color: #909399;
  margin-right: 2px;
  white-space: nowrap;
}
.quick-actions .el-button {
  padding: 4px 10px;
  font-size: 12px;
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.input-row :deep(.el-textarea__inner) {
  border-radius: 8px;
  resize: none;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-right {
  width: 380px;
  min-width: 380px;
  background: #fff;
  border-left: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.preview-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.preview-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.preview-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.contract-text {
  font-size: 13px;
  line-height: 1.8;
  word-break: break-word;
  font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
  color: #303133;
  padding: 16px;
}

.contract-text h1,
.contract-text h2,
.contract-text h3 {
  margin: 16px 0 8px;
  color: #1a1a2e;
}

.contract-text h1 { font-size: 16px; }
.contract-text h2 { font-size: 15px; }
.contract-text h3 { font-size: 14px; }

.contract-text p { margin: 6px 0; }

.contract-text ul,
.contract-text ol {
  padding-left: 20px;
  margin: 6px 0;
}

.contract-text li { margin: 3px 0; }

.contract-text strong { font-weight: 600; }

.contract-text hr {
  border: none;
  border-top: 1px solid #e4e7ed;
  margin: 12px 0;
}

.preview-actions {
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.gen-float-btn {
  position: fixed;
  bottom: 80px;
  right: 40px;
  z-index: 100;
}

@media (max-width: 900px) {
  .sidebar-left {
    width: 160px;
    min-width: 160px;
  }

  .sidebar-right {
    width: 300px;
    min-width: 300px;
  }
}
</style>
