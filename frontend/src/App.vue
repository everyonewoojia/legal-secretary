<template>
  <div class="app-root">
    <nav v-if="store.isLoggedIn" class="topnav">
      <div class="nav-left">
        <router-link to="/" class="nav-brand">法务小秘</router-link>
        <router-link to="/draft" class="nav-item">合同起草</router-link>
        <router-link to="/negotiate" class="nav-item">谈判分析</router-link>
        <router-link v-if="store.isAdmin" to="/admin" class="nav-item">后台管理</router-link>
      </div>
      <div class="nav-right">
        <el-dropdown trigger="click" @command="handleCommand">
          <span class="nav-user">
            <span v-if="store.userInfo?.avatar" class="user-avatar-img"><img :src="store.userInfo.avatar" /></span>
            <span v-else class="user-avatar">{{ store.userInfo?.username?.charAt(0) || '?' }}</span>
            {{ store.userInfo?.username || '用户' }}
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-left:2px"><polyline points="6 9 12 15 18 9"/></svg>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item v-if="store.isAdmin" command="admin">后台管理</el-dropdown-item>
              <el-dropdown-item divided command="logout" style="color:#f56c6c">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const store = useUserStore()

function handleCommand(command) {
  if (command === 'profile') router.push('/profile')
  else if (command === 'admin') router.push('/admin')
  else if (command === 'logout') handleLogout()
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定退出登录？', '提示')
    store.logout()
    ElMessage.success('已退出')
    router.push('/login')
  } catch {
    /* cancelled */
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
</style>

<style scoped>
.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.topnav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 20px;
  background: #1a1a2e;
  flex-shrink: 0;
  z-index: 100;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-brand {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  text-decoration: none;
  letter-spacing: 1px;
  margin-right: 8px;
}

.nav-item {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: color 0.2s;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: #fff;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.user-avatar-img {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.nav-right :deep(.el-button--text) {
  color: rgba(255, 255, 255, 0.6);
}

.nav-right :deep(.el-button--text:hover) {
  color: #fff;
}
</style>
