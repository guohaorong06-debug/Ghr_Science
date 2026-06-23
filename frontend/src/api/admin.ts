import request from './request'

/**
 * 用户管理API
 */
export const userAPI = {
  // 获取用户列表
  getUserList(params: any) {
    return request.get('/api/admin/user/list', { params })
  },

  // 创建用户
  createUser(data: any) {
    return request.post('/api/admin/user', data)
  },

  // 更新用户
  updateUser(id: number, data: any) {
    return request.put('/api/admin/user', data)
  },

  // 删除用户
  deleteUser(id: number) {
    return request.delete(`/api/admin/user/${id}`)
  },

  // 分配角色
  assignRole(userId: number, roleId: number) {
    return request.post('/api/admin/user/assign-role', { userId, roleId })
  },

  // 切换用户状态
  toggleStatus(id: number) {
    return request.put(`/api/admin/user/${id}/toggle-status`)
  }
}

/**
 * 角色管理API
 */
export const roleAPI = {
  // 获取角色列表
  getRoleList(params?: any) {
    return request.get('/api/admin/role/list', { params })
  },

  // 创建角色
  createRole(data: any) {
    return request.post('/api/admin/role', data)
  },

  // 更新角色
  updateRole(id: number, data: any) {
    return request.put('/api/admin/role', data)
  },

  // 删除角色
  deleteRole(id: number) {
    return request.delete(`/api/admin/role/${id}`)
  },

  // 配置权限
  configPermissions(roleId: number, permissionIds: number[]) {
    return request.post('/api/admin/role/config-permissions', { roleId, permissionIds })
  },

  // 查看角色用户
  getRoleUsers(roleId: number) {
    return request.get(`/api/admin/role/${roleId}/users`)
  }
}

/**
 * 权限管理API
 */
export const permissionAPI = {
  // 获取权限列表
  getPermissionList() {
    return request.get('/api/admin/permission/list')
  },

  // 获取权限树
  getPermissionTree() {
    return request.get('/api/admin/permission/tree')
  },

  // 获取角色权限
  getRolePermissions(roleId: number) {
    return request.get(`/api/admin/permission/role/${roleId}`)
  }
}
