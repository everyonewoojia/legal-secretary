import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/draft', name: 'ContractDraft', component: () => import('../views/ContractDraft.vue') },
  { path: '/negotiate', name: 'Negotiate', component: () => import('../views/Negotiate.vue') },
  { path: '/admin', name: 'Admin', component: () => import('../views/Admin.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
