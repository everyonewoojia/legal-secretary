<template>
  <div class="admin-page">
    <el-header class="header" height="56px">
      <div class="header-left">
        <span class="brand">法务小秘 · 后台管理</span>
      </div>
      <div class="header-nav">
        <el-button text @click="router.push('/')">首页</el-button>
        <el-button text @click="router.push('/draft')">合同起草</el-button>
      </div>
    </el-header>

    <div class="admin-body">
      <div class="toolbar">
        <h3 class="section-title">用户管理</h3>
        <el-tag type="info" size="small">{{ userList.length }} 个用户</el-tag>
      </div>

      <el-table :data="userList" style="width:100%" v-loading="loading">
        <el-table-column label="头像" width="60">
          <template #default>
            <div class="avatar-placeholder">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="120" />
        <el-table-column label="操作" min-width="180">
          <template #default="{ row }">
            <el-button
              size="small"
              :type="row.status === 'active' ? 'warning' : 'success'"
              :disabled="row.id === currentUserId"
              @click="toggleStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button
              size="small"
              :disabled="row.id === currentUserId"
              @click="changeRole(row)"
            >
              设为{{ row.role === 'admin' ? '普通用户' : '管理员' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const store = useUserStore()
const userList = ref([])
const loading = ref(false)
const currentUserId = ref(store.userInfo?.id)

async function loadUsers() {
  loading.value = true
  try {
    userList.value = await store.fetchUserList()
  } catch {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

async function toggleStatus(row) {
  try {
    await ElMessageBox.confirm(
      `确定${row.status === 'active' ? '禁用' : '启用'}用户「${row.username}」？`,
      '操作确认',
    )
    const res = await store.toggleUserStatus(row.id)
    if (res.code === 0) {
      ElMessage.success('操作成功')
      await loadUsers()
    } else {
      ElMessage.warning(res.message)
    }
  } catch {
    /* cancelled */
  }
}

async function changeRole(row) {
  const newRole = row.role === 'admin' ? 'user' : 'admin'
  const label = newRole === 'admin' ? '管理员' : '普通用户'
  try {
    await ElMessageBox.confirm(
      `确定将用户「${row.username}」的角色改为「${label}」？`,
      '操作确认',
    )
    const res = await store.changeUserRole(row.id, newRole)
    if (res.code === 0) {
      ElMessage.success('角色已更新')
      await loadUsers()
    } else {
      ElMessage.warning(res.message)
    }
  } catch {
    /* cancelled */
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.admin-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
}

.header-nav {
  display: flex;
  gap: 4px;
}

.admin-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.avatar-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
