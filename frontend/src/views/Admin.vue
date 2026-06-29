<template>
  <div class="admin-page">
    <AppHeader tag="后台管理" tag-type="danger">
      <el-button text @click="router.push('/')">首页</el-button>
      <el-button text @click="router.push('/draft')">合同起草</el-button>
    </AppHeader>

    <div class="admin-body">
      <div class="toolbar">
        <h3 class="section-title">用户管理</h3>
        <el-tag type="info" size="small">{{ userList.length }} 个用户</el-tag>
      </div>

      <el-table :data="userList" style="width:100%" v-loading="loading">
        <el-table-column label="头像" width="60">
          <template #default>
            <div class="avatar-placeholder">
              <el-icon :size="20" color="#fff"><User /></el-icon>
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

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadUsers"
          @size-change="loadUsers"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import AppHeader from '../components/AppHeader.vue'

const router = useRouter()
const store = useUserStore()
const userList = ref([])
const loading = ref(false)
const currentUserId = ref(store.userInfo?.id)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function loadUsers() {
  loading.value = true
  try {
    const result = await store.fetchUserList(page.value, pageSize.value)
    userList.value = result.items
    total.value = result.total
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

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
