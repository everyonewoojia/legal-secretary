import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi, adminApi } from '../api/auth'
import { useContractStore } from './contract'
import { useNegotiationStore } from './negotiation'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)
  const role = computed(() => userInfo.value?.role || '')
  const isAdmin = computed(() => role.value === 'admin')

  function persist() {
    if (token.value) {
      localStorage.setItem('token', token.value)
    } else {
      localStorage.removeItem('token')
    }
    if (userInfo.value) {
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    } else {
      localStorage.removeItem('userInfo')
    }
  }

  function normalizeUser(data) {
    return { ...data, username: data.nickname || data.phone }
  }

  async function login(phone, password) {
    const res = await authApi.login(phone, password)
    if (res.code === 0) {
      token.value = res.data.access_token
      persist()
      const profileRes = await userApi.getProfile()
      if (profileRes.code === 0) {
        userInfo.value = normalizeUser(profileRes.data)
        persist()
      }
    }
    return res
  }

  async function register(data) {
    const res = await authApi.register(data)
    if (res.code === 0) {
      token.value = res.data.token.access_token
      persist()
      const profileRes = await userApi.getProfile()
      if (profileRes.code === 0) {
        userInfo.value = normalizeUser(profileRes.data)
        persist()
      }
    }
    return res
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    persist()
    useContractStore().clearSession()
    useNegotiationStore().resetAnalysis()
  }

  function checkPermission(requiredRole) {
    if (!requiredRole) return true
    if (requiredRole === 'admin') return isAdmin.value
    return isLoggedIn.value
  }

  async function fetchUserList(page = 1, pageSize = 20) {
    const res = await adminApi.getUsers(page, pageSize)
    if (res.code === 0) {
      return {
        items: res.data.items.map((u) => ({
          id: u.id,
          phone: u.phone,
          username: u.nickname || u.phone,
          nickname: u.nickname,
          role: u.role,
          status: u.is_active ? 'active' : 'disabled',
          is_active: u.is_active,
          created_at: u.created_at,
        })),
        total: res.data.total || 0,
      }
    }
    return { items: [], total: 0 }
  }

  async function toggleUserStatus(userId) {
    return await adminApi.toggleUserActive(userId)
  }

  async function changeUserRole(userId, newRole) {
    return await adminApi.changeUserRole(userId, newRole)
  }

  async function updateProfile(data) {
    const payload = { ...data }
    if (payload.username !== undefined) {
      payload.nickname = payload.username
      delete payload.username
    }
    const res = await userApi.updateProfile(payload)
    if (res.code === 0) {
      userInfo.value = normalizeUser(res.data)
      persist()
    }
    return res
  }

  async function changePassword(currentPassword, newPassword) {
    try {
      return await userApi.changePassword(currentPassword, newPassword)
    } catch (e) {
      return { code: 1, message: e.message || '修改密码失败' }
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    role,
    isAdmin,
    login,
    register,
    logout,
    checkPermission,
    fetchUserList,
    toggleUserStatus,
    changeUserRole,
    updateProfile,
    changePassword,
  }
})
