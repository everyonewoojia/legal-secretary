<template>
  <el-container style="height:100vh">
    <el-header class="header">
      <span style="font-size:18px;font-weight:600">法务小秘 · 后台管理</span>
      <el-button text @click="router.push('/draft')">返回起草</el-button>
    </el-header>
    <el-main>
      <el-tabs>
        <el-tab-pane label="用户审核">
          <el-empty description="暂无待审核用户" />
        </el-tab-pane>
        <el-tab-pane label="API配置">
          <el-form label-width="120px">
            <el-form-item label="服务商">
              <el-select v-model="provider">
                <el-option label="通义千问" value="openai" />
                <el-option label="智谱GLM" value="glm" />
              </el-select>
            </el-form-item>
            <el-form-item label="API Key">
              <el-input v-model="apiKey" type="password" show-password />
            </el-form-item>
            <el-button type="primary">保存配置</el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="系统日志">
          <el-empty description="暂无日志数据" />
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const provider = ref('openai')
const apiKey = ref('')
</script>

<style scoped>
.header { display: flex; align-items: center; gap: 16px; background: #fff; border-bottom: 1px solid #eee; padding: 0 20px; }
</style>
