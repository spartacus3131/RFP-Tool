import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Quick Scan API
export const quickScan = {
  scan: async (url: string) => {
    const response = await api.post('/api/quick-scan/', { url })
    return response.data
  },
  getSupportedDomains: async () => {
    const response = await api.get('/api/quick-scan/supported-domains')
    return response.data
  },
}

// RFP API
export const rfpApi = {
  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/rfp/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  get: async (id: string) => {
    const response = await api.get(`/api/rfp/${id}`)
    return response.data
  },
  decide: async (id: string, decision: 'go' | 'no_go', notes?: string) => {
    const response = await api.post(`/api/rfp/${id}/decide`, { decision, notes })
    return response.data
  },
}

// Dashboard API
export const dashboardApi = {
  get: async () => {
    const response = await api.get('/api/dashboard/')
    return response.data
  },
  listRfps: async (params?: { status?: string; client?: string }) => {
    const response = await api.get('/api/dashboard/rfps', { params })
    return response.data
  },
}

// Sub-Consultants API
export const subConsultantsApi = {
  list: async (params?: { discipline?: string; tier?: string }) => {
    const response = await api.get('/api/subconsultants/', { params })
    return response.data
  },
  create: async (data: any) => {
    const response = await api.post('/api/subconsultants/', data)
    return response.data
  },
  match: async (disciplines: string[]) => {
    const response = await api.get('/api/subconsultants/match', {
      params: { disciplines: disciplines.join(',') },
    })
    return response.data
  },
}
