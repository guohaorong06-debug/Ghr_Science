import request from './request'

export interface DemandRecord {
  id?: number
  siteId: number
  recordDate: string
  volume: number
  isHoliday?: boolean
  weather?: string
  temperature?: number
  precipitation?: number
  windSpeed?: number
  createTime?: string
}

export const dataApi = {
  preview: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<any, DemandRecord[]>('/data/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  import: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<any, string>('/data/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  records: (params: {
    current: number
    size: number
    siteId?: number
    startDate?: string
    endDate?: string
  }) => request.get('/data/records', { params }),
}
