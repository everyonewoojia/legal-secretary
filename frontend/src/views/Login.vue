<template>
  <el-container class="login-container">
    <el-card class="login-card">
      <h2>法务小秘</h2>
      <p class="subtitle">AI智能体合同起草与谈判辅助系统</p>
      <el-form @submit.prevent="handleLogin">
        <el-input v-model="phone" placeholder="手机号" :prefix-icon="'Phone'" />
        <el-input v-model="password" type="password" placeholder="密码" show-password style="margin-top:16px" />
        <el-button type="primary" style="width:100%;margin-top:24px" @click="handleLogin">登录</el-button>
      </el-form>
      <div style="margin-top:16px;text-align:center;font-size:13px;color:#999">实训Demo · 仅供学习参考</div>
    </el-card>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { auth } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useUserStore()
const phone = ref('')
const password = ref('')

async function handleLogin() {
  const res = await auth.login(phone.value, password.value)
  if (res.code === 0) {
    store.setLogin(res.data.token, res.data.user)
    ElMessage.success('登录成功')
    router.push('/draft')
  } else {
    ElMessage.error(res.message)
  }
}
</script>

<style scoped>
.login-container { height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5; }
.login-card { width: 400px; }
.login-card h2 { text-align: center; margin-bottom: 4px; }
.subtitle { text-align: center; color: #999; font-size: 13px; margin-bottom: 24px; }
</style>
