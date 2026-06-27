<template>
  <el-container style="height:100vh">
    <el-header class="header">
      <div class="header-left">
        <span class="brand">法务小秘</span>
        <el-tag type="warning" size="small">风险审查</el-tag>
      </div>
      <div class="header-nav">
        <el-button text @click="router.push('/')">首页</el-button>
        <el-button text @click="router.push('/draft')">合同起草</el-button>
        <el-button text @click="router.push('/admin')">后台管理</el-button>
      </div>
    </el-header>

    <el-main class="main-layout">
      <el-card shadow="never" class="input-card">
        <el-form label-width="100px">
          <el-form-item label="合同类型">
            <el-select v-model="contractType">
              <el-option label="技术服务合同" value="tech_service" />
              <el-option label="采购合同" value="procurement" />
              <el-option label="劳动合同" value="employment" />
              <el-option label="合作协议" value="cooperation" />
              <el-option label="保密协议" value="non_disclosure" />
            </el-select>
          </el-form-item>
          <el-form-item label="对方修改文本">
            <el-input
              v-model="modifiedText"
              type="textarea"
              :rows="6"
              placeholder="粘贴对方修改后的合同文本，或输入修改内容..."
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="analyze" :loading="loading">
              开始分析
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <template v-if="result">
        <el-card shadow="never" class="result-card">
          <template #header>
            <span style="font-weight:600">差异比对</span>
          </template>
          <div class="diff-view">
            <span
              v-for="(item, i) in result.diff"
              :key="i"
              :class="['diff-span', item.type]"
            >{{ item.text }}</span>
          </div>
        </el-card>

        <el-card shadow="never" class="result-card">
          <template #header>
            <span style="font-weight:600">风险分析 ({{ result.risk_items.length }} 项)</span>
          </template>
          <div v-if="result.risk_items.length" class="risk-list">
            <div v-for="(item, i) in result.risk_items" :key="i" class="risk-item">
              <div class="risk-header" @click="toggleRisk(i)">
                <el-tag
                  :type="riskTagType(item.risk_level)"
                  size="small"
                >
                  {{ riskLabel(item.risk_level) }}
                </el-tag>
                <span class="risk-title">{{ item.clause_title }}</span>
                <el-icon :class="{ rotated: expanded[i] }">
                  <svg viewBox="0 0 1024 1024" width="14" height="14"><path d="M256 384l256 256 256-256z" fill="currentColor"/></svg>
                </el-icon>
              </div>
              <div v-if="expanded[i]" class="risk-body">
                <div class="risk-desc">
                  <strong>风险描述：</strong>{{ item.risk_desc }}
                </div>
                <div class="risk-advice">
                  <strong>建议话术：</strong>{{ item.advice }}
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="未发现风险项" />
        </el-card>
      </template>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { contract as contractApi } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const contractType = ref('tech_service')
const modifiedText = ref('')
const loading = ref(false)
const result = ref(null)
const expanded = ref({})

function toggleRisk(i) {
  expanded.value[i] = !expanded.value[i]
}

function riskTagType(level) {
  if (level === 'high') return 'danger'
  if (level === 'medium') return 'warning'
  return 'info'
}

function riskLabel(level) {
  if (level === 'high') return '高风险'
  if (level === 'medium') return '中风险'
  if (level === 'low') return '低风险'
  return level
}

async function analyze() {
  if (!modifiedText.value.trim()) {
    ElMessage.warning('请粘贴修改后的合同文本')
    return
  }
  loading.value = true
  try {
    const res = await contractApi.analyze(1, modifiedText.value, contractType.value)
    if (res.code === 0) {
      result.value = res.data

      let diffData = res.data.diff
      if (typeof diffData === 'string') {
        try {
          diffData = JSON.parse(diffData)
        } catch {
          diffData = []
        }
      }
      result.value.diff = diffData

      expanded.value = {}
    } else {
      ElMessage.warning(res.message || '分析失败')
    }
  } catch (err) {
    ElMessage.error(err.message || '请求失败')
  } finally {
    loading.value = false
  }
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
  overflow-y: auto;
}
.input-card {
  margin-bottom: 16px;
}
.result-card {
  margin-bottom: 16px;
}
.diff-view {
  font-size: 14px;
  line-height: 2;
  white-space: pre-wrap;
  word-break: break-word;
}
.diff-span.insert {
  background: #e1f3d8;
  color: #2b7e2b;
  border-radius: 2px;
  padding: 1px 0;
}
.diff-span.delete {
  background: #fde8e8;
  color: #c44;
  border-radius: 2px;
  padding: 1px 0;
  text-decoration: line-through;
}
.risk-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.risk-item {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}
.risk-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
}
.risk-header:hover {
  background: #f9f9f9;
}
.risk-title {
  flex: 1;
  font-size: 14px;
}
.risk-header .el-icon {
  transition: transform 0.2s;
}
.risk-header .el-icon.rotated {
  transform: rotate(180deg);
}
.risk-body {
  padding: 0 16px 12px;
  font-size: 13px;
  line-height: 1.8;
  color: #555;
}
.risk-desc {
  margin-bottom: 8px;
}
</style>
