<template>
  <div class="login-page">
    <div class="shield-bg">
      <template v-for="d in decorations" :key="d.id">
        <svg v-if="d.type === 'shield'" class="deco-icon" :style="d.style" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 2L3 7v6c0 5.25 3.83 10 9 12 5.17-2 9-6.75 9-12V7l-9-5z"/>
          <path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else-if="d.type === 'document'" class="deco-icon" :style="d.style" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
          <path d="M14 2v6h6"/>
          <path d="M8 13h8M8 17h8M8 9h1"/>
        </svg>
        <svg v-else class="deco-icon" :style="d.style" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="7"/>
          <path d="M16.5 16.5L21 21" stroke-linecap="round"/>
        </svg>
      </template>
    </div>
    <div class="login-container">
      <BrandPanel />

      <div class="form-panel">
        <div class="form-card-top" />
        <div class="form-inner">
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <div class="title-line" />
            <p class="form-subtitle">登录您的账号</p>
          </div>

          <el-form @submit.prevent="handleLogin" class="login-form">
            <el-form-item :error="errors.phone" :class="{ 'is-error': errors.phone }">
              <el-input
                v-model="form.phone"
                placeholder="手机号"
                maxlength="11"
                @input="errors.phone = ''"
              >
                <template #prefix>
                  <el-icon><Iphone /></el-icon>
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
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <p v-if="errorMsg" class="error-tip">{{ errorMsg }}</p>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              :disabled="!form.phone || !form.password"
              class="submit-btn glow-btn"
              @click="handleLogin"
            >
              {{ loading ? '登录中…' : '登录' }}
            </el-button>
          </el-form>

          <div class="form-footer">
            <span class="link" @click="router.push('/register')">没有账号？<span class="link-highlight">立即注册</span></span>
          </div>

          <div class="demo-section">
            <p class="demo-label">快速体验</p>
            <div class="demo-btns">
              <button class="demo-btn" @click="fillDemo('13800000000', 'admin123')">
                <span class="demo-role admin">管理员</span>
                <span class="demo-phone">13800000000</span>
              </button>
              <button class="demo-btn" @click="fillDemo('13800000001', 'user123')">
                <span class="demo-role user">普通用户</span>
                <span class="demo-phone">13800000001</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { Iphone, Lock } from '@element-plus/icons-vue'
import BrandPanel from '../components/BrandPanel.vue'

const decorations = [
  // 左侧 7 个（松散分布）
  { id: 1, type: 'shield', style: { top: '5%', left: '3%', width: '80px', opacity: '0.10', animationDelay: '0s', animationDuration: '3.5s' } },
  { id: 2, type: 'document', style: { top: '4%', left: '28%', width: '68px', opacity: '0.08', animationDelay: '1.2s', animationDuration: '4s' } },
  { id: 3, type: 'magnifier', style: { top: '30%', left: '1%', width: '88px', opacity: '0.11', animationDelay: '1.8s', animationDuration: '4.2s' } },
  { id: 4, type: 'shield', style: { top: '35%', left: '25%', width: '64px', opacity: '0.07', animationDelay: '0.3s', animationDuration: '3.5s' } },
  { id: 5, type: 'document', style: { bottom: '25%', left: '4%', width: '76px', opacity: '0.09', animationDelay: '2.2s', animationDuration: '4.5s' } },
  { id: 6, type: 'magnifier', style: { bottom: '8%', left: '30%', width: '84px', opacity: '0.10', animationDelay: '1s', animationDuration: '3.6s' } },
  { id: 7, type: 'shield', style: { bottom: '2%', left: '2%', width: '66px', opacity: '0.07', animationDelay: '0.8s', animationDuration: '3.2s' } },
  // 右侧 6 个（均匀松散）
  { id: 8, type: 'shield', style: { top: '6%', right: '4%', width: '76px', opacity: '0.09', animationDelay: '1.5s', animationDuration: '4s' } },
  { id: 9, type: 'document', style: { top: '5%', right: '35%', width: '70px', opacity: '0.08', animationDelay: '0.4s', animationDuration: '3.7s' } },
  { id: 10, type: 'magnifier', style: { top: '35%', right: '2%', width: '82px', opacity: '0.10', animationDelay: '2s', animationDuration: '4.3s' } },
  { id: 11, type: 'shield', style: { top: '38%', right: '32%', width: '68px', opacity: '0.07', animationDelay: '0.7s', animationDuration: '3.4s' } },
  { id: 12, type: 'document', style: { bottom: '10%', right: '3%', width: '86px', opacity: '0.08', animationDelay: '1.6s', animationDuration: '3.3s' } },
  { id: 13, type: 'magnifier', style: { bottom: '12%', right: '36%', width: '72px', opacity: '0.09', animationDelay: '2.5s', animationDuration: '4.8s' } },
]

