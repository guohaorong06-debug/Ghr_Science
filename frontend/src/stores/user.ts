import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, type UserInfo } from '@/api/auth'

export const useUserStore = defineStore(
  'user',
  () => {
    const token = ref<string>('')
    const userInfo = ref<UserInfo | null>(null)

    const setToken = (newToken: string) => {
      token.value = newToken
    }

    const setUserInfo = (info: UserInfo) => {
      userInfo.value = info
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
    }

    const fetchUserInfo = async () => {
      const data = await authApi.getUserInfo()
      setUserInfo(data)
      return data
    }

    return {
      token,
      userInfo,
      setToken,
      setUserInfo,
      login,
      logout,
      fetchUserInfo,
    }
  },
  {
    persist: true, // 持久化
  }
)
