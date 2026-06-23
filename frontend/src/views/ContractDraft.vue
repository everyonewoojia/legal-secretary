<template>
  <el-container style="height:100vh">
    <el-header class="header">
      <span style="font-size:18px;font-weight:600">法务小秘 · 合同起草</span>
      <el-button text @click="router.push('/negotiate')">风险审查</el-button>
      <el-button text @click="router.push('/admin')">后台管理</el-button>
    </el-header>
    <el-main class="main-layout">
      <el-card class="type-select">
        <div style="font-size:14px;font-weight:600;margin-bottom:12px">选择合同类型</div>
        <el-radio-group v-model="contractType">
          <el-radio-button value="tech_service">技术服务</el-radio-button>
          <el-radio-button value="procurement">采购合同</el-radio-button>
          <el-radio-button value="employment">劳动合同</el-radio-button>
          <el-radio-button value="cooperation">合作协议</el-radio-button>
          <el-radio-button value="non_disclosure">保密协议</el-radio-button>
        </el-radio-group>
      </el-card>

      <div class="chat-preview">
        <el-card class="chat-area">
          <div class="messages" ref="msgBox">
            <div v-for="(m, i) in messages" :key="i" :class="m.role">
              <div class="bubble">{{ m.content }}</div>
            </div>
          </div>
          <div class="input-row">
            <el-input v-model="inputMsg" placeholder="请输入合同要素..." @keyup.enter="send" />
            <el-button type="primary" @click="send" :disabled="!sessionId">发送</el-button>
          </div>
          <el-button type="success" style="margin-top:12px" @click="generate" :disabled="!sessionId">生成合同</el-button>
        </el-card>

        <el-card class="preview-area">
          <div style="display:flex;justify-content:space-between">
            <span style="font-weight:600">合同预览</span>
            <el-button size="small" @click="exportDoc" :disabled="!draftId">下载</el-button>
          </div>
          <div class="preview-text">{{ contractText }}</div>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { contract } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const contractType = ref('tech_service')
const sessionId = ref(null)
const messages = ref([{ role: 'ai', content: '请选择合同类型开始起草。' }])
const inputMsg = ref('')
const contractText = ref('')
const draftId = ref(null)

async function send() {
  if (!inputMsg.value) return
  messages.value.push({ role: 'user', content: inputMsg.value })
  inputMsg.value = ''
}

async function generate() {
  if (!contractType.value) { ElMessage.warning('请选择合同类型'); return }
  if (!sessionId.value) {
    const res = await contract.createSession(contractType.value)
    if (res.code === 0) sessionId.value = res.data.session_id
  }
  const res = await contract.generate(sessionId.value)
  if (res.code === 0) {
    contractText.value = res.data.contract_text
    draftId.value = res.data.draft_id
    messages.value.push({ role: 'ai', content: '合同已生成，请在右侧预览。' })
  } else {
    ElMessage.warning(res.message)
  }
}

async function exportDoc() {
  const res = await contract.export(draftId.value)
  if (res.code === 0) window.open(res.data.download_url)
}
</script>

<style scoped>
.header { display: flex; align-items: center; gap: 16px; background: #fff; border-bottom: 1px solid #eee; padding: 0 20px; }
.main-layout { padding: 16px; }
.type-select { margin-bottom: 16px; }
.chat-preview { display: flex; gap: 16px; height: calc(100vh - 180px); }
.chat-area { flex: 1; display: flex; flex-direction: column; }
.preview-area { flex: 1; display: flex; flex-direction: column; }
.messages { flex: 1; overflow-y: auto; margin-bottom: 12px; }
.bubble { background: #f0f2f5; padding: 8px 12px; border-radius: 8px; margin: 4px 0; }
.user { text-align: right; }
.user .bubble { background: #409eff; color: #fff; }
.input-row { display: flex; gap: 8px; }
.preview-text { white-space: pre-wrap; font-size: 13px; line-height: 1.8; margin-top: 12px; overflow-y: auto; }
</style>
