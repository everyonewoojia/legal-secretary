<template>
  <div class="profile-page">
    <aside class="profile-sidebar">
      <div class="sidebar-header">个人中心</div>
      <nav class="side-nav">
        <div
          :class="['nav-item', { active: activeTab === 'info' }]"
          @click="activeTab = 'info'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          个人信息
        </div>
        <div
          :class="['nav-item', { active: activeTab === 'password' }]"
          @click="activeTab = 'password'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
          修改密码
        </div>
        <div class="nav-divider" />
        <div class="nav-item logout" @click="handleLogout">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          退出登录
        </div>
      </nav>
    </aside>

    <main class="profile-content">
      <div class="user-hero">
        <div class="hero-avatar">
          <img v-if="pendingAvatarPreview" :src="pendingAvatarPreview" class="hero-avatar-img" />
          <img v-else-if="store.userInfo?.avatar" :src="store.userInfo.avatar" class="hero-avatar-img" />
          <span v-else>{{ store.userInfo?.username?.charAt(0) || '?' }}</span>
        </div>
        <div class="hero-info">
          <h2 class="hero-name">{{ store.userInfo?.username || '用户' }}</h2>
          <p class="hero-phone">{{ maskedPhone }}</p>
          <el-tag :type="store.isAdmin ? 'danger' : ''" size="small" effect="plain">
            {{ store.isAdmin ? '管理员' : '普通用户' }}
          </el-tag>
        </div>
      </div>

      <div v-if="activeTab === 'info'" class="content-card">
        <div class="card-top" />
        <div class="card-body">
          <h3 class="card-title">个人信息</h3>

          <div class="avatar-edit">
            <div class="edit-avatar-circle">
              <img v-if="pendingAvatarPreview" :src="pendingAvatarPreview" class="avatar-img" />
              <img v-else-if="store.userInfo?.avatar" :src="store.userInfo.avatar" class="avatar-img" />
              <span v-else>{{ store.userInfo?.username?.charAt(0) || '?' }}</span>
            </div>
            <el-button size="small" @click="simulateAvatarChange">更换头像</el-button>
          </div>

          <el-form label-position="top" class="profile-form">
            <el-form-item label="用户昵称">
              <el-input v-model="form.username" placeholder="请输入昵称" />
            </el-form-item>
            <el-form-item label="手机号">
              <span class="readonly-field">{{ maskedPhone }}</span>
            </el-form-item>
            <el-form-item label="注册时间">
              <span class="readonly-field">{{ formattedCreatedAt }}</span>
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="saving"
                :disabled="!form.username?.trim()"
                @click="saveProfile"
                class="save-btn"
              >
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <div v-if="activeTab === 'password'" class="content-card">
        <div class="card-top" />
        <div class="card-body">
          <h3 class="card-title">修改密码</h3>

          <el-form label-position="top" class="profile-form">
            <el-form-item label="当前密码" :error="pwErrors.current">
              <el-input
                v-model="pwForm.current"
                type="password"
                show-password
                placeholder="请输入当前密码"
                @input="pwErrors.current = ''"
              />
            </el-form-item>
            <el-form-item label="新密码" :error="pwErrors.newPw">
              <el-input
                v-model="pwForm.newPw"
                type="password"
                show-password
                placeholder="至少6位"
                @input="pwErrors.newPw = ''"
              />
            </el-form-item>
            <el-form-item label="确认新密码" :error="pwErrors.confirm">
              <el-input
                v-model="pwForm.confirm"
                type="password"
                show-password
                placeholder="再次输入新密码"
                @input="pwErrors.confirm = ''"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="pwSaving"
                :disabled="!pwForm.current || !pwForm.newPw || !pwForm.confirm"
                @click="changePassword"
                class="save-btn"
              >
                确认修改
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { userApi } from '../api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const store = useUserStore()

const activeTab = ref('info')

const form = reactive({ username: '' })
const saving = ref(false)
const pendingAvatar = ref(null)
const pendingAvatarPreview = ref('')

const pwForm = reactive({ current: '', newPw: '', confirm: '' })
const pwErrors = reactive({ current: '', newPw: '', confirm: '' })
const pwSaving = ref(false)

const maskedPhone = computed(() => {
  const phone = store.userInfo?.phone || ''
  if (phone.length === 11) {
    return phone.slice(0, 3) + '****' + phone.slice(7)
  }
  return phone
})

const formattedCreatedAt = computed(() => {
  if (!store.userInfo?.created_at) return '—'
  const d = new Date(store.userInfo.created_at)
  if (isNaN(d.getTime())) return store.userInfo.created_at
  return `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()}`
})

onMounted(() => {
  form.username = store.userInfo?.username || ''
})

