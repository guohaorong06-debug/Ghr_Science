import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type UserInfo } from '@/api/auth'

export const useUserStore = defineStore(
  'user',
  () => {
    const token = ref<string>('')
    const userInfo = ref<UserInfo | null>(null)
    const permissions = ref<string[]>([])
    const roles = ref<string[]>([])

    const setToken = (newToken: string) => {
      token.value = newToken
    }

    const setUserInfo = (info: UserInfo) => {
      userInfo.value = info
      // 从后端返回的用户信息中提取权限和角色
      if (info.permissions) {
        permissions.value = info.permissions
      }
      if (info.roles) {
        roles.value = info.roles
      }
    }

    const login = async (username: string, password: string) => {
      const data = await authApi.login({ username, password })
      setToken(data.token!)
      setUserInfo(data)
      return data
    }

    const logout = () => {
      token.value = ''
      userInfo.value = null
      permissions.value = []
      roles.value = []
    }

    const fetchUserInfo = async () => {
      const data = await authApi.getUserInfo()
      setUserInfo(data)
      return data
    }

    // 检查是否有指定权限
    const hasPermission = (permissionCode: string) => {
      if (!permissionCode) return true
      return permissions.value.includes(permissionCode)
    }

    // 检查是否有任一权限
    const hasAnyPermission = (permissionCodes: string[]) => {
      return permissionCodes.some(code => permissions.value.includes(code))
    }

    // 检查是否有所有权限
    const hasAllPermissions = (permissionCodes: string[]) => {
      return permissionCodes.every(code => permissions.value.includes(code))
    }

    // 检查是否有指定角色
    const hasRole = (roleCode: string) => {
      return roles.value.includes(roleCode)
    }

    // 是否是管理员
    const isAdmin = computed(() => hasRole('ADMIN'))

    // 是否是运营员
    const isOperator = computed(() => hasRole('OPERATOR'))

    // 是否是游客
    const isGuest = computed(() => hasRole('GUEST'))

    return {
      token,
      userInfo,
      permissions,
      roles,
      isAdmin,
      isOperator,
      isGuest,
      setToken,
      setUserInfo,
      login,
      logout,
      fetchUserInfo,
      hasPermission,
      hasAnyPermission,
      hasAllPermissions,
      hasRole,
    }
  },
  {
    persist: true, // 持久化
  }
)
