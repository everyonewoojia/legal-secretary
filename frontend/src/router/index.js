import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue'), meta: { requiresAuth: true } },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue'), meta: { guest: true } },
  { path: '/draft', name: 'ContractDraft', component: () => import('../views/ContractDraft.vue'), meta: { requiresAuth: true } },
  { path: '/negotiate', name: 'Negotiate', component: () => import('../views/NegotiationAnalyze.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue'), meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: () => import('../views/Admin.vue'), meta: { requiresAuth: true, role: 'admin' } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.guest && userStore.isLoggedIn) {
    next({ path: '/' })
    return
  }

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.role && !userStore.checkPermission(to.meta.role)) {
    ElMessage.warning('无权限访问该页面')
    next(false)
    return
  }

  next()
})

export default router
