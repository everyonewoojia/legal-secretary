import http from './index'

export const authApi = {
  login: (phone, password) => http.post('/auth/login', { phone, password }),
  register: (data) => http.post('/auth/register', data),
  smsCode: (phone) => http.post('/auth/sms-code', { phone }),
}

export const userApi = {
  getProfile: () => http.get('/users/me'),
  updateProfile: (data) => http.put('/users/me', data),
  uploadAvatar: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return http.post('/users/me/avatar', fd)
  },
  changePassword: (oldPassword, newPassword) =>
    http.post('/users/me/change-password', { old_password: oldPassword, new_password: newPassword }),
}

export const adminApi = {
  getUsers: (page = 1, pageSize = 20) =>
    http.get('/admin/users', { params: { page, page_size: pageSize } }),
  toggleUserActive: (userId) => http.put(`/admin/users/${userId}/toggle-active`),
  changeUserRole: (userId, role) => http.put(`/admin/users/${userId}/role`, null, { params: { role } }),
  getApiKeys: () => http.get('/admin/api-keys'),
  updateApiKey: (keyId, data) => http.put(`/admin/api-keys/${keyId}`, null, { params: data }),
  getLogs: (params) => http.get('/admin/logs', { params }),
  getStats: () => http.get('/admin/stats'),
}
