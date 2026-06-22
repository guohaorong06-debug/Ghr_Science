import request from './request'

export interface ForecastResult {
  id?: number
  siteId: number
  forecastDate: string
  modelVersion: string
  median: number
  p10: number
  p90: number
  conditionJson?: string
  createTime?: string
}

export interface AlertRecord {
  id: number
  siteId: number
  forecastId: number
  alertDate: string
  alertLevel: string
  overflowRatio: number
  extraCapacity: number
  isRead: boolean
  createTime: string
}

export const forecastApi = {
  predict: (data: { siteId: number; startDate: string; conditions?: any }) =>
    request.post<any, ForecastResult[]>('/forecast/predict', data),

  getResults: (params: { siteId: number; startDate?: string; endDate?: string }) =>
    request.get<any, ForecastResult[]>('/forecast/results', { params }),

  getAlerts: (params?: { siteId?: number; level?: string; isRead?: boolean }) =>
    request.get<any, Array<{ alert: AlertRecord; siteName: string }>>('/forecast/alerts', { params }),

  markRead: (id: number) => request.put(`/forecast/alerts/${id}/read`),
}