const router = useRouter()
const route = useRoute()
const store = useUserStore()
import('../views/Home.vue')

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

function fillDemo(phone, password) {
  form.phone = phone
  form.password = password
  errors.phone = ''
  errors.password = ''
  errorMsg.value = ''
}

async function handleLogin() {
  if (loading.value) return
  errorMsg.value = ''
  if (!validate()) return
  loading.value = true
  console.time('login-total')
  try {
    const res = await store.login(form.phone, form.password)
    if (res.code === 0) {
      console.timeEnd('login-total')
      ElMessage.success('登录成功')
      window.location.href = route.query.redirect || '/'
    } else {
      errorMsg.value = res.message
    }
  } catch (e) {
    errorMsg.value = e?.message || '登录请求失败，请重试'
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
  animation: breatheBg 4s ease-in-out infinite;
  position: relative;
}

.shield-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  color: #2563EB;
}

.deco-icon {
  position: absolute;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.login-container {
  display: flex;
  width: 960px;
  max-width: 96vw;
  min-height: 600px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(37, 99, 235, 0.10);
  animation: fadeInUp 0.8s ease, breatheShadow 4s ease-in-out infinite;
}

.form-panel {
  flex: 0 0 45%;
  background: #F8FAFF;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
}

.form-card-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #2563EB;
}

.form-inner {
  width: 100%;
  max-width: 360px;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.title-line {
  width: 32px;
  height: 3px;
  background: #2563EB;
  border-radius: 2px;
  margin: 12px auto 8px;
}

.form-subtitle {
  font-size: 15px;
  color: #94A3B8;
  margin: 0;
}

.login-form :deep(.el-input__wrapper) {
  padding: 4px 12px;
  box-shadow: 0 0 0 1px #E2E8F0 inset;
  transition: box-shadow 0.2s;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #2563EB inset;
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
  font-size: 15px;
  font-weight: 600;
  margin-top: 4px;
}

.glow-btn {
  background: #2563EB;
  border-color: #2563EB;
  transition: all 0.3s;
}

.glow-btn:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
  box-shadow: 0 0 20px rgba(37, 99, 235, 0.4);
  animation: breathe 1.5s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { box-shadow: 0 0 12px rgba(37, 99, 235, 0.3); }
  50% { box-shadow: 0 0 28px rgba(37, 99, 235, 0.55); }
}

.form-footer {
  text-align: center;
  margin-top: 20px;
}

.link {
  font-size: 14px;
  color: #64748B;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.link-highlight {
  color: #2563EB;
  font-weight: 600;
}

.demo-section {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid #E2E8F0;
}

.demo-label {
  font-size: 12px;
  color: #c0c4cc;
  margin: 0 0 10px;
  text-align: center;
}

.demo-btns {
  display: flex;
  gap: 10px;
}

.demo-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 12px;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.demo-btn:hover {
  border-color: #2563EB;
  background: #EFF6FF;
}

.demo-role {
  font-size: 12px;
  font-weight: 600;
  padding: 1px 8px;
  border-radius: 4px;
}

.demo-role.admin {
  color: #f56c6c;
  background: #fef0f0;
}

.demo-role.user {
  color: #409eff;
  background: #ecf5ff;
}

.demo-phone {
  font-size: 11px;
  color: #909399;
  font-family: monospace;
}

@keyframes breatheBg {
  0%, 100% { background: #C7D2FE; }
  50% { background: #FFFFFF; }
}

@keyframes breatheShadow {
  0%, 100% { box-shadow: 0 8px 32px rgba(37, 99, 235, 0.08); }
  50% { box-shadow: 0 12px 48px rgba(37, 99, 235, 0.18); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .form-panel {
    flex: 1;
  }

  .login-container {
    min-height: auto;
    border-radius: 0;
    box-shadow: none;
  }

  .login-page {
    align-items: flex-start;
    padding-top: 48px;
  }
}
</style>
