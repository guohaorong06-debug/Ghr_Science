import request from './request'

export interface Permission {
  id?: number
  permissionCode: string
  permissionName: string
  module: string
  resourceType: 'menu' | 'button' | 'api'
  apiPath?: string
  apiMethod?: string
  parentId?: number
  sortOrder?: number
}

/**
 * 权限管理API
 */
export const permissionApi = {
  /**
   * 获取权限列表
   */
  list() {
    return request.get<Permission[]>('/api/admin/permission/list')
  },

  /**
   * 获取权限树
   */
  tree() {
    return request.get<Permission[]>('/api/admin/permission/tree')
  },

  /**
   * 创建权限
   */
  create(data: Permission) {
    return request.post('/api/admin/permission', data)
  },

  /**
   * 更新权限
   */
  update(data: Permission) {
    return request.put('/api/admin/permission', data)
  },

  /**
   * 删除权限
   */
  delete(id: number) {
    return request.delete(`/api/admin/permission/${id}`)
  },

  /**
   * 获取角色权限列表
   */
  getRolePermissions(roleId: number) {
    return request.get<number[]>(`/api/admin/role/${roleId}/permissions`)
  },

  /**
   * 分配角色权限
   */
  assignRolePermissions(roleId: number, permissionIds: number[]) {
    return request.post(`/api/admin/role/${roleId}/assign-permission`, {
      permissionIds
    })
  }
}
