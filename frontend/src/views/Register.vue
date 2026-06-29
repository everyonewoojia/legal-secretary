<template>
  <div class="register-page">
    <div class="register-card">
      <div class="card-header">
        <h1 class="brand">法务小秘</h1>
        <p class="slogan">创建账号，开始智能合同管理</p>
      </div>
      <el-form @submit.prevent="handleRegister" class="register-form">
        <el-form-item :error="errors.phone">
          <el-input
            v-model="form.phone"
            placeholder="手机号"
            maxlength="11"
            @input="errors.phone = ''"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item :error="errors.username">
          <el-input
            v-model="form.username"
            placeholder="用户名（选填）"
            @input="errors.username = ''"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item :error="errors.password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码（至少6位）"
            show-password
            @input="errors.password = ''"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item :error="errors.confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            show-password
            @input="errors.confirmPassword = ''"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item :error="errors.code" class="code-row">
          <el-input
            v-model="form.code"
            placeholder="验证码"
            maxlength="6"
            class="code-input"
            @input="errors.code = ''"
          />
          <el-button
            class="code-btn"
            :disabled="codeCountdown > 0"
            @click="sendCode"
          >
            {{ codeCountdown > 0 ? `${codeCountdown}s` : '获取验证码' }}
          </el-button>
        </el-form-item>
        <p v-if="errorMsg" class="error-tip">{{ errorMsg }}</p>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          :disabled="!form.phone || !form.password || !form.confirmPassword || !form.code"
          class="submit-btn"
          @click="handleRegister"
        >
          {{ loading ? '注册中…' : '注册' }}
        </el-button>
      </el-form>
      <div class="card-footer">
        <span class="link" @click="router.push('/login')">已有账号？去登录</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useUserStore()

const form = reactive({
  phone: '',
  username: '',
  password: '',
  confirmPassword: '',
  code: '',
})

const errors = reactive({
  phone: '',
  username: '',
  password: '',
  confirmPassword: '',
  code: '',
})

const errorMsg = ref('')
const loading = ref(false)
const codeCountdown = ref(0)
let timer = null

function validate() {
  let valid = true
  if (!/^1\d{10}$/.test(form.phone)) {
    errors.phone = '请输入正确的11位手机号'
    valid = false
  }
  if (form.password.length < 6) {
    errors.password = '密码至少6位'
    valid = false
  }
  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = '两次密码输入不一致'
    valid = false
  }
  if (!form.code) {
    errors.code = '请输入验证码'
    valid = false
  }
  return valid
}

function sendCode() {
  if (!/^1\d{10}$/.test(form.phone)) {
    errors.phone = '请先输入正确的手机号'
    return
  }
  codeCountdown.value = 60
  ElMessage.info('模拟验证码：123456')
  timer = setInterval(() => {
    codeCountdown.value--
    if (codeCountdown.value <= 0) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

async function handleRegister() {
  errorMsg.value = ''
  if (!validate()) return
  loading.value = true
  try {
    const res = await store.register({
      phone: form.phone,
      password: form.password,
      username: form.username || undefined,
    })
    if (res.code === 0) {
      ElMessage.success('注册成功')
      router.push('/')
    } else {
      errorMsg.value = res.message
    }
  } catch {
    errorMsg.value = '注册请求失败，请重试'
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 400px;
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.card-header {
  text-align: center;
  margin-bottom: 28px;
}

.brand {
  font-size: 28px;
  font-weight: 800;
  color: #1a1a2e;
  margin: 0 0 6px;
  letter-spacing: 2px;
}

.slogan {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.register-form :deep(.el-input__wrapper) {
  padding: 4px 12px;
}

.register-form :deep(.el-input__inner) {
  height: 42px;
}

.code-row {
  display: flex;
  gap: 8px;
}

.code-input {
  flex: 1;
}

.code-btn {
  width: 120px;
  flex-shrink: 0;
}

.error-tip {
  color: #f56c6c;
  font-size: 13px;
  margin: -8px 0 12px;
  text-align: center;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  margin-top: 4px;
}

.card-footer {
  text-align: center;
  margin-top: 20px;
}

.link {
  font-size: 13px;
  color: #409eff;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}
</style>
