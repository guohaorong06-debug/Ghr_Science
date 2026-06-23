import request from '@/utils/request'

/**
 * 权限管理API
 */
export const permissionApi = {
  /**
   * 获取权限列表
   */
  list() {
    return request.get('/api/admin/permission/list')
  },

  /**
   * 获取权限树
   */
  tree() {
    return request.get('/api/admin/permission/tree')
  },

  /**
   * 创建权限
   */
  create(data) {
    return request.post('/api/admin/permission', data)
  },

  /**
   * 更新权限
   */
  update(data) {
    return request.put('/api/admin/permission', data)
  },

  /**
   * 删除权限
   */
  delete(id) {
    return request.delete(`/api/admin/permission/${id}`)
  },

  /**
   * 获取角色权限列表
   */
  getRolePermissions(roleId) {
    return request.get(`/api/admin/role/${roleId}/permissions`)
  },

  /**
   * 分配角色权限
   */
  assignRolePermissions(roleId, permissionIds) {
    return request.post(`/api/admin/role/${roleId}/assign-permission`, {
      permissionIds
    })
  }
}