function simulateAvatarChange() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/png,image/jpeg,image/gif'
  input.onchange = () => {
    const file = input.files?.[0]
    if (!file) return
    pendingAvatar.value = file
    pendingAvatarPreview.value = URL.createObjectURL(file)
  }
  input.click()
}

async function saveProfile() {
  if (!form.username?.trim()) return
  saving.value = true
  try {
    let avatarUrl = ''
    if (pendingAvatar.value) {
      const uploadRes = await userApi.uploadAvatar(pendingAvatar.value)
      if (uploadRes.code === 0) {
        avatarUrl = uploadRes.data?.avatar || ''
        pendingAvatar.value = null
        pendingAvatarPreview.value = ''
      } else {
        ElMessage.warning('头像上传失败')
        return
      }
    }
    const updateData = { username: form.username.trim() }
    if (avatarUrl) updateData.avatar = avatarUrl
    const res = await store.updateProfile(updateData)
    if (res.code === 0) {
      ElMessage.success('头像已更新')
    } else {
      ElMessage.warning(res.message)
    }
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  pwErrors.current = ''
  pwErrors.newPw = ''
  pwErrors.confirm = ''

  let valid = true
  if (!pwForm.current) {
    pwErrors.current = '请输入当前密码'
    valid = false
  }
  if (pwForm.newPw.length < 6) {
    pwErrors.newPw = '新密码至少6位'
    valid = false
  }
  if (pwForm.newPw !== pwForm.confirm) {
    pwErrors.confirm = '两次密码输入不一致'
    valid = false
  }
  if (!valid) return

  pwSaving.value = true
  try {
    const res = await store.changePassword(pwForm.current, pwForm.newPw)
    if (res.code === 0) {
      ElMessage.success('密码修改成功')
      pwForm.current = ''
      pwForm.newPw = ''
      pwForm.confirm = ''
    } else {
      pwErrors.current = res.message
    }
  } catch {
    ElMessage.error('修改密码失败')
  } finally {
    pwSaving.value = false
  }
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定退出登录？', '提示')
    store.logout()
    ElMessage.success('已退出')
    router.push('/login')
  } catch { /* cancelled */ }
}
</script>

<style scoped>
.profile-page {
  flex: 1;
  display: flex;
  background: #F0F5FF;
}

.profile-sidebar {
  width: 200px;
  min-width: 200px;
  background: #fff;
  border-right: 1px solid #E5E7EB;
  padding-top: 0;
}

.sidebar-header {
  font-size: 15px;
  font-weight: 700;
  color: #0F172A;
  padding: 24px 20px 16px;
  letter-spacing: 0.5px;
}

.side-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.15s;
}

.nav-item:hover {
  background: #EFF6FF;
  color: #2563EB;
}

.nav-item.active {
  background: #EFF6FF;
  color: #2563EB;
  font-weight: 600;
}

.nav-item.logout {
  color: #f56c6c;
}

.nav-item.logout:hover {
  background: #FEF2F2;
  color: #EF4444;
}

.nav-divider {
  height: 1px;
  background: #E5E7EB;
  margin: 8px 0;
}

.profile-content {
  flex: 1;
  padding: 32px 40px;
  overflow-y: auto;
}

.user-hero {
  background: linear-gradient(135deg, #2563EB, #7C3AED);
  border-radius: 12px;
  padding: 28px 32px;
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
  color: #fff;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.20);
}

.hero-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 700;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid rgba(255, 255, 255, 0.4);
}

.hero-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hero-name {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.hero-phone {
  font-size: 13px;
  opacity: 0.8;
  margin: 0;
}

.hero-info :deep(.el-tag) {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.content-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  max-width: 520px;
  margin: 0 auto;
}

.card-top {
  height: 4px;
  background: #2563EB;
}

.card-body {
  padding: 28px 32px 32px;
}

.card-title {
  font-size: 17px;
  font-weight: 600;
  color: #0F172A;
  margin: 0 0 24px;
}

.avatar-edit {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #F0F2F5;
}

.edit-avatar-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  font-weight: 600;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-form {
  max-width: 400px;
}

.readonly-field {
  font-size: 14px;
  color: #606266;
  line-height: 36px;
}

.save-btn {
  width: 100%;
  height: 42px;
  margin-top: 4px;
}

.profile-form :deep(.el-input__wrapper) {
  padding: 4px 12px;
  box-shadow: 0 0 0 1px #E2E8F0 inset;
  transition: box-shadow 0.2s;
}

.profile-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #2563EB inset;
}

.profile-form :deep(.el-input__inner) {
  height: 40px;
}

.profile-form :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  padding-bottom: 4px;
}
</style>
