<template>
  <div class="login-page">
    <div class="login-card">
      <div class="card-header">
        <h1 class="brand">法务小秘</h1>
        <p class="slogan">AI 智能体合同起草与谈判辅助系统</p>
      </div>
      <el-form @submit.prevent="handleLogin" class="login-form">
        <el-form-item
          :error="errors.phone"
          :class="{ 'is-error': errors.phone }"
        >
          <el-input
            v-model="form.phone"
            placeholder="手机号"
            :prefix-icon="'I-phone'"
            maxlength="11"
            @input="errors.phone = ''"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item :error="errors.password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            show-password
            @input="errors.password = ''"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            </template>
          </el-input>
        </el-form-item>
        <p v-if="errorMsg" class="error-tip">{{ errorMsg }}</p>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          :disabled="!form.phone || !form.password"
          class="submit-btn"
          @click="handleLogin"
        >
          {{ loading ? '登录中…' : '登录' }}
        </el-button>
      </el-form>
      <div class="card-footer">
        <span class="link" @click="router.push('/register')">没有账号？立即注册</span>
      </div>
      <div class="demo-hint">
        <p>演示账号：13800000000 / admin123（管理员）</p>
        <p>演示账号：13800000001 / user123（普通用户）</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useUserStore()

const form = reactive({ phone: '', password: '' })
const errors = reactive({ phone: '', password: '' })
const errorMsg = ref('')
const loading = ref(false)

function validate() {
  let valid = true
  if (!/^1\d{10}$/.test(form.phone)) {
    errors.phone = '请输入正确的11位手机号'
    valid = false
  }
  if (!form.password) {
    errors.password = '请输入密码'
    valid = false
  }
  return valid
}

async function handleLogin() {
  errorMsg.value = ''
  if (!validate()) return
  loading.value = true
  try {
    const res = await store.login(form.phone, form.password)
    if (res.code === 0) {
      ElMessage.success('登录成功')
      router.push('/draft')
    } else {
      errorMsg.value = res.message
    }
  } catch {
    errorMsg.value = '登录请求失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
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

.login-form :deep(.el-input__wrapper) {
  padding: 4px 12px;
}

.login-form :deep(.el-input__inner) {
  height: 42px;
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

.demo-hint {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
}

.demo-hint p {
  font-size: 12px;
  color: #c0c4cc;
  margin: 2px 0;
  text-align: center;
}
</style>
