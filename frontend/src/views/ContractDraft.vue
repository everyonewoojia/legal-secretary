<template>
  <el-container style="height:100vh">
    <el-header class="header">
      <div class="header-left">
        <span class="brand">法务小秘</span>
        <el-tag type="success" size="small">合同起草</el-tag>
      </div>
      <div class="header-nav">
        <el-button text @click="router.push('/')">首页</el-button>
        <el-button text @click="router.push('/negotiate')">风险审查</el-button>
        <el-button text @click="router.push('/admin')">后台管理</el-button>
      </div>
    </el-header>

    <el-main class="main-layout">
      <el-card shadow="never" class="type-bar">
        <span style="font-size:14px;font-weight:600;margin-right:16px">合同类型</span>
        <el-radio-group v-model="store.contractType" @change="onTypeChange">
          <el-radio-button value="tech_service">技术服务</el-radio-button>
          <el-radio-button value="procurement">采购合同</el-radio-button>
          <el-radio-button value="employment">劳动合同</el-radio-button>
          <el-radio-button value="cooperation">合作协议</el-radio-button>
          <el-radio-button value="non_disclosure">保密协议</el-radio-button>
        </el-radio-group>
      </el-card>

      <div class="workspace">
        <el-card shadow="never" class="chat-panel">
          <template #header>
            <span>智能对话</span>
          </template>

          <div class="messages" ref="msgBox">
            <div v-for="(m, i) in store.messages" :key="i" :class="['msg', m.role]">
              <div class="avatar">
                {{ m.role === 'ai' ? '🤖' : '👤' }}
              </div>
              <div class="bubble">
                <div class="text">{{ m.content }}</div>
                <el-icon v-if="m.loading" class="is-loading" style="margin-left:4px">
                  <svg viewBox="0 0 1024 1024"><path d="M512 64a32 32 0 0 1 32 32v192a32 32 0 0 1-64 0V96a32 32 0 0 1 32-32z"/><path d="M512 736a32 32 0 0 1 32 32v192a32 32 0 0 1-64 0V768a32 32 0 0 1 32-32z" fill="currentColor" opacity=".6"/><path d="M160 512a32 32 0 0 1 32-32h192a32 32 0 0 1 0 64H192a32 32 0 0 1-32-32z" fill="currentColor" opacity=".4"/><path d="M640 512a32 32 0 0 1 32-32h192a32 32 0 0 1 0 64H672a32 32 0 0 1-32-32z" fill="currentColor" opacity=".8"/></svg>
                </el-icon>
              </div>
            </div>
          </div>

          <div class="quick-actions" v-if="store.messages.length <= 1">
            <el-button size="small" @click="quickFill('甲方：')">甲方</el-button>
            <el-button size="small" @click="quickFill('乙方：')">乙方</el-button>
            <el-button size="small" @click="quickFill('合同金额：')">金额</el-button>
            <el-button size="small" @click="quickFill('交付物：')">交付物</el-button>
          </div>

          <div class="input-row">
            <el-input
              v-model="inputMsg"
              placeholder="输入合同要素信息..."
              :disabled="!store.sessionId"
              @keyup.enter="send"
            />
            <el-button type="primary" @click="send" :disabled="!store.sessionId || sending">
              发送
            </el-button>
          </div>

          <div style="margin-top:12px;display:flex;gap:8px">
            <el-button
              type="success"
              :loading="store.generating"
              :disabled="!store.sessionId || !store.messages.length || sending"
              @click="generate"
            >
              生成合同
            </el-button>
            <el-button @click="resetSession">重新开始</el-button>
          </div>
        </el-card>

        <el-card shadow="never" class="preview-panel">
          <template #header>
            <div class="preview-header">
              <span>合同预览</span>
              <el-button
                size="small"
                type="primary"
                :disabled="!store.draftId"
                @click="exportDoc"
              >
                下载 DOCX
              </el-button>
            </div>
          </template>

          <div v-if="store.contractText" class="preview-body" v-html="renderedContract"></div>
          <el-empty v-else description="合同生成后将在此展示" />
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useContractStore } from '../stores/contract'
import { contract as contractApi } from '../api'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'

const router = useRouter()
const store = useContractStore()
const inputMsg = ref('')
const sending = ref(false)
const msgBox = ref(null)

async function send() {
  const text = inputMsg.value.trim()
  if (!text) return
  inputMsg.value = ''
  sending.value = true
  try {
    await store.sendMessage(text)
  } catch {
    ElMessage.error('对话请求失败')
  } finally {
    sending.value = false
  }
}

function quickFill(template) {
  inputMsg.value = template
}

async function generate() {
  const res = await store.generateContract()
  if (res.code !== 0) {
    ElMessage.warning(res.message || '合同生成失败，请补充完整信息')
  }
}

async function exportDoc() {
  const res = await contractApi.exportDraft(store.draftId)
  if (res.code === 0) {
    window.open(res.data.download_url)
  } else {
    ElMessage.warning('导出失败')
  }
}

function resetSession() {
  store.clearSession()
}

async function onTypeChange(type) {
  store.clearSession()
  try {
    await store.startSession(type)
  } catch {
    ElMessage.error('创建会话失败')
  }
}

const renderedContract = computed(() => {
  return marked(store.contractText)
})

watch(
  () => store.messages.length,
  async () => {
    await nextTick()
    if (msgBox.value) {
      msgBox.value.scrollTop = msgBox.value.scrollHeight
    }
  },
)

if (!store.sessionId) {
  store.startSession(store.contractType)
}
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 0 20px;
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
.main-layout {
  padding: 16px;
  background: #f5f7fa;
  height: calc(100vh - 60px);
}
.type-bar {
  margin-bottom: 16px;
}
.workspace {
  display: flex;
  gap: 16px;
  height: calc(100vh - 160px);
}
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.chat-panel :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 12px;
  padding-right: 4px;
}
.msg {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.msg.user {
  flex-direction: row-reverse;
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  background: #f0f2f5;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}
.msg.user .bubble {
  background: #409eff;
  color: #fff;
}
.msg .text {
  display: inline;
}
.quick-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.input-row {
  display: flex;
  gap: 8px;
}
.preview-panel {
  flex: 1;
  min-width: 0;
}
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.preview-body {
  white-space: pre-wrap;
  font-size: 14px;
  line-height: 1.8;
  overflow-y: auto;
  height: calc(100% - 20px);
}
.preview-body :deep(p) {
  margin-bottom: 8px;
}
.preview-body :deep(h1),
.preview-body :deep(h2),
.preview-body :deep(h3) {
  margin: 16px 0 8px;
}
</style>
