import request from './request'

export interface LogisticsSite {
  id?: number
  name: string
  longitude: number
  latitude: number
  gridId?: number
  capacity: number
  description?: string
  createTime?: string
  updateTime?: string
}

export const siteApi = {
  page: (params: { current: number; size: number; keyword?: string }) =>
    request.get('/site/page', { params }),

  list: () => request.get<any, LogisticsSite[]>('/site/list'),

  getById: (id: number) => request.get<any, LogisticsSite>(`/site/${id}`),

  add: (data: LogisticsSite) => request.post('/site', data),

  update: (data: LogisticsSite) => request.put('/site', data),

  delete: (id: number) => request.delete(`/site/${id}`),
}
