<template>
  <div class="profile-page">
    <aside class="profile-sidebar">
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
        <div
          v-if="store.isAdmin"
          class="nav-item"
          @click="router.push('/admin')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          后台管理
        </div>
        <div class="nav-divider" />
        <div class="nav-item logout" @click="handleLogout">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          退出登录
        </div>
      </nav>
    </aside>

    <main class="profile-content">
      <div v-if="activeTab === 'info'" class="content-panel">
        <h2 class="panel-title">个人信息</h2>

        <div class="avatar-section">
          <div class="avatar-circle">
            <span>{{ store.userInfo?.username?.charAt(0) || '?' }}</span>
          </div>
          <div>
            <el-button size="small" @click="simulateAvatarChange">更换头像</el-button>
            <p class="avatar-hint">支持 JPG/PNG，建议 200x200px</p>
          </div>
        </div>

        <el-form label-width="100px" class="info-form">
          <el-form-item label="用户昵称">
            <el-input v-model="form.username" placeholder="请输入昵称" />
          </el-form-item>
          <el-form-item label="手机号">
            <span class="readonly-field">{{ maskedPhone }}</span>
          </el-form-item>
          <el-form-item label="角色">
            <el-tag :type="store.isAdmin ? 'danger' : 'info'" size="small">
              {{ store.isAdmin ? '管理员' : '普通用户' }}
            </el-tag>
          </el-form-item>
          <el-form-item label="注册时间">
            <span class="readonly-field">{{ store.userInfo?.created_at || '—' }}</span>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="saving"
              :disabled="!form.username?.trim()"
              @click="saveProfile"
            >
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-if="activeTab === 'password'" class="content-panel">
        <h2 class="panel-title">修改密码</h2>

        <el-form label-width="120px" class="info-form">
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
            >
              确认修改
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </main>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const store = useUserStore()

const activeTab = ref('info')

const form = reactive({ username: '' })
const saving = ref(false)

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

onMounted(() => {
  form.username = store.userInfo?.username || ''
})

function simulateAvatarChange() {
  ElMessage.info('头像更换功能（模拟）已触发')
}

async function saveProfile() {
  if (!form.username?.trim()) return
  saving.value = true
  try {
    const res = await store.updateProfile({ username: form.username.trim() })
    if (res.code === 0) {
      ElMessage.success('个人信息已更新')
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
  background: #f0f2f5;
}

.profile-sidebar {
  width: 220px;
  min-width: 220px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  padding-top: 16px;
}

.side-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s;
}

.nav-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

.nav-item.active {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 500;
}

.nav-item.logout {
  color: #f56c6c;
}

.nav-item.logout:hover {
  background: #fef0f0;
}

.nav-divider {
  height: 1px;
  background: #e4e7ed;
  margin: 8px 0;
}

.profile-content {
  flex: 1;
  padding: 32px 40px;
  overflow-y: auto;
}

.content-panel {
  max-width: 600px;
}

.panel-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 24px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f2f5;
}

.avatar-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 600;
  flex-shrink: 0;
}

.avatar-hint {
  font-size: 12px;
  color: #c0c4cc;
  margin: 4px 0 0;
}

.info-form {
  max-width: 440px;
}

.readonly-field {
  font-size: 14px;
  color: #606266;
  line-height: 34px;
}

.info-form :deep(.el-input__wrapper) {
  padding: 4px 12px;
}

.info-form :deep(.el-input__inner) {
  height: 36px;
}
</style>
