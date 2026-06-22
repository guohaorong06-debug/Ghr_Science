import request from './request'

export interface ModelVersion {
  id?: number
  version: string
  filePath: string
  fileSize: number
  isActive: boolean
  metricsJson?: string
  description?: string
  createTime?: string
  updateTime?: string
}

export const modelApi = {
  list: () => request.get<any, ModelVersion[]>('/model/list'),

  getActive: () => request.get<any, ModelVersion>('/model/active'),

  upload: (file: File, version: string, description?: string, metricsJson?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('version', version)
    if (description) formData.append('description', description)
    if (metricsJson) formData.append('metricsJson', metricsJson)
    return request.post<any, ModelVersion>('/model/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  activate: (id: number) => request.put(`/model/${id}/activate`),

  delete: (id: number) => request.delete(`/model/${id}`),
}
