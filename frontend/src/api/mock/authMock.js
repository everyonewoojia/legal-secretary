const STORAGE_KEY = 'mock_users'

const defaultUsers = [
  {
    id: 1,
    phone: '13800000000',
    password: 'admin123',
    username: '管理员',
    role: 'admin',
    status: 'active',
    created_at: '2025-01-01',
  },
  {
    id: 2,
    phone: '13800000001',
    password: 'user123',
    username: '普通用户',
    role: 'user',
    status: 'active',
    created_at: '2025-01-15',
  },
]

function getUsers() {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultUsers))
    return [...defaultUsers]
  }
  try {
    return JSON.parse(raw)
  } catch {
    return [...defaultUsers]
  }
}

function saveUsers(users) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users))
}

function delay(ms = 600) {
  return new Promise((r) => setTimeout(r, ms))
}

export async function mockLogin(phone, password) {
  await delay()
  const users = getUsers()
  const user = users.find((u) => u.phone === phone)
  if (!user) {
    return { code: 1, message: '账号不存在，请检查手机号' }
  }
  if (user.password !== password) {
    return { code: 1, message: '密码错误，请重试' }
  }
  if (user.status !== 'active') {
    return { code: 1, message: '账号已被禁用，请联系管理员' }
  }
  const token = 'mock_token_' + user.id + '_' + Date.now()
  const { password: _, ...safeUser } = user
  return {
    code: 0,
    message: 'success',
    data: { token, user: safeUser },
  }
}

export async function mockRegister({ phone, password, username }) {
  await delay()
  const users = getUsers()
  if (users.find((u) => u.phone === phone)) {
    return { code: 1, message: '该手机号已注册，请直接登录' }
  }
  const newUser = {
    id: users.length > 0 ? Math.max(...users.map((u) => u.id)) + 1 : 1,
    phone,
    password,
    username: username || '用户' + phone.slice(-4),
    role: 'user',
    status: 'active',
    created_at: new Date().toISOString().slice(0, 10),
  }
  users.push(newUser)
  saveUsers(users)
  return { code: 0, message: '注册成功' }
}

export async function mockGetUserList() {
  await delay(400)
  const users = getUsers()
  return users.map(({ password, ...u }) => u)
}

export async function mockToggleUserStatus(userId) {
  await delay(300)
  const users = getUsers()
  const idx = users.findIndex((u) => u.id === userId)
  if (idx === -1) return { code: 1, message: '用户不存在' }
  users[idx].status = users[idx].status === 'active' ? 'disabled' : 'active'
  saveUsers(users)
  return { code: 0, message: '操作成功' }
}

export async function mockChangeUserRole(userId, newRole) {
  await delay(300)
  const users = getUsers()
  const idx = users.findIndex((u) => u.id === userId)
  if (idx === -1) return { code: 1, message: '用户不存在' }
  users[idx].role = newRole
  saveUsers(users)
  return { code: 0, message: '角色已更新' }
}

export async function mockUpdateProfile(userId, data) {
  await delay(500)
  const users = getUsers()
  const idx = users.findIndex((u) => u.id === userId)
  if (idx === -1) return { code: 1, message: '用户不存在' }
  if (data.username) users[idx].username = data.username
  if (data.avatar) users[idx].avatar = data.avatar
  saveUsers(users)
  const { password, ...safeUser } = users[idx]
  return { code: 0, message: 'success', data: { user: safeUser } }
}

export async function mockChangePassword(userId, currentPassword, newPassword) {
  await delay(500)
  const users = getUsers()
  const idx = users.findIndex((u) => u.id === userId)
  if (idx === -1) return { code: 1, message: '用户不存在' }
  if (users[idx].password !== currentPassword) {
    return { code: 1, message: '当前密码不正确' }
  }
  users[idx].password = newPassword
  saveUsers(users)
  return { code: 0, message: '密码修改成功' }
}
