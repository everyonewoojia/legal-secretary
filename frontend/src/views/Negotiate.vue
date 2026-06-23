<template>
  <el-container style="height:100vh">
    <el-header class="header">
      <span style="font-size:18px;font-weight:600">法务小秘 · 风险审查</span>
      <el-button text @click="router.push('/draft')">合同起草</el-button>
    </el-header>
    <el-main>
      <el-card>
        <el-input v-model="modifiedText" type="textarea" :rows="6" placeholder="粘贴对方修改后的合同文本..." />
        <el-button type="primary" style="margin-top:12px" @click="analyze" :loading="loading">开始分析</el-button>
      </el-card>

      <el-card v-if="riskItems.length" style="margin-top:16px">
        <div style="font-weight:600;margin-bottom:12px">风险分析结果</div>
        <el-tag v-for="(item, i) in riskItems" :key="i"
          :type="item.risk_level === 'high' ? 'danger' : item.risk_level === 'medium' ? 'warning' : 'info'"
          style="margin:4px;cursor:pointer">
          {{ item.clause_title }} · {{ item.risk_level }}
        </el-tag>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { contract } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const modifiedText = ref('')
const riskItems = ref([])
const loading = ref(false)

async function analyze() {
  if (!modifiedText.value) { ElMessage.warning('请粘贴修改文本'); return }
  loading.value = true
  const res = await contract.analyze(1, modifiedText.value, 'tech_service')
  if (res.code === 0) riskItems.value = res.data.risk_items
  loading.value = false
}
</script>

<style scoped>
.header { display: flex; align-items: center; gap: 16px; background: #fff; border-bottom: 1px solid #eee; padding: 0 20px; }
</style>
