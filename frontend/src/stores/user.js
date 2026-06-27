import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  mockLogin,
  mockRegister,
  mockGetUserList,
  mockToggleUserStatus,
  mockChangeUserRole,
  mockUpdateProfile,
  mockChangePassword,
} from '../api/mock/authMock'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)
  const role = computed(() => userInfo.value?.role || '')
  const isAdmin = computed(() => role.value === 'admin')

  function persist() {
    if (token.value && userInfo.value) {
      localStorage.setItem('token', token.value)
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    } else {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  }

  async function login(phone, password) {
    const res = await mockLogin(phone, password)
    if (res.code === 0) {
      token.value = res.data.token
      userInfo.value = res.data.user
      persist()
    }
    return res
  }

  async function register(data) {
    const res = await mockRegister(data)
    return res
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    persist()
  }

  function checkPermission(requiredRole) {
    if (!requiredRole) return true
    if (requiredRole === 'admin') return isAdmin.value
    return isLoggedIn.value
  }

  async function fetchUserList() {
    return await mockGetUserList()
  }

  async function toggleUserStatus(userId) {
    return await mockToggleUserStatus(userId)
  }

  async function changeUserRole(userId, newRole) {
    return await mockChangeUserRole(userId, newRole)
  }

  async function updateProfile(data) {
    const userId = userInfo.value?.id
    if (!userId) return { code: 1, message: '未登录' }
    const res = await mockUpdateProfile(userId, data)
    if (res.code === 0) {
      userInfo.value = res.data.user
      persist()
    }
    return res
  }

  async function changePassword(currentPassword, newPassword) {
    const userId = userInfo.value?.id
    if (!userId) return { code: 1, message: '未登录' }
    return await mockChangePassword(userId, currentPassword, newPassword)
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
