import request from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams extends LoginParams {
  realName?: string
  email?: string
  phone?: string
}

export interface UserInfo {
  id: number
  username: string
  realName?: string
  role: string
  email?: string
  phone?: string
  token?: string
}

export const authApi = {
  login: (data: LoginParams) => request.post<any, UserInfo>('/auth/login', data),
  register: (data: RegisterParams) => request.post('/auth/register', data),
  getUserInfo: () => request.get<any, UserInfo>('/auth/info'),
}
